"""Admin-only management API for grounded Phase 1 generation runs."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Literal

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.api_v2_deps.auth import AuthContext, require_admin
from app.core.config import get_settings
from app.core.database import get_db
from app.models.content_factory import ContentGenerationRun, ContentGenerationTask, ContentLayer
from app.modules.jobs import enqueue_durable
from app.services.batch_generation import BatchGenerationEngine, GenerationTaskSpec
from app.services.content_generation.source_context import (
    ContentGenerationSourceContextService,
    source_rows_for_chunks,
)
from app.services.llm_provider import build_provider_router

log = structlog.get_logger(__name__)
router = APIRouter(prefix="/admin/generation", tags=["generation"])


class StrictRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class TaskSpecRequest(StrictRequest):
    caps_ref: str = Field(..., pattern=r"^\d+\.[A-Z]+\.\d+(\.\d+)?$")
    content_type: Literal["diagnostic_item", "lesson"]
    count: int = Field(default=5, ge=1, le=20)
    language: str = Field(default="en", min_length=2, max_length=5)
    grade: int = Field(default=4, ge=0, le=12)
    subject: str = Field(default="Mathematics", min_length=1, max_length=120)
    subject_code: str = Field(default="MATHS", min_length=1, max_length=20)


class StartRunRequest(StrictRequest):
    scope_id: str = Field(..., min_length=1, max_length=80)
    task_specs: list[TaskSpecRequest] = Field(..., min_length=1, max_length=100)
    source_chunk_ids_by_caps_ref: dict[str, list[str]] = Field(default_factory=dict)


class RunResponse(BaseModel):
    run_id: str
    scope_id: str
    status: str
    requested_by: str | None
    provider: str | None
    run_metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime
    durable_job_id: str | None = None


class TaskResponse(BaseModel):
    task_id: str
    caps_ref: str | None
    content_layer: str
    status: str
    attempt_number: int
    provider: str | None
    model: str | None
    prompt_version: str | None
    token_usage: dict[str, Any] | None
    cost_metadata: dict[str, Any] | None
    validation_failures: list[str]
    output_artifact_ids: list[str]
    started_at: datetime | None
    finished_at: datetime | None
    created_at: datetime


def _get_engine() -> BatchGenerationEngine:
    return BatchGenerationEngine(provider_router=build_provider_router(get_settings()))


def _run_response(run: ContentGenerationRun, job_id: str | None = None) -> RunResponse:
    return RunResponse(
        run_id=str(run.run_id),
        scope_id=run.scope_id,
        status=run.status,
        requested_by=run.requested_by,
        provider=run.provider,
        run_metadata=run.run_metadata or {},
        created_at=run.created_at,
        updated_at=run.updated_at,
        durable_job_id=job_id,
    )


@router.post("/runs", response_model=RunResponse, status_code=status.HTTP_202_ACCEPTED)
async def start_generation_run(
    body: StartRunRequest,
    auth: AuthContext = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
    engine: BatchGenerationEngine = Depends(_get_engine),
) -> RunResponse:
    """Create and enqueue a run using only server-resolved approved sources."""
    context_service = ContentGenerationSourceContextService()
    sources_by_caps_ref: dict[str, list[dict[str, Any]]] = {}
    for spec in body.task_specs:
        if spec.caps_ref in sources_by_caps_ref:
            continue
        requested_ids = body.source_chunk_ids_by_caps_ref.get(spec.caps_ref)
        context = await context_service.build_context(
            db,
            scope_id=body.scope_id,
            caps_ref=spec.caps_ref,
            requested_chunk_ids=requested_ids,
        )
        if not context.passed:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "error": "source_provenance_failed",
                    "caps_ref": spec.caps_ref,
                    "errors": context.errors,
                },
            )
        sources_by_caps_ref[spec.caps_ref] = source_rows_for_chunks(
            context.chunks,
            caps_ref=spec.caps_ref,
            grade=spec.grade,
            subject_code=spec.subject_code,
            language=spec.language,
        )

    task_specs = [
        GenerationTaskSpec(
            caps_ref=spec.caps_ref,
            content_layer=(
                ContentLayer.DIAGNOSTIC_ITEMS
                if spec.content_type == "diagnostic_item"
                else ContentLayer.LESSONS
            ),
            content_type=spec.content_type,
            count=spec.count,
            language=spec.language,
            grade=spec.grade,
            subject=spec.subject,
            subject_code=spec.subject_code,
        )
        for spec in body.task_specs
    ]
    run = await engine.create_run(
        scope_id=body.scope_id,
        task_specs=task_specs,
        sources_by_caps_ref=sources_by_caps_ref,
        requested_by=auth.user_id,
        db=db,
    )

    # Set status to queued BEFORE enqueueing to prevent race condition.
    # Use conditional update to avoid overwriting terminal states (completed/failed).
    result = await db.execute(
        update(ContentGenerationRun)
        .where(
            ContentGenerationRun.run_id == run.run_id,
            ContentGenerationRun.status == "created",  # Only update if still in created state
        )
        .values(status="queued")
        .returning(ContentGenerationRun.status)
    )
    updated_status = result.scalar_one_or_none()
    if updated_status is None:
        # Run was already processed - fetch current state
        await db.refresh(run)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "run_already_processed",
                "run_id": str(run.run_id),
                "current_status": run.status,
            },
        )

    # Now enqueue the job - if this fails, set status to enqueue_failed
    try:
        durable_job_id = await enqueue_durable(
            "generate_content_batch",
            operation="content_generation_batch",
            payload={"run_id": str(run.run_id), "actor_id": auth.user_id},
            args=(str(run.run_id),),
        )
    except Exception as exc:
        # Revert to enqueue_failed on error
        await db.execute(
            update(ContentGenerationRun)
            .where(ContentGenerationRun.run_id == run.run_id)
            .values(
                status="enqueue_failed",
                run_metadata={
                    **(run.run_metadata or {}),
                    "enqueue_error_type": type(exc).__name__,
                },
            )
        )
        await db.commit()
        log.error(
            "generation_enqueue_failed",
            run_id=str(run.run_id),
            error_type=type(exc).__name__,
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": "generation_queue_unavailable",
                "run_id": str(run.run_id),
            },
        ) from exc

    # Store the job ID
    run.status = "queued"
    run.run_metadata = {**(run.run_metadata or {}), "durable_job_id": durable_job_id}
    await db.commit()
    return _run_response(run, durable_job_id)


@router.get("/runs/{run_id}", response_model=RunResponse)
async def get_generation_run(
    run_id: uuid.UUID,
    _auth: AuthContext = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> RunResponse:
    row = await db.execute(
        select(ContentGenerationRun).where(ContentGenerationRun.run_id == run_id)
    )
    run = row.scalar_one_or_none()
    if run is None:
        raise HTTPException(status_code=404, detail={"error": "run_not_found"})
    return _run_response(run, (run.run_metadata or {}).get("durable_job_id"))


@router.get("/runs/{run_id}/tasks", response_model=list[TaskResponse])
async def list_run_tasks(
    run_id: uuid.UUID,
    status_filter: str | None = Query(default=None, alias="status"),
    _auth: AuthContext = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> list[TaskResponse]:
    query = select(ContentGenerationTask).where(ContentGenerationTask.run_id == run_id)
    if status_filter:
        query = query.where(ContentGenerationTask.status == status_filter)
    rows = await db.execute(query.order_by(ContentGenerationTask.created_at))
    return [
        TaskResponse(
            task_id=str(task.task_id),
            caps_ref=task.caps_ref,
            content_layer=task.content_layer.value,
            status=task.status,
            attempt_number=task.attempt_number,
            provider=task.provider,
            model=task.model,
            prompt_version=task.prompt_version,
            token_usage=task.token_usage,
            cost_metadata=task.cost_metadata,
            validation_failures=task.validation_failures or [],
            output_artifact_ids=task.output_artifact_ids or [],
            started_at=task.started_at,
            finished_at=task.finished_at,
            created_at=task.created_at,
        )
        for task in rows.scalars().all()
    ]


@router.post("/runs/{run_id}/cancel")
async def cancel_generation_run(
    run_id: uuid.UUID,
    _auth: AuthContext = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    run_row = await db.execute(
        select(ContentGenerationRun).where(ContentGenerationRun.run_id == run_id)
    )
    if run_row.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail={"error": "run_not_found"})
    result = await db.execute(
        update(ContentGenerationTask)
        .where(
            ContentGenerationTask.run_id == run_id,
            ContentGenerationTask.status == "queued",
        )
        .values(status="abandoned")
        .returning(ContentGenerationTask.task_id)
    )
    cancelled = [str(value) for value in result.scalars().all()]
    await db.execute(
        update(ContentGenerationRun)
        .where(ContentGenerationRun.run_id == run_id)
        .values(status="cancelled")
    )
    await db.commit()
    return {"run_id": str(run_id), "cancelled_tasks": len(cancelled), "status": "cancelled"}
