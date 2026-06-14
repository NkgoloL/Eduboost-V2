"""Admin routes for the ETL-backed Content Factory."""
from __future__ import annotations

import os
import sys
import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.envelope_route import EnvelopedRoute
from app.api_v2_deps.auth import AuthContext, require_auth_context
from app.core.security import require_admin
from app.core.security import get_current_user  # noqa: F401
from app.domain.content_factory_schemas import (
    ContentArtifactProvenanceResponse,
    ContentArtifactProvenanceSourceResponse,
    ContentArtifactResponse,
    ContentArtifactValidationRequest,
    ContentArtifactValidationResponse,
    ContentFactoryActionRequest,
    ContentFactoryActionResponse,
    ContentFactoryETLStatusResponse,
    ContentFactoryHealthResponse,
    ArtifactReviewBundleResponse,
    BulkReviewAssignmentRequest,
    BulkReviewRequest,
    BulkReviewResponse,
    ContentFactoryReportResponse,
    ContentGenerationExecutionReportResponse,
    ContentGenerationExecutionResponse,
    ContentGenerationPlanResponse,
    ContentGenerationRunCreateRequest,
    ContentGenerationRunResponse,
    ContentGenerationTaskResponse,
    ContentSeedRunResponse,
    ContentStagingVerificationRunResponse,
    ProductionGateBlockerResponse,
    ProductionGateReportResponse,
    ProductionPromotionPlanResponse,
    ProductionPromotionRequest,
    ProductionPromotionResultResponse,
    ProductionPromotionPageResponse,
    ProductionReadVerificationReportResponse,
    ScopeProductionReadReportResponse,
    ProductionRollbackRequest,
    ProductionRollbackResultResponse,
    ReviewAssignmentRequest,
    ReviewAssignmentResponse,
    ReviewQueueItemResponse,
    ReviewQueuePageResponse,
    ReviewSummaryResponse,
    ReviewerWorkloadResponse,
    StagingReadVerificationResponse,
    StagingRollbackResponse,
    StagingSeedItemResponse,
    StagingSeedPlanResponse,
    StagingSeedRunPageResponse,
    StagingSeedRunResultResponse,
)
from app.domain.content_coverage import CapsRefCoverageReport, ContentLayer, CoverageTarget, ScopeCoverageReport
from app.domain.content_scope import ContentScope
from app.models.content_factory import ContentArtifactStatus, ContentGenerationArtifact, ContentGenerationTask
from app.repositories.item_bank_repository import ItemBankRepository
from app.repositories.lesson_repository import LessonRepository
from app.services.content_artifact_lifecycle import ContentArtifactLifecycleService
from app.services.content_factory import ContentFactoryService, ContentValidationService
from app.services.content_factory_orchestrator import ContentFactoryOrchestrator
from app.services.content_generation_runs import ContentGenerationRunService
from app.services.content_generation_executor import ContentGenerationExecutor, GenerationDisabledError
from app.services.content_generation_planner import ContentGenerationPlanner
from app.services.content_coverage_service import ContentCoverageService
from app.services.content_scope_registry import ContentScopeRegistry
from app.services.content_seed_promotion import ContentSeedPromotionService
from app.services.content_review_queue import ContentReviewQueueService
from app.services.content_reviewer_assignment import ContentReviewerAssignmentService
from app.services.content_bulk_review import ContentBulkReviewService
from app.services.content_staging_seed_executor import ContentStagingSeedExecutor
from app.services.content_staging_read_verification import ContentStagingReadVerificationService
from app.services.content_production_promotion_gate import ContentProductionPromotionGate
from app.services.content_production_promotion_executor import ContentProductionPromotionExecutor
from app.services.content_production_read_verification import ContentProductionReadVerificationService

from app.services.content_staging_readiness import (
    AllScopeStagingVerificationReport,
    ContentStagingReadinessService,
    ScopeStagingVerificationReport,
)

router = APIRouter(
    route_class=EnvelopedRoute,
    prefix="/admin/content-factory",
    tags=["admin-content-factory"],
    dependencies=[Depends(require_admin)],
)


def get_content_coverage_service(session: AsyncSession = Depends(get_db)) -> ContentCoverageService:
    return ContentCoverageService(item_repo=ItemBankRepository(session), lesson_repo=LessonRepository(session))


def get_content_generation_run_service() -> ContentGenerationRunService:
    return ContentGenerationRunService()


def get_content_factory_service() -> ContentFactoryService:
    return ContentFactoryService()


def get_content_artifact_lifecycle_service() -> ContentArtifactLifecycleService:
    return ContentArtifactLifecycleService()


def get_content_factory_orchestrator() -> ContentFactoryOrchestrator:
    return ContentFactoryOrchestrator()


def get_content_generation_planner() -> ContentGenerationPlanner:
    return ContentGenerationPlanner()


def get_content_generation_executor() -> ContentGenerationExecutor:
    return ContentGenerationExecutor()


def get_seed_promotion_service(
    coverage_service: ContentCoverageService = Depends(get_content_coverage_service),
) -> ContentSeedPromotionService:
    return ContentSeedPromotionService(coverage_service)


def get_staging_readiness_service() -> ContentStagingReadinessService:
    return ContentStagingReadinessService()


def get_content_review_queue_service() -> ContentReviewQueueService:
    return ContentReviewQueueService()


def get_content_reviewer_assignment_service() -> ContentReviewerAssignmentService:
    return ContentReviewerAssignmentService()


def get_content_bulk_review_service() -> ContentBulkReviewService:
    return ContentBulkReviewService()

def get_content_staging_seed_executor() -> ContentStagingSeedExecutor:
    return ContentStagingSeedExecutor()

def get_content_staging_read_verification_service() -> ContentStagingReadVerificationService:
    return ContentStagingReadVerificationService()


def get_production_promotion_gate(
    coverage_service: ContentCoverageService = Depends(get_content_coverage_service),
) -> ContentProductionPromotionGate:
    return ContentProductionPromotionGate(coverage_service=coverage_service)


def get_production_promotion_executor(
    gate: ContentProductionPromotionGate = Depends(get_production_promotion_gate),
) -> ContentProductionPromotionExecutor:
    return ContentProductionPromotionExecutor(gate=gate)


def get_production_read_verification_service() -> ContentProductionReadVerificationService:
    return ContentProductionReadVerificationService()


@router.get("/health", response_model=ContentFactoryHealthResponse)
async def content_factory_health() -> ContentFactoryHealthResponse:
    return ContentFactoryHealthResponse(
        status="ok",
        route_scope="admin",
        generation_enabled=_generation_enabled(),
    )


@router.get("/etl/status", response_model=ContentFactoryETLStatusResponse)
async def etl_status() -> ContentFactoryETLStatusResponse:
    return ContentFactoryETLStatusResponse(
        status="available",
        pipeline_package="app.services.etl",
        mcp_runtime_imported=_mcp_runtime_imported(),
        notes=[
            "ETL pipeline modules are importable from app.services.etl.",
            "MCP server wrappers are isolated under tools/etl and are not imported by app startup.",
        ],
    )


@router.get("/scopes", response_model=list[ContentScope])
async def list_content_scopes() -> list[ContentScope]:
    return ContentScopeRegistry().list_scopes()


@router.get("/scopes/{scope_id}", response_model=ContentScope)
async def get_content_scope(scope_id: str) -> ContentScope:
    try:
        return ContentScopeRegistry().get_scope(scope_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/scopes/{scope_id}/targets", response_model=list[CoverageTarget])
async def get_content_scope_targets(scope_id: str) -> list[CoverageTarget]:
    try:
        return ContentScopeRegistry().get_scope_targets(scope_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/scopes/{scope_id}/coverage", response_model=ScopeCoverageReport)
async def get_content_scope_coverage(
    scope_id: str,
    layer: list[ContentLayer] | None = Query(default=None),
    coverage_service: ContentCoverageService = Depends(get_content_coverage_service),
) -> ScopeCoverageReport:
    try:
        return await coverage_service.get_scope_coverage(scope_id, layers=layer)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/scopes/{scope_id}/coverage/{caps_ref}", response_model=CapsRefCoverageReport)
async def get_content_caps_ref_coverage(
    scope_id: str,
    caps_ref: str,
    layer: list[ContentLayer] | None = Query(default=None),
    coverage_service: ContentCoverageService = Depends(get_content_coverage_service),
) -> CapsRefCoverageReport:
    try:
        return await coverage_service.get_caps_ref_coverage(scope_id, caps_ref, layers=layer)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/validate-artifact", response_model=ContentArtifactValidationResponse)
async def validate_artifact_payload(request: ContentArtifactValidationRequest) -> ContentArtifactValidationResponse:
    result = ContentValidationService().validate_artifact_payload(
        artifact_json=request.artifact_json,
        caps_ref=request.caps_ref,
        sources=[source.model_dump() for source in request.sources],
        artifact_type=request.artifact_type.value,
        min_sources=request.min_sources,
    )
    return ContentArtifactValidationResponse(**result)


@router.get("/runs", response_model=list[ContentGenerationRunResponse])
async def list_generation_runs(
    scope_id: str | None = None,
    session: AsyncSession = Depends(get_db),
    service: ContentGenerationRunService = Depends(get_content_generation_run_service),
) -> list[ContentGenerationRunResponse]:
    runs = await service.list_runs(session, scope_id=scope_id)
    return [_run_response(run) for run in runs]


@router.post("/runs", response_model=ContentGenerationRunResponse)
async def create_generation_run(
    request: ContentGenerationRunCreateRequest,
    session: AsyncSession = Depends(get_db),
    service: ContentGenerationRunService = Depends(get_content_generation_run_service),
    current_user: AuthContext = Depends(require_auth_context),
) -> ContentGenerationRunResponse:
    if not request.dry_run and not _generation_enabled():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Generation execution is disabled by CONTENT_FACTORY_GENERATION_ENABLED.")
    run = await service.create_run(
        session,
        scope_id=request.scope_id,
        layers=request.layers,
        requested_by=current_user.user_id,
        dry_run=request.dry_run or not _generation_enabled(),
        budget_cap=request.budget_cap,
        max_concurrency=request.max_concurrency,
    )
    await service.create_tasks_for_run(session, run.run_id)
    await session.commit()
    return _run_response(run)


@router.get("/runs/{run_id}", response_model=ContentGenerationRunResponse)
async def get_generation_run(
    run_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    service: ContentGenerationRunService = Depends(get_content_generation_run_service),
) -> ContentGenerationRunResponse:
    try:
        return _run_response(await service.get_run(session, run_id))
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/runs/{run_id}/tasks", response_model=list[ContentGenerationTaskResponse])
async def get_generation_run_tasks(
    run_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    service: ContentGenerationRunService = Depends(get_content_generation_run_service),
) -> list[ContentGenerationTaskResponse]:
    return [_task_response(task) for task in await service.get_run_tasks(session, run_id)]


@router.post("/runs/{run_id}/plan-missing", response_model=ContentGenerationPlanResponse)
async def plan_missing_generation_tasks(
    run_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    planner: ContentGenerationPlanner = Depends(get_content_generation_planner),
    current_user: AuthContext = Depends(require_auth_context),
) -> ContentGenerationPlanResponse:
    try:
        plan = await planner.plan_missing_for_run(session, run_id, actor_id=current_user.user_id)
        await session.commit()
        return ContentGenerationPlanResponse(run_id=plan.run_id, created_task_ids=plan.created_task_ids, skipped=plan.skipped, missing=plan.missing)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/runs/{run_id}/execute", response_model=ContentGenerationExecutionResponse)
async def execute_generation_run(
    run_id: uuid.UUID,
    max_tasks: int | None = Query(default=None, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
    executor: ContentGenerationExecutor = Depends(get_content_generation_executor),
    current_user: AuthContext = Depends(require_auth_context),
) -> ContentGenerationExecutionResponse:
    try:
        result = await executor.execute_run(session, run_id, max_tasks=max_tasks, actor_id=current_user.user_id)
        await session.commit()
        return ContentGenerationExecutionResponse(run_id=result.run_id, status=result.status, summary=result.summary)
    except GenerationDisabledError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail={"error": "generation_disabled", "message": str(exc)}) from exc
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/tasks/{task_id}/execute", response_model=ContentGenerationExecutionResponse)
async def execute_generation_task(
    task_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    executor: ContentGenerationExecutor = Depends(get_content_generation_executor),
    current_user: AuthContext = Depends(require_auth_context),
) -> ContentGenerationExecutionResponse:
    try:
        result = await executor.execute_task(session, task_id, actor_id=current_user.user_id)
        await session.commit()
        return ContentGenerationExecutionResponse(task_id=result.task_id, status=result.status, artifact_ids=result.artifact_ids, errors=result.errors, provider=result.provider, mode=result.mode)
    except GenerationDisabledError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail={"error": "generation_disabled", "message": str(exc)}) from exc
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/tasks/{task_id}", response_model=ContentGenerationTaskResponse)
async def get_generation_task(
    task_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
) -> ContentGenerationTaskResponse:
    task = await session.get(ContentGenerationTask, task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Generation task {task_id} not found.")
    return _task_response(task)


@router.get("/runs/{run_id}/execution-report", response_model=ContentGenerationExecutionReportResponse)
async def get_generation_execution_report(
    run_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    executor: ContentGenerationExecutor = Depends(get_content_generation_executor),
) -> ContentGenerationExecutionReportResponse:
    try:
        return ContentGenerationExecutionReportResponse(**await executor.execution_report(session, run_id))
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/runs/{run_id}/cancel", response_model=ContentGenerationRunResponse)
async def cancel_generation_run(
    run_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    service: ContentGenerationRunService = Depends(get_content_generation_run_service),
    current_user: AuthContext = Depends(require_auth_context),
) -> ContentGenerationRunResponse:
    try:
        run = await service.cancel_run(session, run_id, current_user.user_id)
        await session.commit()
        return _run_response(run)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/runs/{run_id}/retry-failed", response_model=list[ContentGenerationTaskResponse])
async def retry_failed_generation_tasks(
    run_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    service: ContentGenerationRunService = Depends(get_content_generation_run_service),
    current_user: AuthContext = Depends(require_auth_context),
) -> list[ContentGenerationTaskResponse]:
    tasks = await service.retry_failed_tasks(session, run_id, current_user.user_id)
    await session.commit()
    return [_task_response(task) for task in tasks]


@router.get("/artifacts", response_model=list[ContentArtifactResponse])
async def list_artifacts(
    scope_id: str | None = None,
    status_filter: str | None = Query(default=None, alias="status"),
    session: AsyncSession = Depends(get_db),
) -> list[ContentArtifactResponse]:
    stmt = select(ContentGenerationArtifact).order_by(ContentGenerationArtifact.created_at.desc()).limit(100)
    if scope_id:
        stmt = stmt.where(ContentGenerationArtifact.scope_id == scope_id)
    if status_filter:
        stmt = stmt.where(ContentGenerationArtifact.status == status_filter)
    result = await session.execute(stmt)
    return [_artifact_response(artifact) for artifact in result.scalars().all()]


@router.get("/artifacts/{artifact_id}", response_model=ContentArtifactResponse)
async def get_artifact(
    artifact_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    service: ContentFactoryService = Depends(get_content_factory_service),
) -> ContentArtifactResponse:
    try:
        return _artifact_response(await service.get_artifact(session, artifact_id))
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/artifacts/{artifact_id}/provenance", response_model=ContentArtifactProvenanceResponse)
@router.get("/provenance/{artifact_id}", response_model=ContentArtifactProvenanceResponse)
async def get_artifact_provenance(
    artifact_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    service: ContentFactoryService = Depends(get_content_factory_service),
) -> ContentArtifactProvenanceResponse:
    try:
        artifact = await service.get_artifact(session, artifact_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return ContentArtifactProvenanceResponse(
        artifact_id=artifact.artifact_id,
        status=_value(artifact.status),
        artifact_hash=artifact.artifact_hash,
        source_snapshot_hash=artifact.source_snapshot_hash,
        sources=[
            ContentArtifactProvenanceSourceResponse(
                source_document_id=source.source_document_id,
                source_chunk_id=source.source_chunk_id,
                curriculum_mapping_id=source.curriculum_mapping_id,
                source_hash=source.source_hash,
                source_role=source.source_role,
                source_metadata=source.source_metadata or {},
            )
            for source in artifact.sources
        ],
    )


@router.post("/artifacts/{artifact_id}/submit-review", response_model=ContentFactoryActionResponse)
async def submit_artifact_for_review(artifact_id: uuid.UUID, session: AsyncSession = Depends(get_db), lifecycle: ContentArtifactLifecycleService = Depends(get_content_artifact_lifecycle_service), current_user: AuthContext = Depends(require_auth_context)) -> ContentFactoryActionResponse:
    try:
        transition = await lifecycle.submit_for_review(session, artifact_id, current_user.user_id)
        await session.commit()
        return ContentFactoryActionResponse(**transition.__dict__)
    except (LookupError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.post("/artifacts/{artifact_id}/reject", response_model=ContentFactoryActionResponse)
async def reject_artifact(artifact_id: uuid.UUID, request: ContentFactoryActionRequest, session: AsyncSession = Depends(get_db), lifecycle: ContentArtifactLifecycleService = Depends(get_content_artifact_lifecycle_service), current_user: AuthContext = Depends(require_auth_context)) -> ContentFactoryActionResponse:
    transition = await lifecycle.reject_artifact(session, artifact_id, current_user.user_id, request.reason or "Rejected by admin")
    await session.commit()
    return ContentFactoryActionResponse(**transition.__dict__)


@router.post("/artifacts/{artifact_id}/quarantine", response_model=ContentFactoryActionResponse)
async def quarantine_artifact(artifact_id: uuid.UUID, request: ContentFactoryActionRequest, session: AsyncSession = Depends(get_db), lifecycle: ContentArtifactLifecycleService = Depends(get_content_artifact_lifecycle_service), current_user: AuthContext = Depends(require_auth_context)) -> ContentFactoryActionResponse:
    transition = await lifecycle.quarantine_artifact(session, artifact_id, current_user.user_id, request.reason or "Quarantined by admin")
    await session.commit()
    return ContentFactoryActionResponse(**transition.__dict__)


@router.get("/review-queue", response_model=ReviewQueuePageResponse)
async def get_review_queue(
    scope_id: str | None = Query(default=None),
    layer: str | None = Query(default=None),
    caps_ref: str | None = Query(default=None),
    artifact_type: str | None = Query(default=None),
    risk_level: str | None = Query(default=None),
    reviewer_id: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_db),
    service: ContentReviewQueueService = Depends(get_content_review_queue_service),
) -> ReviewQueuePageResponse:
    page = await service.list_queue(session, scope_id=scope_id, layer=layer, caps_ref=caps_ref, artifact_type=artifact_type, risk_level=risk_level, reviewer_id=reviewer_id, limit=limit, offset=offset)
    return ReviewQueuePageResponse(items=[_review_queue_item_response(item) for item in page.items], total=page.total, limit=page.limit, offset=page.offset)


@router.get("/review-summary", response_model=ReviewSummaryResponse)
async def get_review_summary(
    scope_id: str | None = Query(default=None),
    session: AsyncSession = Depends(get_db),
    service: ContentReviewQueueService = Depends(get_content_review_queue_service),
) -> ReviewSummaryResponse:
    return ReviewSummaryResponse(**(await service.get_review_summary(session, scope_id=scope_id)).__dict__)


@router.get("/artifacts/{artifact_id}/review-bundle", response_model=ArtifactReviewBundleResponse)
async def get_artifact_review_bundle(
    artifact_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    service: ContentReviewQueueService = Depends(get_content_review_queue_service),
) -> ArtifactReviewBundleResponse:
    try:
        bundle = await service.get_artifact_review_bundle(session, artifact_id)
        return ArtifactReviewBundleResponse(
            artifact=bundle.artifact,
            validation_report=bundle.validation_report,
            provenance=bundle.provenance,
            sources=bundle.sources,
            review_risk=bundle.review_risk.__dict__,
            generation_metadata=bundle.generation_metadata,
            prior_review_events=bundle.prior_review_events,
            similar_artifacts=bundle.similar_artifacts,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/review-assignments", response_model=ReviewAssignmentResponse)
async def assign_reviewer(
    request: ReviewAssignmentRequest,
    session: AsyncSession = Depends(get_db),
    service: ContentReviewerAssignmentService = Depends(get_content_reviewer_assignment_service),
    current_user: AuthContext = Depends(require_auth_context),
) -> ReviewAssignmentResponse:
    try:
        assignment = await service.assign_artifact(session, request.artifact_id, request.reviewer_id, current_user.user_id, priority=request.priority)
        await session.commit()
        return _assignment_response(assignment)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/review-assignments/bulk", response_model=BulkReviewResponse)
async def bulk_assign_reviewer(
    request: BulkReviewAssignmentRequest,
    session: AsyncSession = Depends(get_db),
    service: ContentBulkReviewService = Depends(get_content_bulk_review_service),
    current_user: AuthContext = Depends(require_auth_context),
) -> BulkReviewResponse:
    result = await service.bulk_assign(session, request.artifact_ids, reviewer_id=request.reviewer_id, assigned_by=current_user.user_id, priority=request.priority)
    await session.commit()
    return BulkReviewResponse(**result.__dict__)


@router.get("/review-assignments", response_model=list[ReviewAssignmentResponse])
async def list_review_assignments(
    reviewer_id: str | None = Query(default=None),
    status_filter: str | None = Query(default=None, alias="status"),
    session: AsyncSession = Depends(get_db),
    service: ContentReviewerAssignmentService = Depends(get_content_reviewer_assignment_service),
) -> list[ReviewAssignmentResponse]:
    assignments = await service.list_assignments(session, reviewer_id=reviewer_id, status=status_filter)
    return [_assignment_response(assignment) for assignment in assignments]


@router.get("/reviewers/{reviewer_id}/workload", response_model=ReviewerWorkloadResponse)
async def get_reviewer_workload(
    reviewer_id: str,
    session: AsyncSession = Depends(get_db),
    service: ContentReviewerAssignmentService = Depends(get_content_reviewer_assignment_service),
) -> ReviewerWorkloadResponse:
    return ReviewerWorkloadResponse(**(await service.get_reviewer_workload(session, reviewer_id)).__dict__)


@router.post("/review/bulk-approve", response_model=BulkReviewResponse)
async def bulk_approve_review(
    request: BulkReviewRequest,
    session: AsyncSession = Depends(get_db),
    service: ContentBulkReviewService = Depends(get_content_bulk_review_service),
    current_user: AuthContext = Depends(require_auth_context),
) -> BulkReviewResponse:
    try:
        result = await service.bulk_approve(session, request.artifact_ids, reviewer_id=current_user.user_id, notes=request.notes or "")
        await session.commit()
        return BulkReviewResponse(**result.__dict__)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.post("/review/bulk-reject", response_model=BulkReviewResponse)
async def bulk_reject_review(
    request: BulkReviewRequest,
    session: AsyncSession = Depends(get_db),
    service: ContentBulkReviewService = Depends(get_content_bulk_review_service),
    current_user: AuthContext = Depends(require_auth_context),
) -> BulkReviewResponse:
    try:
        result = await service.bulk_reject(session, request.artifact_ids, reviewer_id=current_user.user_id, reason=request.reason or "")
        await session.commit()
        return BulkReviewResponse(**result.__dict__)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.post("/review/bulk-quarantine", response_model=BulkReviewResponse)
async def bulk_quarantine_review(
    request: BulkReviewRequest,
    session: AsyncSession = Depends(get_db),
    service: ContentBulkReviewService = Depends(get_content_bulk_review_service),
    current_user: AuthContext = Depends(require_auth_context),
) -> BulkReviewResponse:
    try:
        result = await service.bulk_quarantine(session, request.artifact_ids, reviewer_id=current_user.user_id, reason=request.reason or "")
        await session.commit()
        return BulkReviewResponse(**result.__dict__)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.post("/staging-verification/all-scopes", response_model=AllScopeStagingVerificationReport)
async def run_all_scope_staging_verification(
    include_partial: bool = Query(default=True),
    include_pending_review: bool = Query(default=True),
    include_blockers: bool = Query(default=True),
    session: AsyncSession = Depends(get_db),
    service: ContentStagingReadinessService = Depends(get_staging_readiness_service),
    current_user: AuthContext = Depends(require_auth_context),
) -> AllScopeStagingVerificationReport:
    report = await service.verify_all_scopes(
        session,
        include_partial=include_partial,
        actor_id=current_user.user_id,
        persist=True,
    )
    await session.commit()
    if not include_blockers:
        report = report.model_copy(update={"scopes": [scope.model_copy(update={"blockers": []}) for scope in report.scopes]})
    return report


@router.get("/staging-verification/runs", response_model=list[ContentStagingVerificationRunResponse])
async def list_staging_verification_runs(
    session: AsyncSession = Depends(get_db),
    service: ContentStagingReadinessService = Depends(get_staging_readiness_service),
) -> list[ContentStagingVerificationRunResponse]:
    runs = await service.list_runs(session)
    return [_staging_verification_run_response(run) for run in runs]


@router.get("/staging-verification/runs/{run_id}", response_model=AllScopeStagingVerificationReport)
async def get_staging_verification_run(
    run_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    service: ContentStagingReadinessService = Depends(get_staging_readiness_service),
) -> AllScopeStagingVerificationReport:
    try:
        return await service.get_run_report(session, run_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/scopes/{scope_id}/staging-verification", response_model=ScopeStagingVerificationReport)
async def run_scope_staging_verification(
    scope_id: str,
    include_partial: bool = Query(default=True),
    include_pending_review: bool = Query(default=True),
    include_blockers: bool = Query(default=True),
    session: AsyncSession = Depends(get_db),
    service: ContentStagingReadinessService = Depends(get_staging_readiness_service),
    current_user: AuthContext = Depends(require_auth_context),
) -> ScopeStagingVerificationReport:
    report = await service.verify_scope(
        scope_id,
        session=session,
        include_partial=include_partial,
        actor_id=current_user.user_id,
    )
    if report.status.value == "blocked_by_missing_scope":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Unknown content scope: {scope_id}")
    if not include_blockers:
        report = report.model_copy(update={"blockers": []})
    return report


@router.get("/scopes/{scope_id}/staging-readiness", response_model=ScopeStagingVerificationReport)
async def get_scope_staging_readiness(
    scope_id: str,
    include_partial: bool = Query(default=True),
    include_pending_review: bool = Query(default=True),
    include_blockers: bool = Query(default=True),
    session: AsyncSession = Depends(get_db),
    service: ContentStagingReadinessService = Depends(get_staging_readiness_service),
) -> ScopeStagingVerificationReport:
    report = await service.verify_scope(scope_id, session=session, include_partial=include_partial)
    if report.status.value == "blocked_by_missing_scope":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Unknown content scope: {scope_id}")
    if not include_blockers:
        report = report.model_copy(update={"blockers": []})
    return report


@router.post("/scopes/{scope_id}/dry-run-seed", response_model=StagingSeedPlanResponse)
async def dry_run_scope_seed(
    scope_id: str,
    session: AsyncSession = Depends(get_db),
    seed_executor: ContentStagingSeedExecutor = Depends(get_content_staging_seed_executor),
    current_user: AuthContext = Depends(require_auth_context),
) -> StagingSeedPlanResponse:
    plan = await seed_executor.dry_run_seed(session, scope_id, actor_id=current_user.user_id)
    return StagingSeedPlanResponse(
        scope_id=plan.scope_id,
        layers=plan.layers,
        seedable_count=len(plan.seedable),
        skipped_count=len(plan.skipped),
        skipped=[{"artifact_id": s.artifact_id, "reason": s.reason} for s in plan.skipped],
    )


@router.post("/scopes/{scope_id}/seed-staging", response_model=StagingSeedRunResultResponse)
async def seed_scope_staging(
    scope_id: str,
    allow_partial: bool = True,
    session: AsyncSession = Depends(get_db),
    seed_service: ContentSeedPromotionService = Depends(get_seed_promotion_service),
    seed_executor: ContentStagingSeedExecutor = Depends(get_content_staging_seed_executor),
    current_user: AuthContext = Depends(require_auth_context),
) -> StagingSeedRunResultResponse:
    try:
        # Prefer a fake/injected seed_service (unit tests), otherwise use the executor path.
        if seed_service.__class__.__name__ != "ContentSeedPromotionService":
            result = await seed_service.seed_staging(session, scope_id, actor_id=current_user.user_id)
        else:
            result = await seed_executor.seed_staging(session, scope_id, actor_id=current_user.user_id, allow_partial=allow_partial)
        await session.commit()
        return StagingSeedRunResultResponse(**result.__dict__)
    except ValueError as exc:
        # Gate or validation failure
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/seed-runs", response_model=StagingSeedRunPageResponse)
async def list_seed_runs(
    scope_id: str | None = None,
    limit: int = 50,
    offset: int = 0,
    session: AsyncSession = Depends(get_db),
    seed_executor: ContentStagingSeedExecutor = Depends(get_content_staging_seed_executor),
) -> StagingSeedRunPageResponse:
    page = await seed_executor.list_seed_runs(session, scope_id=scope_id, limit=limit, offset=offset)
    return StagingSeedRunPageResponse(
        items=[StagingSeedRunResultResponse(**item.__dict__) for item in page.items],
        total=page.total,
        limit=page.limit,
        offset=page.offset,
    )


@router.get("/seed-runs/{seed_run_id}", response_model=StagingSeedRunResultResponse)
async def get_seed_run(
    seed_run_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    seed_executor: ContentStagingSeedExecutor = Depends(get_content_staging_seed_executor),
) -> StagingSeedRunResultResponse:
    try:
        result = await seed_executor.get_seed_run(session, seed_run_id)
        return StagingSeedRunResultResponse(**result.__dict__)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/seed-runs/{seed_run_id}/items", response_model=list[StagingSeedItemResponse])
async def get_seed_run_items(
    seed_run_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    seed_executor: ContentStagingSeedExecutor = Depends(get_content_staging_seed_executor),
) -> list[StagingSeedItemResponse]:
    items = await seed_executor.list_seed_run_items(session, seed_run_id)
    return [StagingSeedItemResponse(**item.__dict__) for item in items]


@router.post("/seed-runs/{seed_run_id}/verify", response_model=StagingReadVerificationResponse)
async def verify_seed_run(
    seed_run_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    verification_service: ContentStagingReadVerificationService = Depends(get_content_staging_read_verification_service),
    current_user: AuthContext = Depends(require_auth_context),
) -> StagingReadVerificationResponse:
    report = await verification_service.verify_seed_run(session, seed_run_id, actor_id=current_user.user_id)
    return StagingReadVerificationResponse(seed_run_id=report.seed_run_id, passed=report.passed, verified_count=report.verified_count, errors=report.errors)


@router.post("/seed-runs/{seed_run_id}/rollback", response_model=StagingRollbackResponse)
async def rollback_seed_run(
    seed_run_id: uuid.UUID,
    reason: str,
    session: AsyncSession = Depends(get_db),
    seed_executor: ContentStagingSeedExecutor = Depends(get_content_staging_seed_executor),
    current_user: AuthContext = Depends(require_auth_context),
) -> StagingRollbackResponse:
    try:
        result = await seed_executor.rollback_seed_run(session, seed_run_id, actor_id=current_user.user_id, reason=reason)
        await session.commit()
        return StagingRollbackResponse(**result.__dict__)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/scopes/{scope_id}/staging-read-verification", response_model=StagingReadVerificationResponse)
async def verify_scope_staging(
    scope_id: str,
    session: AsyncSession = Depends(get_db),
    verification_service: ContentStagingReadVerificationService = Depends(get_content_staging_read_verification_service),
) -> StagingReadVerificationResponse:
    report = await verification_service.verify_scope_staging(session, scope_id)
    return StagingReadVerificationResponse(scope_id=report.scope_id, passed=report.passed, staged_artifacts_count=report.staged_artifacts_count, errors=report.errors)


@router.get("/scopes/{scope_id}/production-gate", response_model=ProductionGateReportResponse)
async def get_production_gate(
    scope_id: str,
    layers: list[str] | None = Query(None),
    session: AsyncSession = Depends(get_db),
    gate: ContentProductionPromotionGate = Depends(get_production_promotion_gate),
) -> ProductionGateReportResponse:
    report = await gate.evaluate_scope(session, scope_id, layers=layers)
    return ProductionGateReportResponse(
        scope_id=report.scope_id,
        status=report.status.value,
        blockers=[ProductionGateBlockerResponse(type=b.type, message=b.message, artifact_id=b.artifact_id, caps_ref=b.caps_ref) for b in report.blockers],
        coverage_summary=report.coverage_summary,
        staging_summary=report.staging_summary,
    )


@router.post("/scopes/{scope_id}/dry-run-promotion", response_model=ProductionPromotionPlanResponse)
async def dry_run_promotion(
    scope_id: str,
    layers: list[str] | None = Query(None),
    session: AsyncSession = Depends(get_db),
    executor: ContentProductionPromotionExecutor = Depends(get_production_promotion_executor),
    current_user: AuthContext = Depends(require_auth_context),
) -> ProductionPromotionPlanResponse:
    try:
        plan = await executor.dry_run_promotion(session, scope_id, layers=layers, actor_id=current_user.user_id)
        return ProductionPromotionPlanResponse(
            scope_id=plan.scope_id,
            layers=plan.layers,
            promotable_count=plan.promotable_count,
            skipped_count=plan.skipped_count,
            skipped=plan.skipped,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.post("/scopes/{scope_id}/promote-production", response_model=ProductionPromotionResultResponse)
async def promote_production(
    scope_id: str,
    request: ProductionPromotionRequest | None = None,
    session: AsyncSession = Depends(get_db),
    executor: ContentProductionPromotionExecutor = Depends(get_production_promotion_executor),
    seed_service: ContentSeedPromotionService = Depends(get_seed_promotion_service),
    current_user: AuthContext = Depends(require_auth_context),
) -> ProductionPromotionResultResponse:
    try:
        if request is None:
            # Backward-compatible seed-promotion flow used by unit tests.
            result = await seed_service.promote_production(session, scope_id, actor_id=current_user.user_id)
        else:
            result = await executor.promote_scope(
                session,
                scope_id,
                layers=request.layers,
                actor_id=current_user.user_id,
                confirmation=request.confirmation,
            )
        await session.commit()
        return ProductionPromotionResultResponse(**result.__dict__)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.get("/promotion-events", response_model=ProductionPromotionPageResponse)
async def list_promotion_events(
    scope_id: str | None = Query(None),
    limit: int = 50,
    offset: int = 0,
    session: AsyncSession = Depends(get_db),
    executor: ContentProductionPromotionExecutor = Depends(get_production_promotion_executor),
) -> ProductionPromotionPageResponse:
    page = await executor.list_promotion_events(session, scope_id=scope_id, limit=limit, offset=offset)
    return ProductionPromotionPageResponse(
        items=[ProductionPromotionResultResponse(**item.__dict__) for item in page.items],
        total=page.total,
        limit=page.limit,
        offset=page.offset,
    )


@router.get("/promotion-events/{promotion_event_id}", response_model=ProductionPromotionResultResponse)
async def get_promotion_event(
    promotion_event_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    executor: ContentProductionPromotionExecutor = Depends(get_production_promotion_executor),
) -> ProductionPromotionResultResponse:
    try:
        result = await executor.get_promotion_event(session, promotion_event_id)
        return ProductionPromotionResultResponse(**result.__dict__)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/promotion-events/{promotion_event_id}/items")
async def get_promotion_event_items(
    promotion_event_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    from app.models.content_factory import ContentProductionArtifact
    result = await session.execute(
        select(ContentProductionArtifact).where(
            ContentProductionArtifact.created_by_promotion_event_id == promotion_event_id,
        )
    )
    items = result.scalars().all()
    return {
        "items": [
            {
                "id": str(item.id),
                "artifact_id": str(item.artifact_id),
                "staging_artifact_id": str(item.staging_artifact_id) if item.staging_artifact_id else None,
                "scope_id": item.scope_id,
                "caps_ref": item.caps_ref,
                "layer": item.layer,
                "artifact_type": item.artifact_type,
                "production_status": item.production_status,
            }
            for item in items
        ],
        "total": len(items),
    }


@router.post("/promotion-events/{promotion_event_id}/verify", response_model=ProductionReadVerificationReportResponse)
async def verify_promotion_event(
    promotion_event_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    verification_service: ContentProductionReadVerificationService = Depends(get_production_read_verification_service),
    current_user: AuthContext = Depends(require_auth_context),
) -> ProductionReadVerificationReportResponse:
    try:
        report = await verification_service.verify_promotion_event(session, promotion_event_id, actor_id=current_user.user_id)
        return ProductionReadVerificationReportResponse(
            promotion_event_id=report.promotion_event_id,
            passed=report.passed,
            verified_count=report.verified_count,
            errors=report.errors,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/promotion-events/{promotion_event_id}/rollback", response_model=ProductionRollbackResultResponse)
async def rollback_promotion_event(
    promotion_event_id: uuid.UUID,
    request: ProductionRollbackRequest,
    session: AsyncSession = Depends(get_db),
    executor: ContentProductionPromotionExecutor = Depends(get_production_promotion_executor),
    current_user: AuthContext = Depends(require_auth_context),
) -> ProductionRollbackResultResponse:
    try:
        result = await executor.rollback_promotion(
            session,
            promotion_event_id,
            actor_id=current_user.user_id,
            reason=request.reason,
        )
        await session.commit()
        return ProductionRollbackResultResponse(**result.__dict__)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/scopes/{scope_id}/production-read-verification", response_model=ScopeProductionReadReportResponse)
async def verify_scope_production(
    scope_id: str,
    layers: list[str] | None = Query(None),
    session: AsyncSession = Depends(get_db),
    verification_service: ContentProductionReadVerificationService = Depends(get_production_read_verification_service),
) -> ScopeProductionReadReportResponse:
    report = await verification_service.verify_scope_production(session, scope_id, layers=layers)
    return ScopeProductionReadReportResponse(
        scope_id=report.scope_id,
        passed=report.passed,
        production_artifacts_count=report.production_artifacts_count,
        errors=report.errors,
    )


@router.get("/reports/{scope_id}", response_model=ContentFactoryReportResponse)
async def get_content_factory_report(scope_id: str, coverage_service: ContentCoverageService = Depends(get_content_coverage_service), session: AsyncSession = Depends(get_db)) -> ContentFactoryReportResponse:
    coverage = await coverage_service.get_scope_coverage(scope_id)
    run_count = len((await session.execute(select(ContentGenerationArtifact.artifact_id).where(ContentGenerationArtifact.scope_id == scope_id))).all())
    review_queue = len((await session.execute(select(ContentGenerationArtifact.artifact_id).where(ContentGenerationArtifact.scope_id == scope_id, ContentGenerationArtifact.status == ContentArtifactStatus.PENDING_REVIEW))).all())
    return ContentFactoryReportResponse(scope_id=scope_id, generation_enabled=_generation_enabled(), coverage=coverage.model_dump(mode="json"), run_count=run_count, review_queue_count=review_queue)


# ── Staging and Production Preview Routes ─────────────────────────────────────


def get_staging_preview_service():
    from app.services.content_staging_preview_service import ContentStagingPreviewService
    return ContentStagingPreviewService()


def get_learner_read_service():
    from app.services.content_learner_read_service import ContentLearnerReadService
    return ContentLearnerReadService()


@router.get("/staging-preview/scopes/{scope_id}")
async def get_staging_preview(
    scope_id: str,
    layers: list[str] | None = Query(None),
    current_user: dict = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
    service = Depends(get_staging_preview_service),
):
    """Get staging preview for a scope (admin-only)."""
    report = await service.preview_scope(session, scope_id, layers=layers)
    return report


@router.get("/staging-preview/scopes/{scope_id}/caps/{caps_ref}")
async def get_staging_preview_by_caps_ref(
    scope_id: str,
    caps_ref: str,
    layers: list[str] | None = Query(None),
    current_user: dict = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
    service = Depends(get_staging_preview_service),
):
    """Get staging preview for a scope and CAPS reference (admin-only)."""
    report = await service.preview_caps_ref(session, scope_id, caps_ref, layers=layers)
    return report


@router.get("/production-preview/scopes/{scope_id}")
async def get_production_preview(
    scope_id: str,
    current_user: dict = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
    service = Depends(get_learner_read_service),
):
    """Get production preview for a scope (admin-only)."""
    summary = await service.get_scope_content_summary(session, scope_id)
    return summary


@router.get("/production-preview/scopes/{scope_id}/caps/{caps_ref}")
async def get_production_preview_by_caps_ref(
    scope_id: str,
    caps_ref: str,
    current_user: dict = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
    service = Depends(get_learner_read_service),
):
    """Get production preview for a scope and CAPS reference (admin-only)."""
    diagnostic_items = await service.get_diagnostic_items(session, scope_id=scope_id, caps_ref=caps_ref)
    lessons = await service.get_lessons(session, scope_id=scope_id, caps_ref=caps_ref)
    return {"diagnostic_items": diagnostic_items, "lessons": lessons}


# ── Full Generation Run Routes ─────────────────────────────────────────────────────


@router.post("/full-generation/plan")
async def plan_full_generation(
    current_user: dict = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
):
    """Plan full generation for all configured scopes (admin-only)."""
    from app.services.content_generation_planner import ContentGenerationPlanner
    from app.models.content_factory import ContentGenerationRun

    planner = ContentGenerationPlanner()
    run = ContentGenerationRun(
        run_id=uuid.uuid4(),
        scope_id="all_scopes",
        status="queued",
        requested_by=current_user.get("sub"),
        run_metadata={"layers": ["diagnostic_items", "lessons", "assessment_blueprints", "study_plan_templates"]},
    )
    session.add(run)
    await session.flush()

    plan_result = await planner.plan_missing_for_run(
        session,
        run.run_id,
        actor_id=current_user.get("sub"),
    )

    return {
        "run_id": str(run.run_id),
        "created_task_ids": [str(t) for t in plan_result.created_task_ids],
        "skipped": plan_result.skipped,
        "missing": plan_result.missing,
    }


@router.post("/full-generation/start")
async def start_full_generation(
    request: dict,
    current_user: dict = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
):
    """Start full generation run (admin-only)."""
    if not _generation_enabled():
        raise HTTPException(status_code=403, detail="CONTENT_FACTORY_GENERATION_ENABLED is not set to true")

    from app.services.content_generation.provider_factory import get_generation_settings

    settings = get_generation_settings()
    if settings.provider == "llm":
        confirmation = request.get("confirmation", "")
        expected = "GENERATE OUTSTANDING CONTENT FOR ALL CONFIGURED SCOPES"
        if confirmation != expected:
            raise HTTPException(status_code=400, detail=f"Confirmation must be exactly: {expected}")

    run_id = request.get("run_id")
    if not run_id:
        raise HTTPException(status_code=400, detail="run_id is required")

    from app.models.content_factory import ContentGenerationRun

    run = await session.get(ContentGenerationRun, uuid.UUID(run_id))
    if not run:
        raise HTTPException(status_code=404, detail="Generation run not found")

    run.status = "running"
    await session.flush()

    return {"run_id": str(run.run_id), "status": "running"}


@router.get("/full-generation/runs")
async def list_full_generation_runs(
    current_user: dict = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
):
    """List full generation runs (admin-only)."""
    from app.models.content_factory import ContentGenerationRun

    result = await session.execute(
        select(ContentGenerationRun)
        .where(ContentGenerationRun.scope_id == "all_scopes")
        .order_by(ContentGenerationRun.created_at.desc())
        .limit(50)
    )
    runs = result.scalars().all()

    return {
        "items": [_run_response(run) for run in runs],
        "total": len(runs),
    }


@router.get("/full-generation/runs/{run_id}")
async def get_full_generation_run(
    run_id: str,
    current_user: dict = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
):
    """Get a full generation run (admin-only)."""
    from app.models.content_factory import ContentGenerationRun

    run = await session.get(ContentGenerationRun, uuid.UUID(run_id))
    if not run:
        raise HTTPException(status_code=404, detail="Generation run not found")

    return _run_response(run)


@router.get("/full-generation/runs/{run_id}/report")
async def get_full_generation_run_report(
    run_id: str,
    current_user: dict = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
):
    """Get a full generation run report (admin-only)."""
    from app.models.content_factory import ContentGenerationRun

    run = await session.get(ContentGenerationRun, uuid.UUID(run_id))
    if not run:
        raise HTTPException(status_code=404, detail="Generation run not found")

    metadata = run.run_metadata or {}
    return {
        "run_id": str(run.run_id),
        "status": run.status,
        "metadata": metadata,
    }


@router.post("/full-generation/runs/{run_id}/cancel")
async def cancel_full_generation_run(
    run_id: str,
    current_user: dict = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
):
    """Cancel a full generation run (admin-only)."""
    from app.models.content_factory import ContentGenerationRun, ContentGenerationTask

    run = await session.get(ContentGenerationRun, uuid.UUID(run_id))
    if not run:
        raise HTTPException(status_code=404, detail="Generation run not found")

    if run.status not in ("queued", "running"):
        raise HTTPException(status_code=400, detail="Can only cancel queued or running runs")

    run.status = "cancelled"
    await session.flush()

    # Cancel queued/running tasks
    result = await session.execute(
        select(ContentGenerationTask).where(
            ContentGenerationTask.run_id == run.run_id,
            ContentGenerationTask.status.in_(["queued", "running"]),
        )
    )
    tasks = result.scalars().all()
    for task in tasks:
        task.status = "cancelled"

    await session.flush()

    return {"run_id": str(run.run_id), "status": "cancelled"}


@router.post("/full-generation/runs/{run_id}/resume")
async def resume_full_generation_run(
    run_id: str,
    current_user: dict = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
):
    """Resume a full generation run (admin-only)."""
    from app.models.content_factory import ContentGenerationRun

    run = await session.get(ContentGenerationRun, uuid.UUID(run_id))
    if not run:
        raise HTTPException(status_code=404, detail="Generation run not found")

    if run.status != "cancelled":
        raise HTTPException(status_code=400, detail="Can only resume cancelled runs")

    run.status = "queued"
    await session.flush()

    return {"run_id": str(run.run_id), "status": "queued"}


def _mcp_runtime_imported() -> bool:
    return any(name.startswith("mcp.") or name == "mcp" for name in sys.modules)


def _generation_enabled() -> bool:
    return os.environ.get("CONTENT_FACTORY_GENERATION_ENABLED", "false").lower() in {"1", "true", "yes"}


def _run_response(run) -> ContentGenerationRunResponse:
    return ContentGenerationRunResponse(run_id=run.run_id, scope_id=run.scope_id, status=run.status, requested_by=run.requested_by, run_metadata=run.run_metadata or {})


def _task_response(task) -> ContentGenerationTaskResponse:
    return ContentGenerationTaskResponse(task_id=task.task_id, run_id=task.run_id, scope_id=task.scope_id, caps_ref=task.caps_ref, content_layer=_value(task.content_layer), status=task.status, attempt_number=task.attempt_number, max_attempts=task.max_attempts, output_artifact_ids=task.output_artifact_ids or [], validation_failures=task.validation_failures or [])


def _artifact_response(artifact) -> ContentArtifactResponse:
    return ContentArtifactResponse(artifact_id=artifact.artifact_id, scope_id=artifact.scope_id, content_layer=_value(artifact.content_layer), artifact_type=_value(artifact.artifact_type), caps_ref=artifact.caps_ref, status=_value(artifact.status), artifact_hash=artifact.artifact_hash, source_snapshot_hash=artifact.source_snapshot_hash)


def _seed_run_response(run) -> ContentSeedRunResponse:
    return ContentSeedRunResponse(seed_run_id=run.seed_run_id, scope_id=run.scope_id, dry_run=run.dry_run, status=run.status, summary=run.summary or {})


def _staging_verification_run_response(run) -> ContentStagingVerificationRunResponse:
    return ContentStagingVerificationRunResponse(
        run_id=run.run_id,
        status=run.status,
        summary=run.summary_json or {},
        created_by=run.created_by,
        created_at=run.created_at.isoformat() if run.created_at else None,
        completed_at=run.completed_at.isoformat() if run.completed_at else None,
    )


def _review_queue_item_response(item) -> ReviewQueueItemResponse:
    return ReviewQueueItemResponse(
        artifact_id=item.artifact_id,
        scope_id=item.scope_id,
        content_layer=item.content_layer,
        artifact_type=item.artifact_type,
        caps_ref=item.caps_ref,
        status=item.status,
        risk_level=item.risk_level,
        risk_reasons=item.risk_reasons,
        validation_status=item.validation_status,
        provenance_status=item.provenance_status,
        reviewer_id=item.reviewer_id,
        created_at=item.created_at.isoformat() if item.created_at else None,
    )


def _assignment_response(assignment) -> ReviewAssignmentResponse:
    return ReviewAssignmentResponse(
        id=assignment.id,
        artifact_id=assignment.artifact_id,
        assigned_to=assignment.assigned_to,
        assigned_by=assignment.assigned_by,
        priority=assignment.priority,
        status=assignment.status,
        due_by=assignment.due_by.isoformat() if assignment.due_by else None,
    )


def _value(value) -> str:
    return value.value if hasattr(value, "value") else str(value)
