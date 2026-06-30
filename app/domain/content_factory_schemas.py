"""Pydantic schemas for Content Factory admin routes."""
from __future__ import annotations

import uuid
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.content_factory import ContentArtifactType, ContentLayer, ContentReviewAction


class ETLSourceCitation(BaseModel):
    model_config = ConfigDict(extra="allow")

    source_document_id: str
    source_chunk_id: str | None = None
    curriculum_mapping_id: str | None = None
    source_hash: str | None = None
    source_role: str = "primary_context"
    caps_ref: str | None = None
    document_status: str | None = None
    license_status: str | None = None
    chunk_quality_score: float | None = None


class SourceBundleValidationRequest(BaseModel):
    caps_ref: str | None = None
    min_sources: int = Field(default=1, ge=0, le=20)
    require_approved_documents: bool = True
    allow_synthetic_without_source: bool = False
    sources: list[ETLSourceCitation] = Field(default_factory=list)


class SourceBundleValidationResponse(BaseModel):
    passed: bool
    errors: list[str]
    source_snapshot_hash: str | None


class ContentFactoryHealthResponse(BaseModel):
    status: str
    route_scope: str
    generation_enabled: bool = False


class ContentFactoryETLStatusResponse(BaseModel):
    status: str
    pipeline_package: str
    mcp_runtime_imported: bool
    notes: list[str] = Field(default_factory=list)


class ContentArtifactCreate(BaseModel):
    scope_id: str
    content_layer: ContentLayer
    artifact_type: ContentArtifactType
    artifact_json: dict[str, Any]
    caps_ref: str | None = None
    grade: int | None = Field(default=None, ge=0, le=12)
    subject_code: str | None = None
    language: str | None = "en"
    schema_version: str = "1.0"
    provider: str | None = None
    model: str | None = None
    prompt_version: str | None = None
    token_usage: dict[str, Any] | None = None
    cost_metadata: dict[str, Any] | None = None
    quality_score: float | None = Field(default=None, ge=0, le=1)
    safety_status: str | None = "passed"
    answer_key_verified: bool = False
    caps_alignment_score: float | None = Field(default=None, ge=0, le=1)
    min_sources: int = Field(default=1, ge=0, le=20)
    sources: list[ETLSourceCitation] = Field(default_factory=list)


class ContentArtifactValidationRequest(BaseModel):
    artifact_type: ContentArtifactType
    artifact_json: dict[str, Any]
    caps_ref: str | None = None
    min_sources: int = Field(default=1, ge=0, le=20)
    sources: list[ETLSourceCitation] = Field(default_factory=list)


class ContentArtifactResponse(BaseModel):
    artifact_id: uuid.UUID
    scope_id: str
    content_layer: str
    artifact_type: str
    caps_ref: str | None
    status: str
    artifact_hash: str
    source_snapshot_hash: str | None


class ContentValidationReportResponse(BaseModel):
    validation_report_id: uuid.UUID
    artifact_id: uuid.UUID
    passed: bool
    checks: dict[str, Any]
    errors: list[str]


class ContentArtifactValidationResponse(BaseModel):
    passed: bool
    checks: dict[str, Any]
    errors: list[str]
    source_snapshot_hash: str | None


class ContentArtifactProvenanceSourceResponse(BaseModel):
    source_document_id: str
    source_chunk_id: str | None
    curriculum_mapping_id: str | None
    source_hash: str | None
    source_role: str
    source_metadata: dict[str, Any]


class ContentArtifactProvenanceResponse(BaseModel):
    artifact_id: uuid.UUID
    status: str
    artifact_hash: str
    source_snapshot_hash: str | None
    sources: list[ContentArtifactProvenanceSourceResponse]


class ContentArtifactReviewRequest(BaseModel):
    review_action: ContentReviewAction
    review_reason: str | None = None
    quality_score: float | None = Field(default=None, ge=0, le=1)


class ContentArtifactReviewResponse(BaseModel):
    review_id: uuid.UUID
    artifact_id: uuid.UUID
    review_action: str
    reviewer_id: str | None

class ContentGenerationRunCreateRequest(BaseModel):
    scope_id: str
    layers: list[ContentLayer] = Field(default_factory=lambda: [ContentLayer.DIAGNOSTIC_ITEMS, ContentLayer.LESSONS])
    dry_run: bool = True
    budget_cap: float | None = Field(default=None, ge=0)
    max_concurrency: int = Field(default=1, ge=1, le=20)


class ContentGenerationRunResponse(BaseModel):
    run_id: uuid.UUID
    scope_id: str
    status: str
    requested_by: str | None = None
    run_metadata: dict[str, Any] = Field(default_factory=dict)


class ContentGenerationTaskResponse(BaseModel):
    task_id: uuid.UUID
    run_id: uuid.UUID
    scope_id: str
    caps_ref: str | None
    content_layer: str
    status: str
    attempt_number: int = 1
    max_attempts: int = 3
    output_artifact_ids: list[str] = Field(default_factory=list)
    validation_failures: list[str] = Field(default_factory=list)


class ContentGenerationPlanResponse(BaseModel):
    run_id: uuid.UUID
    created_task_ids: list[uuid.UUID] = Field(default_factory=list)
    skipped: list[dict[str, Any]] = Field(default_factory=list)
    missing: list[dict[str, Any]] = Field(default_factory=list)


class ContentGenerationExecutionResponse(BaseModel):
    run_id: uuid.UUID | None = None
    task_id: uuid.UUID | None = None
    status: str
    artifact_ids: list[uuid.UUID] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    summary: dict[str, Any] = Field(default_factory=dict)
    provider: str | None = None
    mode: str | None = None


class ContentGenerationExecutionReportResponse(BaseModel):
    run_id: str
    status: str
    tasks: int
    queued: int
    succeeded: int
    failed: int
    skipped: int
    artifacts: int


class ContentFactoryActionRequest(BaseModel):
    reason: str | None = None
    notes: str | None = None


class ContentFactoryActionResponse(BaseModel):
    artifact_id: uuid.UUID | None = None
    previous_status: str | None = None
    new_status: str | None = None
    status: str | None = None
    errors: list[str] = Field(default_factory=list)
    summary: dict[str, Any] = Field(default_factory=dict)


class ContentSeedRunResponse(BaseModel):
    seed_run_id: uuid.UUID
    scope_id: str
    dry_run: bool
    status: str
    summary: dict[str, Any] = Field(default_factory=dict)


class StagingSeedSkippedArtifactResponse(BaseModel):
    artifact_id: uuid.UUID
    reason: str


class StagingSeedPlanResponse(BaseModel):
    scope_id: str
    layers: list[str] = Field(default_factory=list)
    seedable_count: int
    skipped_count: int
    skipped: list[StagingSeedSkippedArtifactResponse] = Field(default_factory=list)


class StagingSeedRunResultResponse(BaseModel):
    seed_run_id: uuid.UUID
    scope_id: str
    status: str
    seeded_count: int
    skipped_count: int
    errors: list[str] = Field(default_factory=list)


class StagingSeedRunPageResponse(BaseModel):
    items: list[StagingSeedRunResultResponse] = Field(default_factory=list)
    total: int
    limit: int
    offset: int


class StagingSeedItemResponse(BaseModel):
    id: uuid.UUID
    seed_run_id: uuid.UUID
    artifact_id: uuid.UUID
    scope_id: str
    caps_ref: str | None = None
    layer: str
    artifact_type: str
    target_table: str
    target_record_id: str | None = None
    status: str
    skip_reason: str | None = None
    seed_payload_hash: str | None = None


class StagingReadVerificationResponse(BaseModel):
    seed_run_id: uuid.UUID | None = None
    scope_id: str | None = None
    passed: bool
    verified_count: int | None = None
    staged_artifacts_count: int | None = None
    errors: list[str] = Field(default_factory=list)


class StagingRollbackResponse(BaseModel):
    seed_run_id: uuid.UUID
    status: str
    rolled_back_count: int


class ProductionGateBlockerResponse(BaseModel):
    type: str
    message: str
    artifact_id: uuid.UUID | None = None
    caps_ref: str | None = None


class ProductionGateReportResponse(BaseModel):
    scope_id: str
    status: str
    blockers: list[ProductionGateBlockerResponse] = Field(default_factory=list)
    coverage_summary: dict[str, Any] = Field(default_factory=dict)
    staging_summary: dict[str, Any] = Field(default_factory=dict)


class ProductionPromotionPlanResponse(BaseModel):
    scope_id: str
    layers: list[str]
    promotable_count: int
    skipped_count: int
    skipped: list[dict[str, Any]] = Field(default_factory=list)


class ProductionPromotionRequest(BaseModel):
    layers: list[str] | None = None
    confirmation: str = Field(min_length=1)


class ProductionPromotionResultResponse(BaseModel):
    promotion_event_id: uuid.UUID
    scope_id: str
    status: str
    promoted_count: int
    skipped_count: int
    errors: list[str] = Field(default_factory=list)


class ProductionPromotionPageResponse(BaseModel):
    items: list[ProductionPromotionResultResponse] = Field(default_factory=list)
    total: int
    limit: int
    offset: int


class ProductionReadVerificationReportResponse(BaseModel):
    promotion_event_id: uuid.UUID
    passed: bool
    verified_count: int
    errors: list[str] = Field(default_factory=list)


class ScopeProductionReadReportResponse(BaseModel):
    scope_id: str
    passed: bool
    production_artifacts_count: int
    errors: list[str] = Field(default_factory=list)


class ProductionRollbackRequest(BaseModel):
    reason: str


class ProductionRollbackResultResponse(BaseModel):
    promotion_event_id: uuid.UUID
    status: str
    rolled_back_count: int


class ContentFactoryReportResponse(BaseModel):
    scope_id: str
    generation_enabled: bool
    coverage: dict[str, Any]
    run_count: int
    review_queue_count: int


class ReviewRiskResponse(BaseModel):
    level: str
    score: int = 0
    reasons: list[str] = Field(default_factory=list)


class ReviewQueueItemResponse(BaseModel):
    artifact_id: uuid.UUID
    scope_id: str
    content_layer: str
    artifact_type: str
    caps_ref: str | None = None
    status: str
    risk_level: str
    risk_reasons: list[str] = Field(default_factory=list)
    validation_status: str
    provenance_status: str
    reviewer_id: str | None = None
    created_at: str | None = None


class ReviewQueuePageResponse(BaseModel):
    items: list[ReviewQueueItemResponse]
    total: int
    limit: int
    offset: int


class ReviewSummaryResponse(BaseModel):
    pending_review: int = 0
    low_risk: int = 0
    medium_risk: int = 0
    high_risk: int = 0
    critical_risk: int = 0
    assigned: int = 0


class ArtifactReviewBundleResponse(BaseModel):
    artifact: dict[str, Any]
    validation_report: dict[str, Any] | None = None
    provenance: dict[str, Any]
    sources: list[dict[str, Any]] = Field(default_factory=list)
    review_risk: ReviewRiskResponse
    generation_metadata: dict[str, Any] = Field(default_factory=dict)
    prior_review_events: list[dict[str, Any]] = Field(default_factory=list)
    similar_artifacts: list[dict[str, Any]] = Field(default_factory=list)


class ReviewAssignmentRequest(BaseModel):
    artifact_id: uuid.UUID
    reviewer_id: str
    priority: str = "normal"


class BulkReviewAssignmentRequest(BaseModel):
    artifact_ids: list[uuid.UUID] = Field(default_factory=list, min_length=1)
    reviewer_id: str
    priority: str = "normal"


class ReviewAssignmentResponse(BaseModel):
    id: uuid.UUID
    artifact_id: uuid.UUID
    assigned_to: str
    assigned_by: str
    priority: str
    status: str
    due_by: str | None = None


class ReviewerWorkloadResponse(BaseModel):
    reviewer_id: str
    assigned: int
    in_review: int
    overdue: int
    total_open: int


class BulkReviewRequest(BaseModel):
    artifact_ids: list[uuid.UUID] = Field(default_factory=list, min_length=1)
    reason: str | None = None
    notes: str | None = None


class BulkReviewResponse(BaseModel):
    status: str
    artifact_ids: list[uuid.UUID] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    summary: dict[str, int] = Field(default_factory=dict)


class ContentStagingVerificationRunResponse(BaseModel):
    run_id: uuid.UUID
    status: str
    summary: dict[str, Any] = Field(default_factory=dict)
    created_by: str | None = None
    created_at: str | None = None
    completed_at: str | None = None
