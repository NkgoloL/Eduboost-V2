"""
EduBoost SA — Ingestion API Router
====================================
FastAPI router exposing the ingestion system over HTTP.
Mount this router in the main EduBoost FastAPI application::

    from scripts.ingestion.api import router as ingestion_router
    app.include_router(ingestion_router)

Endpoints
---------
GET  /api/ingestion/sources          — list all available scrapers
GET  /api/ingestion/datasets         — list HuggingFace dataset catalogue
POST /api/ingestion/jobs             — create & enqueue a new job
GET  /api/ingestion/jobs             — list recent jobs
GET  /api/ingestion/jobs/{id}        — get a specific job
POST /api/ingestion/jobs/{id}/start  — (re)start a queued job
POST /api/ingestion/jobs/{id}/cancel — request job cancellation
GET  /api/ingestion/jobs/{id}/progress — live progress snapshot
POST /api/ingestion/pipeline/run     — run pipeline synchronously (dev/test)
GET  /api/ingestion/stats            — aggregated system stats

All endpoints return JSON.  Long-running pipeline runs are always
performed in background tasks; the endpoint returns immediately with
the job ID.
"""
from __future__ import annotations

import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from scripts.ingestion.config import HF_DATASETS, SOURCES
from scripts.ingestion.models import IngestionJob, JobStatus
from scripts.ingestion.queue_manager import QueueManager
from scripts.ingestion.sources import SCRAPER_REGISTRY, ZA_SOURCES, OPEN_SOURCES

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ingestion", tags=["ingestion"])

# ── Dependency: shared queue manager ─────────────────────────────────────────

_queue_manager: QueueManager | None = None


async def get_queue_manager() -> QueueManager:
    global _queue_manager
    if _queue_manager is None:
        redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379")
        _queue_manager = QueueManager(redis_url=redis_url)
        await _queue_manager.connect()
    return _queue_manager


# ── Request / Response schemas ────────────────────────────────────────────────

class CreateJobRequest(BaseModel):
    source_id:   str  = Field(..., description="Scraper source ID (e.g. 'siyavula', 'khan_academy')")
    grade_min:   int  = Field(1,   ge=1, le=12, description="Minimum grade (inclusive)")
    grade_max:   int  = Field(12,  ge=1, le=12, description="Maximum grade (inclusive)")
    limit:       int  = Field(0,   ge=0, description="Max items to scrape per source (0 = unlimited)")
    dry_run:     bool = Field(False, description="Parse but do not write to DB")
    export_jsonl: bool = Field(False, description="Write training JSONL to export_dir")
    priority:    int  = Field(5,   ge=1, le=10, description="Job priority 1 (low) – 10 (high)")

    model_config = {"json_schema_extra": {
        "example": {
            "source_id": "siyavula",
            "grade_min": 10,
            "grade_max": 12,
            "limit": 500,
            "dry_run": False,
        }
    }}


class JobResponse(BaseModel):
    job_id:    str
    source_id: str
    status:    str
    queued_at: str
    message:   str = ""


class ProgressResponse(BaseModel):
    job_id:    str
    source_id: str
    status:    str
    pct:       float
    scraped:   int
    processed: int
    failed:    int
    message:   str
    eta_secs:  int | None = None


class SourceInfo(BaseModel):
    id:           str
    name:         str
    jurisdiction: str
    grade_range:  list[int]
    license:      str
    requires_playwright: bool
    enabled:      bool


class RunPipelineRequest(BaseModel):
    source_ids:  list[str] | None = Field(None, description="Sources to run (None = all)")
    grade_min:   int = Field(1, ge=1, le=12)
    grade_max:   int = Field(12, ge=1, le=12)
    limit:       int = Field(100, ge=1, le=10_000)
    dry_run:     bool = Field(True)


# ── Sources ───────────────────────────────────────────────────────────────────

@router.get(
    "/sources",
    response_model=list[SourceInfo],
    summary="List all available scraper sources",
)
async def list_sources() -> list[SourceInfo]:
    """Return metadata for every registered scraper source."""
    result = []
    for src_id, cfg in SOURCES.items():
        if src_id in SCRAPER_REGISTRY:
            result.append(SourceInfo(
                id=src_id,
                name=cfg.name,
                jurisdiction=cfg.jurisdiction,
                grade_range=list(cfg.grade_range),
                license=cfg.license,
                requires_playwright=cfg.requires_playwright,
                enabled=cfg.enabled,
            ))
    return sorted(result, key=lambda s: s.id)


@router.get(
    "/datasets",
    summary="List HuggingFace dataset catalogue",
)
async def list_datasets() -> list[dict[str, Any]]:
    """Return the full HuggingFace open-dataset catalogue."""
    return HF_DATASETS


# ── Jobs ─────────────────────────────────────────────────────────────────────

@router.post(
    "/jobs",
    response_model=JobResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Create and enqueue an ingestion job",
)
async def create_job(
    req: CreateJobRequest,
    background_tasks: BackgroundTasks,
    qm: QueueManager = Depends(get_queue_manager),
) -> JobResponse:
    """
    Create a new ingestion job and push it onto the Redis queue.

    The job will be picked up by the next available worker.
    Use ``GET /api/ingestion/jobs/{id}/progress`` to monitor it.
    """
    if req.source_id not in SCRAPER_REGISTRY:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown source_id '{req.source_id}'. "
                   f"Valid options: {sorted(SCRAPER_REGISTRY.keys())}",
        )
    if req.grade_min > req.grade_max:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="grade_min must be ≤ grade_max",
        )

    job = IngestionJob(
        source_id=req.source_id,
        config={
            "grade_range": [req.grade_min, req.grade_max],
            "limit":       req.limit,
            "dry_run":     req.dry_run,
            "export_jsonl": req.export_jsonl,
            "priority":    req.priority,
        },
    )

    job_id = await qm.enqueue(job)
    queued_at = datetime.now(timezone.utc).isoformat()

    logger.info("Created job %s for source=%s", job_id, req.source_id)

    return JobResponse(
        job_id=job_id,
        source_id=req.source_id,
        status=JobStatus.PENDING.value,
        queued_at=queued_at,
        message=f"Job queued. Monitor at /api/ingestion/jobs/{job_id}/progress",
    )


@router.get(
    "/jobs",
    summary="List recently queued/running jobs",
)
async def list_jobs(
    n: Annotated[int, Query(ge=1, le=100)] = 20,
    qm: QueueManager = Depends(get_queue_manager),
) -> dict[str, Any]:
    """
    Return the first *n* jobs currently in the queue (oldest first).
    Does not include already-dequeued jobs.
    """
    queue_length = await qm.queue_length()
    jobs = await qm.peek_queue(n=n)
    return {
        "queue_length": queue_length,
        "showing":      len(jobs),
        "jobs":         jobs,
    }


@router.get(
    "/jobs/{job_id}",
    summary="Get a specific job by ID",
)
async def get_job(
    job_id: str,
    qm: QueueManager = Depends(get_queue_manager),
) -> dict[str, Any]:
    """Fetch stored metadata for *job_id* (from Redis hash)."""
    data = await qm.get_job(job_id)
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job '{job_id}' not found",
        )
    return {"job_id": job_id, **data}


@router.post(
    "/jobs/{job_id}/cancel",
    summary="Request cancellation of a running or queued job",
)
async def cancel_job(
    job_id: str,
    qm: QueueManager = Depends(get_queue_manager),
) -> dict[str, str]:
    """
    Signal the worker to cancel *job_id*.

    Cancellation is **cooperative** — the worker checks this flag between
    scrape items. Jobs that are actively mid-request may complete the
    current item before stopping.
    """
    ok = await qm.cancel_job(job_id)
    return {
        "job_id": job_id,
        "status": "cancel_requested" if ok else "already_cancelled",
    }


@router.get(
    "/jobs/{job_id}/progress",
    response_model=ProgressResponse,
    summary="Get live progress for a running job",
)
async def get_progress(
    job_id: str,
    qm: QueueManager = Depends(get_queue_manager),
) -> ProgressResponse:
    """
    Return the latest progress snapshot written by the worker.

    Snapshots are updated after each batch of scrape items.
    Returns 404 if the job has never started or progress has expired.
    """
    snap = await qm.get_progress(job_id)
    if not snap:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No progress data for job '{job_id}'",
        )
    return ProgressResponse(
        job_id=snap.job_id,
        source_id=snap.source_id,
        status=snap.status.value,
        pct=snap.pct,
        scraped=snap.scraped,
        processed=snap.processed,
        failed=snap.failed,
        message=snap.message,
        eta_secs=snap.eta_secs,
    )


# ── Direct pipeline run (dev / testing) ──────────────────────────────────────

@router.post(
    "/pipeline/run",
    summary="Run the pipeline directly (small batches / dev use)",
    status_code=status.HTTP_202_ACCEPTED,
)
async def run_pipeline(
    req: RunPipelineRequest,
    background_tasks: BackgroundTasks,
) -> dict[str, Any]:
    """
    Trigger a pipeline run in a background task.

    This endpoint is intended for development and small-scale testing.
    For production workloads, use ``POST /api/ingestion/jobs`` to enqueue
    jobs that will be picked up by dedicated worker processes.

    Returns immediately with a run ID; no live progress is available
    (check application logs).
    """
    from scripts.ingestion.main import run_ingestion

    run_id = str(uuid.uuid4())

    async def _run() -> None:
        try:
            stats = await run_ingestion(
                source_ids=req.source_ids,
                grade_range=(req.grade_min, req.grade_max),
                limit=req.limit,
                dry_run=req.dry_run,
                job_id=run_id,
            )
            logger.info("Pipeline run %s completed: %s", run_id, stats)
        except Exception as exc:
            logger.exception("Pipeline run %s failed: %s", run_id, exc)

    background_tasks.add_task(_run)

    return {
        "run_id":  run_id,
        "status":  "started",
        "message": "Pipeline running in background — check application logs for progress.",
        "config": {
            "source_ids": req.source_ids,
            "grade_range": [req.grade_min, req.grade_max],
            "limit":       req.limit,
            "dry_run":     req.dry_run,
        },
    }


# ── Stats & health ────────────────────────────────────────────────────────────

@router.get(
    "/stats",
    summary="Aggregated queue and system statistics",
)
async def get_stats(
    qm: QueueManager = Depends(get_queue_manager),
) -> dict[str, Any]:
    """Return high-level stats: queue depth, source count, etc."""
    queue_length = await qm.queue_length()
    return {
        "queue_depth":   queue_length,
        "sources_total": len(SCRAPER_REGISTRY),
        "sources_za":    len(ZA_SOURCES),
        "sources_open":  len(OPEN_SOURCES),
        "datasets_hf":   len(HF_DATASETS),
        "timestamp":     datetime.now(timezone.utc).isoformat(),
    }


@router.get(
    "/health",
    summary="Health check",
)
async def health(
    qm: QueueManager = Depends(get_queue_manager),
) -> dict[str, str]:
    """Check that the ingestion service and Redis are reachable."""
    try:
        await qm.queue_length()
        redis_ok = "ok"
    except Exception as exc:
        redis_ok = f"error: {exc}"

    return {
        "status": "ok" if redis_ok == "ok" else "degraded",
        "redis":  redis_ok,
    }
