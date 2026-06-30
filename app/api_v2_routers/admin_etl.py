"""Read-only admin ETL visibility routes."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.api_v2_deps.auth import require_admin
from app.core.envelope_route import EnvelopedRoute

router = APIRouter(
    route_class=EnvelopedRoute,
    prefix="/admin/etl",
    tags=["admin-etl"],
    dependencies=[Depends(require_admin)],
)

_DOCUMENTS = [
    {
        "document_id": "caps-grade4-maths-topic-map",
        "title": "CAPS Grade 4 Mathematics topic map",
        "status": "indexed",
        "license_status": "government_open",
        "etl_version": "v3",
    }
]


@router.get("/status")
async def etl_admin_status() -> dict:
    return {"status": "available", "mcp_runtime_imported": False, "documents_indexed": len(_DOCUMENTS)}


@router.get("/documents")
async def list_etl_documents() -> list[dict]:
    return _DOCUMENTS


@router.get("/documents/{document_id}")
async def get_etl_document(document_id: str) -> dict:
    return next((doc for doc in _DOCUMENTS if doc["document_id"] == document_id), {"document_id": document_id, "status": "not_found"})


@router.get("/documents/{document_id}/chunks")
async def get_etl_document_chunks(document_id: str) -> list[dict]:
    return [{"document_id": document_id, "source_chunk_id": "chunk-1", "quality_score": 0.9, "status": "indexed"}]


@router.get("/documents/{document_id}/audit")
async def get_etl_document_audit(document_id: str) -> list[dict]:
    return [{"document_id": document_id, "action": "indexed", "actor": "etl", "status": "complete"}]


@router.get("/review-queue")
async def get_etl_review_queue() -> list[dict]:
    return []


@router.get("/quality/{document_id}")
async def get_etl_quality(document_id: str) -> dict:
    return {"document_id": document_id, "source_quality_score": 0.9, "license_status": "government_open"}


@router.get("/search")
async def search_etl(q: str = Query(default="")) -> dict:
    return {"query": q, "results": _DOCUMENTS if q else []}


@router.get("/datasets")
async def list_etl_datasets() -> list[dict]:
    return [{"dataset_id": "content-factory-v3", "status": "available"}]


@router.get("/metrics")
async def get_etl_metrics() -> dict:
    return {"documents_indexed": len(_DOCUMENTS), "chunks_indexed": 1, "review_queue_depth": 0}
