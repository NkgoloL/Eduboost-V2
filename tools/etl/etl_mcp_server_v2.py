"""
etl_mcp_server_v2.py — Eduboost ETL MCP Server (v2, all phases)
================================================================
Extends v1 (11 tools) with 9 new tools covering Phases 8–12.

Full tool list (20 tools)
──────────────────────────────────────────────────────────────────
PHASE 1-7 (inherited from v1, re-exported here)
  etl_ingest_document       Phase 1  — acquire & register a document
  etl_get_document          Phase 8  — fetch document record by ID
  etl_list_documents        Phase 8  — filter the document registry
  etl_run_pipeline          Phase 3-7— run all ETL stages on a document
  etl_run_stage             Phase 3-7— run one ETL stage
  etl_approve_document      Phase 11 — approve for production
  etl_reject_document       Phase 11 — reject with auditable reason
  etl_reprocess_document    Phase 11 — reset & re-run pipeline
  etl_get_review_queue      Phase 11 — pending review tasks
  etl_get_pipeline_stats    Phase 12 — aggregated health metrics
  etl_get_content_gaps      Phase 11 — coverage by grade/subject/type
  etl_get_quality_report    Phase 7  — per-document quality check

NEW IN V2
  etl_get_document_chunks   Phase 6/8— inspect chunks of a document
  etl_update_metadata       Phase 5/8— partial metadata correction
  etl_create_document_version Phase 8— snapshot a version
  etl_search_fulltext       Phase 9  — keyword search with citations
  etl_generate_training_data Phase 10— auto-generate training examples
  etl_list_training_datasets Phase 10— list all training datasets
  etl_export_dataset        Phase 10 — export JSONL/CSV/Parquet
  etl_submit_feedback       Phase 12 — ingest user feedback
  etl_get_monitoring_report Phase 12 — full pipeline health snapshot
  etl_get_completeness_report Phase 12— curriculum coverage report

Setup
-----
    pip install mcp[cli] fastmcp

Run (stdio — for Claude Desktop / MCP Inspector):
    python etl_mcp_server_v2.py

Run (HTTP — for remote clients):
    python etl_mcp_server_v2.py --transport streamable-http --port 8765
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import os
import sys
import warnings
from pathlib import Path
from typing import Optional

from tools.etl.mcp_compat import FastMCP
from pydantic import BaseModel, Field, ConfigDict

warnings.warn(
    "tools.etl.etl_mcp_server_v2 is deprecated and will be removed in Release 2.1 (2026-10-31). "
    "Use tools.etl.etl_mcp_server as the canonical entry point instead.",
    DeprecationWarning,
    stacklevel=2,
)

sys.path.insert(0, str(Path(__file__).parent))

# ── Import v1 pipeline + v2/v3 extensions ─────────────────────────────────
from app.services.etl.etl_pipeline import (
    DocumentType, SourceType, LicenseStatus, ProcessingStatus,
    IngestRequest,
)
from app.services.etl.etl_pipeline_v3_additions import EduboostETLv3

# ── Server init ────────────────────────────────────────────────────────────
ETL_DB_URL  = os.getenv("ETL_DB_URL",      "sqlite:///eduboost_etl.db")
ETL_STORAGE = os.getenv("ETL_STORAGE_ROOT", "./data")
ETL_EXPORTS = os.getenv("ETL_EXPORTS_DIR",  "./exports")

mcp = FastMCP("eduboost_etl_v3", json_response=True)
_pipeline: Optional[EduboostETLv3] = None


def pipeline() -> EduboostETLv3:
    """Lazy singleton — initialised on first tool call."""
    global _pipeline
    if _pipeline is None:
        _pipeline = EduboostETLv3(db_url=ETL_DB_URL, storage_root=ETL_STORAGE)
        _pipeline.init_db()
        try:
            _pipeline.init_fts()
        except Exception:
            pass   # FTS5 unavailable in this SQLite build
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
# PYDANTIC INPUT MODELS
# ===========================================================================

class IngestDocumentInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    file_path: str = Field(..., description=(
        "Absolute or relative path to the document file "
        "(PDF, DOCX, TXT, MD, HTML, CSV, XLSX). "
        "Example: '/uploads/grade4_maths_textbook.pdf'"
    ))
    document_type: str = Field(
        default=DocumentType.unknown,
        description="Content category. One of: " + ", ".join(t.value for t in DocumentType)
    )
    source_type: str = Field(
        default=SourceType.manual_upload,
        description="Origin. One of: " + ", ".join(t.value for t in SourceType)
    )
    uploaded_by: str = Field(default="system")
    grade: Optional[int] = Field(default=None, ge=1, le=12)
    subject: Optional[str] = Field(default=None, description="e.g. 'mathematics', 'english'")
    language: str = Field(default="en", description="ISO 639-1 code, e.g. 'en', 'af', 'zu'")
    license_status: str = Field(
        default=LicenseStatus.unknown,
        description="Rights status. One of: " + ", ".join(t.value for t in LicenseStatus)
    )
    source_url: Optional[str] = Field(default=None)
    title: Optional[str] = Field(default=None)
    notes: str = Field(default="")


class GetDocumentInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    document_id: str = Field(..., description="UUID of the document.")


class ListDocumentsInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: Optional[str] = Field(default=None)
    grade: Optional[int] = Field(default=None, ge=1, le=12)
    subject: Optional[str] = Field(default=None)
    document_type: Optional[str] = Field(default=None)
    limit: int = Field(default=50, ge=1, le=500)


class RunPipelineInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    document_id: str


class RunStageInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    document_id: str
    stage: str = Field(..., description="One of: extract, normalize, chunk, validate")


class ApproveDocumentInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    document_id: str
    reviewer: str
    notes: str = Field(default="")


class RejectDocumentInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    document_id: str
    reviewer: str
    reason: str


class ReprocessDocumentInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    document_id: str


class GetQualityReportInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    document_id: str


# ── V2 input models ────────────────────────────────────────────────────────

class GetDocumentChunksInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    document_id: str = Field(..., description="UUID of the document.")
    chunk_type: Optional[str] = Field(
        default=None,
        description=(
            "Optional filter. One of: section, topic, lesson, legal_clause, "
            "assessment_question, answer_memo, table, summary, glossary, paragraph"
        )
    )
    limit: int = Field(default=50, ge=1, le=500, description="Max chunks to return.")


class UpdateMetadataInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    document_id: str = Field(..., description="UUID of the document to update.")
    updated_by: str = Field(default="system", description="Name or user ID making the correction.")
    title: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    subject: Optional[str] = Field(default=None)
    grade: Optional[int] = Field(default=None, ge=1, le=12)
    language: Optional[str] = Field(default=None)
    publisher: Optional[str] = Field(default=None)
    author: Optional[str] = Field(default=None)
    publication_year: Optional[int] = Field(default=None, ge=1900, le=2100)
    curriculum: Optional[str] = Field(default=None, description="e.g. CAPS, IEB, Cambridge")
    province: Optional[str] = Field(default=None)
    license_status: Optional[str] = Field(default=None)
    reviewer_notes: Optional[str] = Field(default=None)


class CreateVersionInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    document_id: str
    change_summary: str = Field(default="", description="Human-readable description of what changed.")
    created_by: str = Field(default="system")


class SearchFulltextInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str = Field(..., description=(
        "Free-text search query. Supports FTS5 operators: "
        "AND, OR, NOT, phrase search with quotes, prefix with *. "
        "Example: 'grade 4 fractions', '\"learning objective\" AND mathematics'"
    ))
    grade: Optional[int] = Field(default=None, ge=1, le=12, description="Filter by grade.")
    subject: Optional[str] = Field(default=None, description="Filter by subject.")
    document_type: Optional[str] = Field(default=None, description="Filter by document type.")
    limit: int = Field(default=10, ge=1, le=100, description="Max results.")


class GenerateTrainingDataInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    example_type: str = Field(
        default="qa",
        description=(
            "Type of training examples to generate. One of:\n"
            "  qa       — question–answer pairs (one per chunk)\n"
            "  summary  — chunk → brief summary\n"
            "  concept  — key concepts + definitions\n"
            "  rubric   — assessment marking guidance\n"
            "In production these templates are replaced by LLM-generated content."
        )
    )
    document_ids: Optional[list[str]] = Field(
        default=None,
        description=(
            "List of document UUIDs to generate examples from. "
            "If omitted, all approved/indexed documents are used."
        )
    )
    dataset_name: Optional[str] = Field(default=None, description="Human-readable name for the dataset.")
    split: str = Field(default="train", description="One of: train, validation, test")
    created_by: str = Field(default="system")


class ListTrainingDatasetsInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    limit: int = Field(default=20, ge=1, le=100)


class ExportDatasetInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    dataset_id: str = Field(..., description="UUID of the training dataset to export.")
    format: str = Field(
        default="jsonl",
        description="Export format. One of: jsonl, csv, parquet"
    )


class SubmitFeedbackInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    user_id: str = Field(..., description="User or session ID submitting the feedback.")
    feedback_type: str = Field(
        ...,
        description=(
            "Category. One of: incorrect_answer, missing_document, "
            "outdated_document, bad_citation, wrong_grade_subject"
        )
    )
    details: str = Field(default="", description="Free-text description of the issue.")
    document_id: Optional[str] = Field(default=None, description="Affected document UUID, if known.")
    chunk_id: Optional[str] = Field(default=None, description="Affected chunk UUID, if known.")


# ── V3 Input Models ────────────────────────────────────────────────────────

class GetAuditTrailInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    document_id: str = Field(..., description="UUID of the document.")
    limit: int = Field(default=50, ge=1, le=500)


class DeprecateDocumentInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    document_id: str = Field(..., description="UUID of the document to deprecate.")
    deprecated_by: str = Field(..., description="Reviewer / admin user ID.")
    reason: str = Field(default="", description="Human-readable deprecation reason.")
    replacement_id: Optional[str] = Field(
        default=None,
        description="document_id of the replacement document, if one exists."
    )


class BulkReviewInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    document_ids: list[str] = Field(
        ..., min_length=1, max_length=200,
        description="List of document UUIDs to approve or reject."
    )
    action: str = Field(
        ..., description="One of: approve | reject"
    )
    reviewer: str = Field(..., description="Reviewer user ID / email.")
    reason: str = Field(default="", description="Optional shared note for all decisions.")


class AssignReviewerInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    task_id: str = Field(..., description="UUID of the review task.")
    document_id: str = Field(..., description="UUID of the document under review.")
    assigned_to: str = Field(..., description="User ID / email of the assignee.")
    assigned_by: str = Field(default="system")
    priority: str = Field(
        default="normal",
        description="One of: low | normal | high | critical"
    )
    due_days: Optional[int] = Field(
        default=None, ge=1, le=90,
        description="Days from now until the review is due."
    )


class GetReviewerWorkloadInput(BaseModel):
    model_config = ConfigDict(extra="forbid")


class SplitDatasetInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    dataset_id: str = Field(..., description="UUID of the parent dataset to split.")
    train: float = Field(default=0.70, ge=0.1, le=0.9,
                         description="Fraction of examples for the train split.")
    val: float = Field(default=0.15, ge=0.0, le=0.5,
                       description="Fraction for the validation split (0 to skip).")
    test: float = Field(default=0.15, ge=0.05, le=0.5,
                        description="Fraction for the test split.")
    seed: int = Field(default=42, description="Random seed for reproducibility.")


class CheckContaminationInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    train_dataset_id: str = Field(..., description="UUID of the training dataset.")
    test_dataset_id: str  = Field(..., description="UUID of the test dataset.")
    similarity_threshold: float = Field(
        default=0.90, ge=0.5, le=1.0,
        description="Exact-match hash threshold. 0.9 = flag 90%+ similar inputs."
    )


class GetDatasetStatisticsInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    dataset_id: str = Field(..., description="UUID of the dataset.")


class ResolveFeedbackInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    feedback_id: str = Field(..., description="UUID of the feedback item.")
    resolved_by: str = Field(..., description="Reviewer / admin user ID.")
    resolution_type: str = Field(
        ...,
        description="One of: fixed | acknowledged | wont_fix | duplicate"
    )
    notes: str = Field(default="", description="Optional notes about the resolution.")


class GetMetricWindowInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    metric_name: str = Field(
        ...,
        description=(
            "Metric counter name. Common values: ingestion_count, extraction_failures, "
            "validation_failures, approval_count, rejection_count, feedback_count."
        )
    )
    hours: int = Field(default=24, ge=1, le=720,
                       description="Lookback window in hours (max 30 days).")
    bucket_minutes: int = Field(
        default=60, ge=5, le=1440,
        description="Bucket size in minutes for aggregation."
    )


# ===========================================================================
# TOOLS — PHASE 1–7 (v1 parity)
# ===========================================================================

@mcp.tool(name="etl_ingest_document", annotations={
    "title": "Ingest Document",
    "readOnlyHint": False, "destructiveHint": False,
    "idempotentHint": False, "openWorldHint": False,
})
async def etl_ingest_document(params: IngestDocumentInput) -> str:
    """
    Phase 1 — Acquire a document file and register it in the pipeline.

    Performs SHA-256 duplicate detection, copies to immutable raw storage,
    registers the document source, and creates the canonical record with
    'acquired' status. Returns document_id for use in subsequent tool calls.
    """
    try:
        doc = pipeline().ingest(IngestRequest(
            file_path=params.file_path, source_type=params.source_type,
            uploaded_by=params.uploaded_by, document_type=params.document_type,
            source_url=params.source_url, license_status=params.license_status,
            grade=params.grade, subject=params.subject,
            language=params.language, title=params.title, notes=params.notes,
        ))
        return json.dumps({
            "success": True,
            "document_id": doc.document_id,
            "title": doc.title,
            "document_type": doc.document_type,
            "processing_status": doc.processing_status,
            "checksum": doc.checksum[:16] + "…",
            "file_size_bytes": doc.file_size_bytes,
            "next_step": f"Call etl_run_pipeline with document_id='{doc.document_id}'",
        }, indent=2)
    except ValueError as e:
        return json.dumps({"success": False, "error": str(e)}, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, indent=2)


@mcp.tool(name="etl_get_document", annotations={
    "title": "Get Document", "readOnlyHint": True,
    "destructiveHint": False, "idempotentHint": True, "openWorldHint": False,
})
async def etl_get_document(params: GetDocumentInput) -> str:
    """Fetch the full canonical record for a document by its UUID."""
    try:
        doc = pipeline()._load_document(params.document_id)
        return json.dumps(dataclasses.asdict(doc), indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, indent=2)


@mcp.tool(name="etl_list_documents", annotations={
    "title": "List Documents", "readOnlyHint": True,
    "destructiveHint": False, "idempotentHint": True, "openWorldHint": False,
})
async def etl_list_documents(params: ListDocumentsInput) -> str:
    """Filter and search the document registry. Supports status, grade, subject, type."""
    docs = pipeline().list_documents(
        status=params.status, grade=params.grade,
        subject=params.subject, document_type=params.document_type,
        limit=params.limit,
    )
    return json.dumps({"count": len(docs), "documents": docs}, indent=2)


@mcp.tool(name="etl_run_pipeline", annotations={
    "title": "Run Full Pipeline", "readOnlyHint": False,
    "destructiveHint": False, "idempotentHint": False, "openWorldHint": False,
})
async def etl_run_pipeline(params: RunPipelineInput) -> str:
    """
    Run all ETL phases (3–7) on a document: extract → normalize →
    metadata enrichment → chunk → quality validate.
    Returns the quality check result and next recommended steps.
    """
    try:
        result = pipeline().run_full_pipeline(params.document_id)
        return json.dumps({
            "success": True,
            "document_id": params.document_id,
            "quality_score": result.quality_score,
            "status": result.status,
            "issues": result.issues,
            "scores": {
                "metadata":    result.metadata_score,
                "extraction":  result.extraction_score,
                "structure":   result.structure_score,
                "completeness": result.completeness_score,
                "provenance":  result.provenance_score,
                "training":    result.training_suitability,
            },
            "next_steps": _next_steps(result.status),
        }, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, indent=2)


@mcp.tool(name="etl_run_stage", annotations={
    "title": "Run Pipeline Stage", "readOnlyHint": False,
    "destructiveHint": False, "idempotentHint": False, "openWorldHint": False,
})
async def etl_run_stage(params: RunStageInput) -> str:
    """
    Run a single pipeline stage on a document.
    stage: extract | normalize | chunk | validate
    Useful for debugging or re-running one step after a fix.
    """
    p = pipeline()
    try:
        doc = p._load_document(params.document_id)
        if params.stage == "extract":
            p.extract(params.document_id)
            msg = "Extraction complete."
        elif params.stage == "normalize":
            p.normalize(params.document_id)
            msg = "Normalisation complete."
        elif params.stage == "chunk":
            n = p.chunk(params.document_id)
            msg = f"{n} chunks produced."
        elif params.stage == "validate":
            result = p.validate(params.document_id)
            return json.dumps({
                "success": True, "stage": "validate",
                "quality_check": dataclasses.asdict(result),
            }, indent=2)
        else:
            return json.dumps({"success": False, "error": f"Unknown stage '{params.stage}'."})
        doc = p._load_document(params.document_id)
        return json.dumps({
            "success": True, "stage": params.stage, "message": msg,
            "processing_status": doc.processing_status,
        }, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, indent=2)


@mcp.tool(name="etl_approve_document", annotations={
    "title": "Approve Document", "readOnlyHint": False,
    "destructiveHint": False, "idempotentHint": True, "openWorldHint": False,
})
async def etl_approve_document(params: ApproveDocumentInput) -> str:
    """
    Approve a document for production use. Sets status → 'approved'.
    After approval the document is eligible for search indexing and
    training data generation. Reviewer and notes are recorded in the audit trail.
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


@mcp.tool(name="etl_reject_document", annotations={
    "title": "Reject Document", "readOnlyHint": False,
    "destructiveHint": False, "idempotentHint": True, "openWorldHint": False,
})
async def etl_reject_document(params: RejectDocumentInput) -> str:
    """
    Reject a document with a machine-readable reason. Sets status → 'rejected'.
    Rejected documents are excluded from production. Raw file is preserved.
    """
    try:
        doc = pipeline().reject_document(
            params.document_id, params.reviewer, params.reason
        )
        return json.dumps({
            "success": True,
            "document_id": doc.document_id,
            "processing_status": doc.processing_status,
            "rejected_reason": doc.rejected_reason,
        }, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, indent=2)


@mcp.tool(name="etl_reprocess_document", annotations={
    "title": "Reprocess Document", "readOnlyHint": False,
    "destructiveHint": False, "idempotentHint": False, "openWorldHint": False,
})
async def etl_reprocess_document(params: ReprocessDocumentInput) -> str:
    """Reset a document to 'acquired' and re-run the full pipeline."""
    try:
        result = pipeline().reprocess_document(params.document_id)
        return json.dumps({
            "success": True,
            "document_id": params.document_id,
            "quality_check": dataclasses.asdict(result),
        }, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, indent=2)


@mcp.tool(name="etl_get_review_queue", annotations={
    "title": "Get Review Queue", "readOnlyHint": True,
    "destructiveHint": False, "idempotentHint": True, "openWorldHint": False,
})
async def etl_get_review_queue() -> str:
    """List all documents awaiting human review (auto-flagged or user-reported)."""
    tasks = pipeline().get_review_queue()
    return json.dumps({"pending_count": len(tasks), "tasks": tasks}, indent=2)


@mcp.tool(name="etl_get_pipeline_stats", annotations={
    "title": "Get Pipeline Stats", "readOnlyHint": True,
    "destructiveHint": False, "idempotentHint": True, "openWorldHint": False,
})
async def etl_get_pipeline_stats() -> str:
    """Return aggregated pipeline health metrics: counts per status, avg quality, pending reviews."""
    return json.dumps(pipeline().get_pipeline_stats(), indent=2)


@mcp.tool(name="etl_get_content_gaps", annotations={
    "title": "Get Content Gaps", "readOnlyHint": True,
    "destructiveHint": False, "idempotentHint": True, "openWorldHint": False,
})
async def etl_get_content_gaps() -> str:
    """
    Identify missing content by grade × subject × document_type.
    Useful for content team planning and dashboard gap matrices.
    """
    gaps = pipeline().get_content_gaps()
    by_grade: dict = {}
    for row in gaps:
        g = str(row.get("grade") or "unknown")
        s = row.get("subject") or "unknown"
        dt = row.get("document_type") or "unknown"
        st = row.get("processing_status") or "unknown"
        by_grade.setdefault(g, {}).setdefault(s, {}).setdefault(dt, {})[st] = row.get("cnt", 0)
    return json.dumps({"raw_rows": gaps, "by_grade": by_grade}, indent=2)


@mcp.tool(name="etl_get_quality_report", annotations={
    "title": "Get Quality Report", "readOnlyHint": True,
    "destructiveHint": False, "idempotentHint": True, "openWorldHint": False,
})
async def etl_get_quality_report(params: GetQualityReportInput) -> str:
    """
    Return the latest quality check for a document, including all six dimension scores
    and a list of specific issues that should be resolved before approval.
    """
    report = pipeline().get_quality_report(params.document_id)
    if not report:
        return json.dumps({
            "error": f"No quality report for '{params.document_id}'. Run etl_run_pipeline first."
        })
    return json.dumps(report, indent=2)


# ===========================================================================
# TOOLS — PHASE 8: CANONICAL CONTENT STORE (new in v2)
# ===========================================================================

@mcp.tool(name="etl_get_document_chunks", annotations={
    "title": "Get Document Chunks", "readOnlyHint": True,
    "destructiveHint": False, "idempotentHint": True, "openWorldHint": False,
})
async def etl_get_document_chunks(params: GetDocumentChunksInput) -> str:
    """
    Inspect the chunks produced for a document.
    Each chunk includes: heading, content, section_path, page range,
    curriculum_code, token_count, and parent chunk reference.
    Useful for debugging segmentation or building retrieval datasets.
    """
    try:
        chunks = pipeline().get_document_chunks(
            params.document_id, chunk_type=params.chunk_type
        )
        return json.dumps({
            "document_id": params.document_id,
            "total_chunks": len(chunks),
            "chunks": chunks[:params.limit],
        }, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, indent=2)


@mcp.tool(name="etl_update_metadata", annotations={
    "title": "Update Document Metadata", "readOnlyHint": False,
    "destructiveHint": False, "idempotentHint": True, "openWorldHint": False,
})
async def etl_update_metadata(params: UpdateMetadataInput) -> str:
    """
    Correct or enrich document metadata without reprocessing the document.
    Allowed fields: title, description, subject, grade, language, publisher,
    author, publication_year, curriculum, province, license_status, reviewer_notes.
    Automatically creates a version snapshot for audit purposes.
    """
    updates = {k: v for k, v in {
        "title": params.title, "description": params.description,
        "subject": params.subject, "grade": params.grade,
        "language": params.language, "publisher": params.publisher,
        "author": params.author, "publication_year": params.publication_year,
        "curriculum": params.curriculum, "province": params.province,
        "license_status": params.license_status, "reviewer_notes": params.reviewer_notes,
    }.items() if v is not None}

    if not updates:
        return json.dumps({"success": False, "error": "No fields provided to update."})
    try:
        result = pipeline().update_document_metadata(
            params.document_id, updates, updated_by=params.updated_by
        )
        return json.dumps({"success": True, "document_id": params.document_id, **result}, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, indent=2)


@mcp.tool(name="etl_create_document_version", annotations={
    "title": "Create Document Version", "readOnlyHint": False,
    "destructiveHint": False, "idempotentHint": False, "openWorldHint": False,
})
async def etl_create_document_version(params: CreateVersionInput) -> str:
    """
    Snapshot the current normalised output as a new document version.
    Call after significant metadata updates or re-processing to create
    an auditable version history. Versions are stored with semver numbers (1.0, 1.1, …).
    """
    try:
        v = pipeline().create_version(
            params.document_id,
            change_summary=params.change_summary,
            created_by=params.created_by,
        )
        return json.dumps(dataclasses.asdict(v), indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, indent=2)


# ===========================================================================
# TOOLS — PHASE 9: SEARCH & RETRIEVAL (new in v2)
# ===========================================================================

@mcp.tool(name="etl_search_fulltext", annotations={
    "title": "Full-Text Search", "readOnlyHint": True,
    "destructiveHint": False, "idempotentHint": True, "openWorldHint": False,
})
async def etl_search_fulltext(params: SearchFulltextInput) -> str:
    """
    Keyword search across all approved document chunks using FTS5 (or LIKE fallback).

    Supports FTS5 operators: AND, OR, NOT, phrase quotes, prefix *.
    Examples:
      'fractions grade 4'
      '"learning objective" AND mathematics'
      'CAPS* AND "lesson plan"'

    Each result includes a citation object with document_id, title, section_path,
    and page numbers — suitable for AI response attribution.

    Returns up to `limit` ranked results with content previews.
    """
    try:
        hits = pipeline().search_fulltext(
            params.query, grade=params.grade, subject=params.subject,
            document_type=params.document_type, limit=params.limit,
        )
        # Trim content for API response size
        for h in hits:
            h["content_preview"] = h.get("content", "")[:300]
            h.pop("content", None)
        return json.dumps({
            "query": params.query,
            "result_count": len(hits),
            "results": hits,
        }, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, indent=2)


# ===========================================================================
# TOOLS — PHASE 10: TRAINING DATASET BUILDER (new in v2)
# ===========================================================================

@mcp.tool(name="etl_generate_training_data", annotations={
    "title": "Generate Training Data", "readOnlyHint": False,
    "destructiveHint": False, "idempotentHint": False, "openWorldHint": False,
})
async def etl_generate_training_data(params: GenerateTrainingDataInput) -> str:
    """
    Phase 10 — Auto-generate training examples from approved/indexed documents.

    example_type options:
      qa       — Question–answer pairs (one per chunk, from headings)
      summary  — Chunk → condensed summary
      concept  — Key concept + definition extraction
      rubric   — Assessment marking guidance (from memoranda chunks)

    In production, the template generation is replaced by LLM-generated content.
    Synthetic examples are flagged with is_synthetic=true.
    All examples are traceable to their source document and chunk.

    Returns dataset_id for use with etl_export_dataset.
    """
    try:
        dataset = pipeline().generate_training_dataset(
            document_ids=params.document_ids,
            example_type=params.example_type,
            dataset_name=params.dataset_name,
            split=params.split,
            is_synthetic=True,
            created_by=params.created_by,
        )
        return json.dumps({
            "success": True,
            "dataset_id": dataset.dataset_id,
            "name": dataset.name,
            "example_type": dataset.dataset_type,
            "split": dataset.split,
            "example_count": dataset.example_count,
            "is_synthetic": dataset.is_synthetic,
            "next_step": (
                f"Call etl_export_dataset with dataset_id='{dataset.dataset_id}' "
                "to export as JSONL/CSV/Parquet."
            ),
        }, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, indent=2)


@mcp.tool(name="etl_list_training_datasets", annotations={
    "title": "List Training Datasets", "readOnlyHint": True,
    "destructiveHint": False, "idempotentHint": True, "openWorldHint": False,
})
async def etl_list_training_datasets(params: ListTrainingDatasetsInput) -> str:
    """
    List all training datasets with metadata: type, split, example count,
    version, and export status.
    """
    datasets = pipeline().list_training_datasets()
    return json.dumps({
        "count": len(datasets),
        "datasets": datasets[:params.limit],
    }, indent=2)


@mcp.tool(name="etl_export_dataset", annotations={
    "title": "Export Training Dataset", "readOnlyHint": False,
    "destructiveHint": False, "idempotentHint": True, "openWorldHint": False,
})
async def etl_export_dataset(params: ExportDatasetInput) -> str:
    """
    Export a training dataset to disk.
    format: jsonl (default) | csv | parquet

    JSONL format: one JSON object per line with keys:
      id, type, input, output, grade, subject, doc_id, synthetic

    Records the export path and timestamp in the dataset record.
    Returns the full output file path.
    """
    try:
        path = pipeline().export_dataset(
            params.dataset_id, fmt=params.format, out_dir=ETL_EXPORTS
        )
        if not path:
            return json.dumps({"success": False, "error": "No examples found for this dataset."})
        return json.dumps({
            "success": True,
            "dataset_id": params.dataset_id,
            "format": params.format,
            "output_path": path,
        }, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, indent=2)


# ===========================================================================
# TOOLS — PHASE 12: MONITORING & FEEDBACK LOOP (new in v2)
# ===========================================================================

@mcp.tool(name="etl_submit_feedback", annotations={
    "title": "Submit User Feedback", "readOnlyHint": False,
    "destructiveHint": False, "idempotentHint": False, "openWorldHint": False,
})
async def etl_submit_feedback(params: SubmitFeedbackInput) -> str:
    """
    Phase 12 — Ingest user feedback into the pipeline's feedback loop.

    Feedback types:
      incorrect_answer    — AI gave a wrong answer citing this document
      missing_document    — A required document is not in the system
      outdated_document   — Content is out of date
      bad_citation        — Citation is wrong or doesn't match content
      wrong_grade_subject — Document is miscategorised

    Actionable feedback types automatically create review tasks so content
    teams can investigate and resolve the issue.
    """
    try:
        fb = pipeline().submit_feedback(
            user_id=params.user_id,
            feedback_type=params.feedback_type,
            details=params.details,
            document_id=params.document_id,
            chunk_id=params.chunk_id,
        )
        return json.dumps({
            "success": True,
            "feedback_id": fb.feedback_id,
            "feedback_type": fb.feedback_type,
            "review_task_created": fb.review_task_id is not None,
            "review_task_id": fb.review_task_id,
        }, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, indent=2)


@mcp.tool(name="etl_get_monitoring_report", annotations={
    "title": "Get Monitoring Report", "readOnlyHint": True,
    "destructiveHint": False, "idempotentHint": True, "openWorldHint": False,
})
async def etl_get_monitoring_report() -> str:
    """
    Phase 12 — Full pipeline health snapshot.

    Includes:
    - Document totals and stage distribution
    - 7-day ingestion rate
    - 30-day approval rate
    - Average quality score
    - Stale documents (>90 days in early stages)
    - Job failure rate (last 24h)
    - Pending review count
    - User feedback summary (last 30 days)
    - Actionable alerts

    Use this for operational dashboards and scheduled health checks.
    """
    try:
        report = pipeline().get_monitoring_report()
        return json.dumps(dataclasses.asdict(report), indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, indent=2)


@mcp.tool(name="etl_get_completeness_report", annotations={
    "title": "Get Completeness Report", "readOnlyHint": True,
    "destructiveHint": False, "idempotentHint": True, "openWorldHint": False,
})
async def etl_get_completeness_report() -> str:
    """
    Phase 12 — Curriculum coverage report.

    Checks whether every grade (1–12) × subject × required document type
    (textbook, lesson_plan, past_paper, assessment_rubric) has at least one
    approved document.

    Returns:
    - coverage_pct — percentage of required slots filled
    - missing       — list of {grade, subject, document_type} combinations with no approved content
    """
    try:
        report = pipeline().get_completeness_report()
        return json.dumps(report, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, indent=2)


# ===========================================================================
# TOOLS — V3 ADDITIONS (PHASES 8, 10, 11, 12)
# ===========================================================================

@mcp.tool(name="etl_get_audit_trail", annotations={
    "title": "Get Document Audit Trail",
    "readOnlyHint": True, "destructiveHint": False,
    "idempotentHint": True, "openWorldHint": False,
})
async def etl_get_audit_trail(params: GetAuditTrailInput) -> str:
    """
    Phase 8 — Return the chronological audit trail for a document.

    Every status change, metadata edit, approval, rejection, and deprecation
    is recorded. Use this to investigate how a document reached its current
    state or to satisfy audit requirements.

    Returns: list of {audit_id, action, field_name, old_value, new_value,
                       performed_by, performed_at, notes}
    """
    trail = pipeline().get_audit_trail(params.document_id, limit=params.limit)
    return json.dumps({"document_id": params.document_id, "count": len(trail), "trail": trail},
                      indent=2)


@mcp.tool(name="etl_deprecate_document", annotations={
    "title": "Deprecate Document",
    "readOnlyHint": False, "destructiveHint": False,
    "idempotentHint": True, "openWorldHint": False,
})
async def etl_deprecate_document(params: DeprecateDocumentInput) -> str:
    """
    Phase 8 — Soft-deprecate a document (status → archived).

    Deprecated documents remain in the database for audit purposes but are
    excluded from search indexes, training sets, and the production content store.
    If a replacement document exists, pass its ID to create a traceability link.

    Use this when:
    - A newer edition of a document has been ingested
    - A document was found to be incorrectly licensed
    - Content is permanently outdated
    """
    try:
        result = pipeline().deprecate_document(
            document_id=params.document_id,
            deprecated_by=params.deprecated_by,
            reason=params.reason,
            replacement_id=params.replacement_id,
        )
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, indent=2)


@mcp.tool(name="etl_bulk_review", annotations={
    "title": "Bulk Approve or Reject Documents",
    "readOnlyHint": False, "destructiveHint": False,
    "idempotentHint": False, "openWorldHint": False,
})
async def etl_bulk_review(params: BulkReviewInput) -> str:
    """
    Phase 11 — Approve or reject up to 200 documents in one call.

    Useful for processing large review queues after a batch ingestion run.
    Each document result is reported individually — partial failures are normal
    (e.g., documents already approved or in an incompatible state).

    Returns: {total, succeeded, failed, results: [{document_id, success, ?error}]}
    """
    try:
        result = pipeline().bulk_review(
            document_ids=params.document_ids,
            action=params.action,
            reviewer=params.reviewer,
            reason=params.reason,
        )
        return json.dumps(dataclasses.asdict(result), indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, indent=2)


@mcp.tool(name="etl_assign_reviewer", annotations={
    "title": "Assign Review Task to Reviewer",
    "readOnlyHint": False, "destructiveHint": False,
    "idempotentHint": False, "openWorldHint": False,
})
async def etl_assign_reviewer(params: AssignReviewerInput) -> str:
    """
    Phase 11 — Assign an open review task to a specific team member.

    Sets priority (low / normal / high / critical) and an optional due date.
    Use etl_get_reviewer_workload to balance assignments across reviewers.
    """
    try:
        result = pipeline().assign_reviewer(
            task_id=params.task_id,
            document_id=params.document_id,
            assigned_to=params.assigned_to,
            assigned_by=params.assigned_by,
            priority=params.priority,
            due_days=params.due_days,
        )
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, indent=2)


@mcp.tool(name="etl_get_reviewer_workload", annotations={
    "title": "Get Reviewer Workload",
    "readOnlyHint": True, "destructiveHint": False,
    "idempotentHint": True, "openWorldHint": False,
})
async def etl_get_reviewer_workload(params: GetReviewerWorkloadInput) -> str:
    """
    Phase 11 — Return open task counts per reviewer.

    Includes urgent (high/critical priority) task counts separately.
    Use before etl_assign_reviewer to avoid overloading any one reviewer.

    Returns: [{assigned_to, open_tasks, urgent}]
    """
    try:
        workload = pipeline().get_reviewer_workload()
        return json.dumps({"reviewers": workload}, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, indent=2)


@mcp.tool(name="etl_split_dataset", annotations={
    "title": "Split Training Dataset into Train/Val/Test",
    "readOnlyHint": False, "destructiveHint": False,
    "idempotentHint": False, "openWorldHint": False,
})
async def etl_split_dataset(params: SplitDatasetInput) -> str:
    """
    Phase 10 — Split a training dataset into train / validation / test subsets.

    Uses deterministic hash-based shuffling for reproducibility. Creates three
    child datasets, moves examples into them, and records the split in
    dataset_splits. Run etl_check_contamination afterwards to verify no leakage.

    Returns: {parent_dataset_id, train_dataset_id, val_dataset_id,
              test_dataset_id, train_count, val_count, test_count}
    """
    try:
        assert abs(params.train + params.val + params.test - 1.0) < 1e-6, \
            "train + val + test must equal 1.0"
        result = pipeline().split_dataset(
            dataset_id=params.dataset_id,
            train=params.train, val=params.val, test=params.test,
            seed=params.seed,
        )
        return json.dumps(dataclasses.asdict(result), indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, indent=2)


@mcp.tool(name="etl_check_contamination", annotations={
    "title": "Check Train/Test Contamination",
    "readOnlyHint": False, "destructiveHint": False,
    "idempotentHint": True, "openWorldHint": False,
})
async def etl_check_contamination(params: CheckContaminationInput) -> str:
    """
    Phase 10 — Detect input_text overlap between train and test datasets.

    Uses SHA-256 hashing for exact-match detection. Records results in
    contamination_checks for audit. A clean dataset returns passed=true
    and overlap_count=0.

    Run this after etl_split_dataset and before exporting training data.

    Returns: {check_id, overlap_count, overlap_example_ids, passed}
    """
    try:
        report = pipeline().check_contamination(
            train_dataset_id=params.train_dataset_id,
            test_dataset_id=params.test_dataset_id,
            similarity_threshold=params.similarity_threshold,
        )
        return json.dumps(dataclasses.asdict(report), indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, indent=2)


@mcp.tool(name="etl_get_dataset_statistics", annotations={
    "title": "Get Training Dataset Statistics",
    "readOnlyHint": True, "destructiveHint": False,
    "idempotentHint": True, "openWorldHint": False,
})
async def etl_get_dataset_statistics(params: GetDatasetStatisticsInput) -> str:
    """
    Phase 10 — Detailed statistics for a training dataset.

    Includes:
    - synthetic vs human-reviewed example counts (and percentages)
    - average quality score
    - example type breakdown (qa / summary / concept / rubric / ...)
    - grade distribution
    - subject distribution

    Use before exporting to verify dataset composition meets quality criteria.
    """
    try:
        stats = pipeline().get_dataset_statistics(params.dataset_id)
        return json.dumps(stats, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, indent=2)


@mcp.tool(name="etl_resolve_feedback", annotations={
    "title": "Resolve User Feedback",
    "readOnlyHint": False, "destructiveHint": False,
    "idempotentHint": False, "openWorldHint": False,
})
async def etl_resolve_feedback(params: ResolveFeedbackInput) -> str:
    """
    Phase 12 — Mark a user feedback item as resolved.

    resolution_type options:
      fixed         — Issue confirmed and corrected in the pipeline
      acknowledged  — Known issue, will be addressed in next cycle
      wont_fix      — Intentional design decision, no action needed
      duplicate     — Already tracked via another feedback item

    Resolving feedback closes any associated review task.
    """
    try:
        result = pipeline().resolve_feedback(
            feedback_id=params.feedback_id,
            resolved_by=params.resolved_by,
            resolution_type=params.resolution_type,
            notes=params.notes,
        )
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, indent=2)


@mcp.tool(name="etl_get_metric_window", annotations={
    "title": "Get Pipeline Metric Time Window",
    "readOnlyHint": True, "destructiveHint": False,
    "idempotentHint": True, "openWorldHint": False,
})
async def etl_get_metric_window(params: GetMetricWindowInput) -> str:
    """
    Phase 12 — Return time-bucketed metric aggregates for sparkline charts.

    Queries pipeline_metrics for a named counter and returns sum-per-bucket
    over the requested window.

    Common metric_name values:
      ingestion_count      — documents successfully ingested per hour
      extraction_failures  — extraction stage failures
      validation_failures  — quality gate failures
      approval_count       — documents approved per day
      rejection_count      — documents rejected per day
      feedback_count       — user feedback submissions

    Returns: [{bucket: "2025-05-20T14:00", value: 12.0}, ...]
    """
    try:
        buckets = pipeline().get_metric_window(
            metric_name=params.metric_name,
            hours=params.hours,
            bucket_minutes=params.bucket_minutes,
        )
        return json.dumps({
            "metric_name": params.metric_name,
            "hours": params.hours,
            "bucket_minutes": params.bucket_minutes,
            "buckets": buckets,
        }, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, indent=2)


# ===========================================================================
# HELPERS
# ===========================================================================

def _next_steps(status: str) -> list[str]:
    return {
        ProcessingStatus.validated.value: [
            "Call etl_approve_document to promote to production.",
            "Optionally call etl_create_document_version to snapshot this state.",
        ],
        ProcessingStatus.needs_review.value: [
            "Call etl_get_review_queue to see open tasks.",
            "Call etl_get_quality_report for detailed issue breakdown.",
            "Call etl_update_metadata to fix incomplete fields.",
            "Then call etl_approve_document or etl_reject_document.",
        ],
        ProcessingStatus.rejected.value: [
            "Investigate issues. Fix source file or metadata.",
            "Call etl_reprocess_document after fixing.",
        ],
        ProcessingStatus.approved.value: [
            "Call etl_generate_training_data to build training examples.",
            "Index chunks with an embedding model then call etl_search_fulltext to verify.",
        ],
    }.get(status, ["Check etl_get_pipeline_stats for overall health."])


# ===========================================================================
# ENTRY POINT
# ===========================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Eduboost ETL MCP Server v2")
    parser.add_argument("--transport", choices=["stdio", "streamable-http"],
                        default="stdio")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()

    print(f"Starting Eduboost ETL MCP Server v2 (transport={args.transport})", file=sys.stderr)
    print(f"  DB:      {ETL_DB_URL}",  file=sys.stderr)
    print(f"  Storage: {ETL_STORAGE}", file=sys.stderr)
    print(f"  Exports: {ETL_EXPORTS}", file=sys.stderr)

    _start_mcp_server(mcp, transport=args.transport, host=args.host, port=args.port)
