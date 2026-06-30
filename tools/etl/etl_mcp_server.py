"""
etl_mcp_server.py — Eduboost ETL MCP Server
============================================
Exposes the ETL pipeline as MCP tools so Claude (or any MCP client) can
drive the full document lifecycle: ingest, validate, review, report.

Tools
-----
  etl_ingest_document     — Phase 1: acquire & register a document
  etl_get_document        — Fetch a document record by ID
  etl_list_documents      — Filter/search the document registry
  etl_run_pipeline        — Run all ETL phases on a document
  etl_run_stage           — Run one pipeline stage (extract/normalize/chunk/validate)
  etl_approve_document    — Mark a document as approved for production
  etl_reject_document     — Reject a document with reason
  etl_reprocess_document  — Reset and re-run pipeline
  etl_get_review_queue    — List all pending human-review tasks
  etl_get_pipeline_stats  — Aggregated pipeline health metrics
  etl_get_content_gaps    — Show missing content by grade/subject/doc-type
  etl_get_quality_report  — Detailed quality check for one document

Setup
-----
    pip install mcp[cli] fastmcp

Run (stdio — for Claude Desktop / MCP Inspector):
    python etl_mcp_server.py

Run (HTTP — for remote clients):
    python etl_mcp_server.py --transport streamable-http --port 8765
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Optional

# FastMCP is part of the official Python MCP SDK
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field, ConfigDict

# Bring in the pipeline
sys.path.insert(0, str(Path(__file__).parent))
from app.services.etl.etl_pipeline import (
    EduboostETL, IngestRequest,
    DocumentType, SourceType, LicenseStatus, ProcessingStatus,
)

# ---------------------------------------------------------------------------
# Server init — reads config from env vars so the same server file works in
# all environments (dev, CI, production).
# ---------------------------------------------------------------------------

ETL_DB_URL     = os.getenv("ETL_DB_URL",      "sqlite:///eduboost_etl.db")
ETL_STORAGE    = os.getenv("ETL_STORAGE_ROOT", "./data")

mcp = FastMCP("eduboost_etl_mcp", json_response=True)
_pipeline: Optional[EduboostETL] = None


def pipeline() -> EduboostETL:
    """Lazy singleton — initialised on first tool call."""
    global _pipeline
    if _pipeline is None:
        _pipeline = EduboostETL(db_url=ETL_DB_URL, storage_root=ETL_STORAGE)
        _pipeline.init_db()
    return _pipeline


def _run_streamable_http_app(mcp_server, host: str, port: int) -> None:
    """Run a browser-friendly Streamable HTTP app using uvicorn."""
    import uvicorn
    from starlette.responses import JSONResponse

    class _BrowserFriendlyStreamableHTTPMiddleware:
        def __init__(self, app):
            self.app = app

        async def __call__(self, scope, receive, send):
            if (
                scope.get("type") == "http"
                and scope.get("method") == "GET"
                and scope.get("path") == getattr(mcp_server.settings, "streamable_http_path", "/mcp")
            ):
                accept = ""
                for key, value in scope.get("headers", []):
                    if key == b"accept":
                        accept = value.decode("latin-1")
                        break
                if "text/event-stream" not in accept and "application/json" not in accept:
                    response = JSONResponse(
                        {
                            "jsonrpc": "2.0",
                            "id": "server-error",
                            "error": {
                                "code": -32000,
                                "message": "MCP endpoint. Use an MCP client or POST /mcp with MCP headers.",
                            },
                        },
                        status_code=200,
                    )
                    await response(scope, receive, send)
                    return
            await self.app(scope, receive, send)

    app = _BrowserFriendlyStreamableHTTPMiddleware(mcp_server.streamable_http_app())
    uvicorn.run(app, host=host, port=port, log_level=mcp_server.settings.log_level.lower())


def _start_mcp_server(mcp_server, transport: str, host: str, port: int) -> None:
    """Start the MCP server across supported FastMCP SDK versions."""
    if transport == "streamable-http":
        try:
            mcp_server.run(transport="streamable-http", host=host, port=port)
        except TypeError as exc:
            if "unexpected keyword argument 'host'" not in str(exc) and "unexpected keyword argument 'port'" not in str(exc):
                raise
            mcp_server.settings.host = host
            mcp_server.settings.port = port
            _run_streamable_http_app(mcp_server, host=host, port=port)
            return
    else:
        mcp_server.run(transport=transport)


# ===========================================================================
# INPUT MODELS  (Pydantic — auto-generate JSON Schema for MCP)
# ===========================================================================

class IngestDocumentInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    file_path: str = Field(
        ...,
        description="Absolute or relative path to the document file on disk "
                    "(PDF, DOCX, TXT, MD, HTML, CSV, XLSX). "
                    "Example: '/uploads/grade4_maths_textbook.pdf'"
    )
    document_type: str = Field(
        default=DocumentType.unknown,
        description=(
            "Content category. One of: " +
            ", ".join(t.value for t in DocumentType)
        )
    )
    source_type: str = Field(
        default=SourceType.manual_upload,
        description=(
            "Origin of the file. One of: " +
            ", ".join(t.value for t in SourceType)
        )
    )
    uploaded_by: str = Field(default="system", description="User or service uploading the file.")
    grade: Optional[int] = Field(default=None, ge=1, le=12, description="Target school grade (1–12).")
    subject: Optional[str] = Field(default=None, description="Subject area, e.g. 'mathematics', 'english'.")
    language: str = Field(default="en", description="ISO 639-1 language code, e.g. 'en', 'af', 'zu'.")
    license_status: str = Field(
        default=LicenseStatus.unknown,
        description=(
            "Rights status. One of: " +
            ", ".join(t.value for t in LicenseStatus)
        )
    )
    source_url: Optional[str] = Field(default=None, description="Original URL if downloaded from the web.")
    title: Optional[str] = Field(default=None, description="Override auto-inferred title.")
    notes: str = Field(default="", description="Free-text notes for the content team.")


class GetDocumentInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    document_id: str = Field(..., description="UUID of the document to fetch.")


class ListDocumentsInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: Optional[str] = Field(
        default=None,
        description=(
            "Filter by processing status. One of: " +
            ", ".join(s.value for s in ProcessingStatus)
        )
    )
    grade: Optional[int] = Field(default=None, ge=1, le=12, description="Filter by grade.")
    subject: Optional[str] = Field(default=None, description="Filter by subject.")
    document_type: Optional[str] = Field(default=None, description="Filter by document type.")
    limit: int = Field(default=50, ge=1, le=500, description="Max rows to return.")


class RunPipelineInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    document_id: str = Field(..., description="UUID of the document to process.")


class RunStageInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    document_id: str = Field(..., description="UUID of the document to process.")
    stage: str = Field(
        ...,
        description="Pipeline stage to run. One of: extract, normalize, chunk, validate"
    )


class ApproveDocumentInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    document_id: str = Field(..., description="UUID of the document to approve.")
    reviewer: str = Field(..., description="Name or user ID of the reviewer.")
    notes: str = Field(default="", description="Optional reviewer notes.")


class RejectDocumentInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    document_id: str = Field(..., description="UUID of the document to reject.")
    reviewer: str = Field(..., description="Name or user ID of the reviewer.")
    reason: str = Field(..., description="Machine-readable rejection reason.")


class ReprocessDocumentInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    document_id: str = Field(..., description="UUID of the document to reprocess.")


class GetQualityReportInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    document_id: str = Field(..., description="UUID of the document.")


# ===========================================================================
# TOOLS
# ===========================================================================

@mcp.tool(
    name="etl_ingest_document",
    annotations={
        "title": "Ingest Document",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    }
)
async def etl_ingest_document(params: IngestDocumentInput) -> str:
    """
    Phase 1 — Acquire a document file and register it in the Eduboost ETL pipeline.

    Performs:
    - SHA-256 duplicate detection (rejects exact duplicates)
    - Copies the raw file to immutable storage
    - Registers the document source
    - Creates the canonical document record with 'acquired' status

    Returns the document_id and provenance metadata. Use the returned
    document_id with etl_run_pipeline to process the document.
    """
    try:
        doc = pipeline().ingest(IngestRequest(
            file_path=params.file_path,
            source_type=params.source_type,
            uploaded_by=params.uploaded_by,
            document_type=params.document_type,
            source_url=params.source_url,
            license_status=params.license_status,
            grade=params.grade,
            subject=params.subject,
            language=params.language,
            title=params.title,
            notes=params.notes,
        ))
        return json.dumps({
            "success": True,
            "document_id": doc.document_id,
            "title": doc.title,
            "document_type": doc.document_type,
            "processing_status": doc.processing_status,
            "checksum": doc.checksum[:16] + "…",
            "file_size_bytes": doc.file_size_bytes,
            "next_step": f"Call etl_run_pipeline with document_id='{doc.document_id}' to process.",
        }, indent=2)
    except ValueError as e:
        return json.dumps({"success": False, "error": str(e)}, indent=2)
    except FileNotFoundError as e:
        return json.dumps({"success": False, "error": str(e)}, indent=2)


@mcp.tool(
    name="etl_get_document",
    annotations={
        "title": "Get Document",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    }
)
async def etl_get_document(params: GetDocumentInput) -> str:
    """
    Fetch full metadata for a single document by its UUID.

    Returns all metadata fields including processing_status, quality_score,
    grade, subject, document_type, license_status, and reviewer information.
    """
    try:
        doc = pipeline()._load_document(params.document_id)
        import dataclasses
        return json.dumps(dataclasses.asdict(doc), indent=2)
    except ValueError as e:
        return json.dumps({"error": str(e)}, indent=2)


@mcp.tool(
    name="etl_list_documents",
    annotations={
        "title": "List Documents",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    }
)
async def etl_list_documents(params: ListDocumentsInput) -> str:
    """
    List documents in the registry with optional filters.

    Filter by processing_status, grade, subject, or document_type.
    Returns up to `limit` records sorted by creation date descending.

    Useful for:
    - Auditing what content exists
    - Finding documents in a specific stage
    - Identifying content by grade and subject
    """
    docs = pipeline().list_documents(
        status=params.status,
        grade=params.grade,
        subject=params.subject,
        document_type=params.document_type,
        limit=params.limit,
    )
    return json.dumps({
        "count": len(docs),
        "filters": {
            "status": params.status,
            "grade": params.grade,
            "subject": params.subject,
            "document_type": params.document_type,
        },
        "documents": docs,
    }, indent=2)


@mcp.tool(
    name="etl_run_pipeline",
    annotations={
        "title": "Run Full ETL Pipeline",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    }
)
async def etl_run_pipeline(params: RunPipelineInput) -> str:
    """
    Run the complete ETL pipeline on a document (Phases 3–7):

    1. Extract — text, headings, tables, page references
    2. Normalize — clean text, detect language, infer metadata
    3. Chunk — document-type-aware segmentation
    4. Validate — multi-factor quality scoring

    Returns the quality check result including quality_score (0–1),
    status (validated/needs_review/rejected), and a list of specific issues.
    Documents scoring < 0.4 are auto-rejected. Scores 0.4–0.7 go to review queue.
    """
    try:
        result = pipeline().run_full_pipeline(params.document_id)
        import dataclasses
        return json.dumps({
            "success": True,
            "document_id": params.document_id,
            "quality_check": dataclasses.asdict(result),
            "next_steps": _next_steps(result.status),
        }, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, indent=2)


@mcp.tool(
    name="etl_run_stage",
    annotations={
        "title": "Run Single Pipeline Stage",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    }
)
async def etl_run_stage(params: RunStageInput) -> str:
    """
    Run a single pipeline stage on a document.

    Stages (must be run in order):
    - extract    — Phase 3: pull text/structure from raw file
    - normalize  — Phase 4+5: clean text, enrich metadata
    - chunk      — Phase 6: segment into retrieval-ready chunks
    - validate   — Phase 7: score quality and flag issues

    Use this to rerun a single failing stage without rerunning the whole pipeline.
    """
    p = pipeline()
    try:
        stage = params.stage.lower()
        if stage == "extract":
            result = p.extract(params.document_id)
            return json.dumps({
                "success": True, "stage": "extract",
                "extraction_ok": result.extraction_ok,
                "page_count": result.page_count,
                "heading_count": len(result.headings),
                "text_length": len(result.raw_text),
                "ocr_confidence": result.ocr_confidence,
                "error": result.error,
            }, indent=2)
        elif stage == "normalize":
            result = p.normalize(params.document_id)
            return json.dumps({
                "success": True, "stage": "normalize",
                "word_count": result.get("word_count"),
                "language": result.get("language"),
                "curriculum_codes": result.get("curriculum_codes"),
                "metadata_updates": result.get("metadata_updates"),
            }, indent=2)
        elif stage == "chunk":
            chunks = p.chunk(params.document_id)
            types = {}
            for c in chunks:
                types[c.chunk_type] = types.get(c.chunk_type, 0) + 1
            return json.dumps({
                "success": True, "stage": "chunk",
                "total_chunks": len(chunks),
                "chunk_types": types,
                "avg_tokens": int(sum(c.token_count for c in chunks) / max(len(chunks), 1)),
            }, indent=2)
        elif stage == "validate":
            import dataclasses
            result = p.validate(params.document_id)
            return json.dumps({
                "success": True, "stage": "validate",
                "quality_check": dataclasses.asdict(result),
            }, indent=2)
        else:
            return json.dumps({
                "error": f"Unknown stage '{stage}'. Must be one of: extract, normalize, chunk, validate"
            }, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, indent=2)


@mcp.tool(
    name="etl_approve_document",
    annotations={
        "title": "Approve Document",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    }
)
async def etl_approve_document(params: ApproveDocumentInput) -> str:
    """
    Mark a document as approved for production use.

    Sets processing_status to 'approved', records the reviewer name,
    and closes any open review tasks. Approved documents can be indexed
    and used by AI services.
    """
    try:
        doc = pipeline().approve_document(
            params.document_id, params.reviewer, params.notes
        )
        return json.dumps({
            "success": True,
            "document_id": doc.document_id,
            "title": doc.title,
            "processing_status": doc.processing_status,
            "reviewed_by": doc.reviewed_by,
        }, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, indent=2)


@mcp.tool(
    name="etl_reject_document",
    annotations={
        "title": "Reject Document",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    }
)
async def etl_reject_document(params: RejectDocumentInput) -> str:
    """
    Reject a document with an auditable reason.

    Sets processing_status to 'rejected', records reviewer and reason.
    Rejected documents are excluded from the production index and AI services.
    The raw file is preserved for audit purposes.
    """
    try:
        doc = pipeline().reject_document(
            params.document_id, params.reviewer, params.reason
        )
        return json.dumps({
            "success": True,
            "document_id": doc.document_id,
            "title": doc.title,
            "processing_status": doc.processing_status,
            "rejected_reason": doc.rejected_reason,
            "reviewed_by": doc.reviewed_by,
        }, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, indent=2)


@mcp.tool(
    name="etl_reprocess_document",
    annotations={
        "title": "Reprocess Document",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    }
)
async def etl_reprocess_document(params: ReprocessDocumentInput) -> str:
    """
    Reset a document to 'acquired' status and re-run the full pipeline.

    Use after:
    - Source file replacement (improved scan, corrected OCR)
    - Chunking or normalization rule updates
    - Manual metadata corrections
    - Pipeline bug fixes

    The original raw file is preserved. Chunks and quality checks
    from the previous run are overwritten.
    """
    try:
        import dataclasses
        result = pipeline().reprocess_document(params.document_id)
        return json.dumps({
            "success": True,
            "document_id": params.document_id,
            "quality_check": dataclasses.asdict(result),
        }, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, indent=2)


@mcp.tool(
    name="etl_get_review_queue",
    annotations={
        "title": "Get Review Queue",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    }
)
async def etl_get_review_queue() -> str:
    """
    Return all documents currently waiting for human review.

    Review tasks are created automatically when:
    - Quality score is between 0.4 and 0.7
    - Metadata is incomplete
    - License status is unknown
    - Extraction confidence is low

    Use etl_approve_document or etl_reject_document to resolve tasks.
    """
    tasks = pipeline().get_review_queue()
    return json.dumps({
        "pending_count": len(tasks),
        "tasks": tasks,
    }, indent=2)


@mcp.tool(
    name="etl_get_pipeline_stats",
    annotations={
        "title": "Get Pipeline Stats",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    }
)
async def etl_get_pipeline_stats() -> str:
    """
    Return aggregated pipeline health metrics.

    Includes:
    - Document counts per processing_status
    - Total document count
    - Average quality score
    - Pending review count

    Use this for a quick operational health check.
    """
    stats = pipeline().get_pipeline_stats()
    return json.dumps(stats, indent=2)


@mcp.tool(
    name="etl_get_content_gaps",
    annotations={
        "title": "Get Content Gaps",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    }
)
async def etl_get_content_gaps() -> str:
    """
    Analyse the document inventory for content gaps.

    Returns a breakdown of document counts by grade, subject, and document_type.
    Useful for identifying:
    - Grades/subjects with no approved content
    - Missing document types (e.g. no memoranda for Grade 10 Maths)
    - Imbalances across the curriculum

    This is the machine-readable equivalent of Phase 11's content gap dashboard.
    """
    gaps = pipeline().get_content_gaps()
    # Summarise by grade
    by_grade: dict[str, dict] = {}
    for row in gaps:
        g = str(row.get("grade") or "unknown")
        s = row.get("subject") or "unknown"
        dt = row.get("document_type") or "unknown"
        st = row.get("processing_status") or "unknown"
        by_grade.setdefault(g, {}).setdefault(s, {}).setdefault(dt, {})[st] = row.get("cnt", 0)
    return json.dumps({
        "raw_rows": gaps,
        "by_grade": by_grade,
        "summary": (
            f"{len(gaps)} grade×subject×type combinations found. "
            f"Use 'by_grade' to see which grade/subject/type combinations lack approved content."
        ),
    }, indent=2)


@mcp.tool(
    name="etl_get_quality_report",
    annotations={
        "title": "Get Quality Report",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    }
)
async def etl_get_quality_report(params: GetQualityReportInput) -> str:
    """
    Return the most recent quality check report for a document.

    Includes the six quality dimensions and their weighted composite:
    - metadata_score        (20%)
    - extraction_score      (20%)
    - structure_score       (20%)
    - completeness_score    (20%)
    - provenance_score      (10%)
    - training_suitability  (10%)

    Also includes a list of specific quality issues that should be addressed.
    """
    report = pipeline().get_quality_report(params.document_id)
    if not report:
        return json.dumps({
            "error": f"No quality report found for document '{params.document_id}'. "
                     "Run etl_run_pipeline first."
        }, indent=2)
    return json.dumps(report, indent=2)


# ===========================================================================
# HELPERS
# ===========================================================================

def _next_steps(status: str) -> list[str]:
    return {
        ProcessingStatus.validated:    ["Call etl_approve_document to promote to production."],
        ProcessingStatus.needs_review: ["Call etl_get_review_queue to see open tasks.",
                                        "Call etl_approve_document or etl_reject_document after review."],
        ProcessingStatus.rejected:     ["Investigate issues. Fix source file or metadata.",
                                        "Call etl_reprocess_document after fixing."],
    }.get(status, ["Check etl_get_pipeline_stats for overall health."])


# ===========================================================================
# ENTRY POINT
# ===========================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Eduboost ETL MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "streamable-http"],
        default="stdio",
        help="Transport mode (default: stdio for Claude Desktop)"
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()

    print(f"Starting Eduboost ETL MCP server (transport={args.transport})", file=sys.stderr)
    print(f"  DB:      {ETL_DB_URL}", file=sys.stderr)
    print(f"  Storage: {ETL_STORAGE}", file=sys.stderr)

    _start_mcp_server(mcp, transport=args.transport, host=args.host, port=args.port)
