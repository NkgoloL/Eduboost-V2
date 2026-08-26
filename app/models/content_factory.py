"""Content Factory ORM models.

These tables govern generated learner-facing artifacts. Source document
governance remains in the ETL pipeline; these records only keep the generated
content lifecycle and its provenance links.
"""
from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ContentScopeStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    RETIRED = "retired"


class ContentArtifactStatus(str, enum.Enum):
    DRAFT = "draft"
    GENERATED = "generated"
    VALIDATION_FAILED = "validation_failed"
    PENDING_REVIEW = "pending_review"
    REVISION_REQUIRED = "revision_required"
    APPROVED = "approved"
    PUBLISHED = "published"
    SUPERSEDED = "superseded"
    SEEDED_STAGING = "seeded_staging"
    PROMOTED_PRODUCTION = "promoted_production"
    RETIRED = "retired"
    REJECTED = "rejected"
    QUARANTINED = "quarantined"
    GENERATION_FAILED = "generation_failed"


class ContentLayer(str, enum.Enum):
    DIAGNOSTIC_ITEMS = "diagnostic_items"
    LESSONS = "lessons"
    ASSESSMENT_BLUEPRINTS = "assessment_blueprints"
    STUDY_PLAN_TEMPLATES = "study_plan_templates"


class ContentArtifactType(str, enum.Enum):
    DIAGNOSTIC_ITEM = "diagnostic_item"
    LESSON = "lesson"
    ASSESSMENT_BLUEPRINT = "assessment_blueprint"
    STUDY_PLAN_TEMPLATE = "study_plan_template"
    RUBRIC = "rubric"
    REMEDIATION_PATH = "remediation_path"


class ContentReviewAction(str, enum.Enum):
    APPROVE = "approve"
    REJECT = "reject"
    QUARANTINE = "quarantine"
    REQUEST_CHANGES = "request_changes"


class ContentScope(Base):
    __tablename__ = "content_scopes"

    scope_id: Mapped[str] = mapped_column(String(80), primary_key=True)
    grade: Mapped[int] = mapped_column(Integer, nullable=False)
    subject_code: Mapped[str] = mapped_column(String(20), nullable=False)
    subject_slug: Mapped[str] = mapped_column(String(80), nullable=False)
    subject_display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    language: Mapped[str] = mapped_column(String(8), nullable=False, server_default="en")
    curriculum: Mapped[str] = mapped_column(String(40), nullable=False, server_default="CAPS")
    status: Mapped[ContentScopeStatus] = mapped_column(
        Enum(ContentScopeStatus, name="content_scope_status", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        server_default=ContentScopeStatus.ACTIVE.value,
    )
    source_policy: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    targets: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        CheckConstraint("grade >= 0 AND grade <= 12", name="ck_content_scopes_grade_range"),
        Index("ix_content_scopes_grade_subject_language", "grade", "subject_code", "language"),
    )


class ContentCoverageTarget(Base):
    __tablename__ = "content_coverage_targets"

    target_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid())
    scope_id: Mapped[str] = mapped_column(ForeignKey("content_scopes.scope_id", ondelete="CASCADE"), nullable=False)
    caps_ref: Mapped[str] = mapped_column(String(80), nullable=False)
    content_layer: Mapped[ContentLayer] = mapped_column(
        Enum(ContentLayer, name="content_layer", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    target_count: Mapped[int] = mapped_column(Integer, nullable=False)
    minimum_approved_sources: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        CheckConstraint("target_count >= 0", name="ck_content_coverage_targets_count_non_negative"),
        UniqueConstraint("scope_id", "caps_ref", "content_layer", name="uq_content_coverage_target_scope_caps_layer"),
    )


class ContentGenerationRun(Base):
    __tablename__ = "content_generation_runs"

    run_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid())
    scope_id: Mapped[str] = mapped_column(ForeignKey("content_scopes.scope_id"), nullable=False)
    requested_by: Mapped[str | None] = mapped_column(String(80), nullable=True)
    status: Mapped[str] = mapped_column(String(40), nullable=False, server_default="draft")
    provider: Mapped[str | None] = mapped_column(String(80), nullable=True)
    model: Mapped[str | None] = mapped_column(String(120), nullable=True)
    prompt_version: Mapped[str | None] = mapped_column(String(80), nullable=True)
    run_metadata: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())


class ContentGenerationTask(Base):
    __tablename__ = "content_generation_tasks"

    task_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid())
    run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("content_generation_runs.run_id", ondelete="CASCADE"), nullable=False)
    scope_id: Mapped[str] = mapped_column(String(80), nullable=False)
    caps_ref: Mapped[str | None] = mapped_column(String(80), nullable=True)
    content_layer: Mapped[ContentLayer] = mapped_column(
        Enum(ContentLayer, name="content_layer", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(String(40), nullable=False, server_default="queued")
    attempt_number: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
    max_attempts: Mapped[int] = mapped_column(Integer, nullable=False, server_default="3")
    idempotency_key: Mapped[str | None] = mapped_column(String(160), nullable=True, unique=True)
    depends_on_task_ids: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    input_artifact_ids: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    output_artifact_ids: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    provider: Mapped[str | None] = mapped_column(String(80), nullable=True)
    model: Mapped[str | None] = mapped_column(String(120), nullable=True)
    prompt_version: Mapped[str | None] = mapped_column(String(80), nullable=True)
    token_usage: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    cost_metadata: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    validation_failures: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    artifact_paths: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    locked_by: Mapped[str | None] = mapped_column(String(120), nullable=True)
    lock_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    admin_actor_id: Mapped[str | None] = mapped_column(String(80), nullable=True)
    task_metadata: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    __table_args__ = (Index("ix_content_generation_tasks_run_status", "run_id", "status"),)


class ContentGenerationArtifact(Base):
    __tablename__ = "content_generation_artifacts"

    artifact_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid())
    run_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("content_generation_runs.run_id"), nullable=True)
    task_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("content_generation_tasks.task_id"), nullable=True)
    scope_id: Mapped[str] = mapped_column(String(80), nullable=False)
    content_layer: Mapped[ContentLayer] = mapped_column(
        Enum(ContentLayer, name="content_layer", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    artifact_type: Mapped[ContentArtifactType] = mapped_column(
        Enum(ContentArtifactType, name="content_artifact_type", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    caps_ref: Mapped[str | None] = mapped_column(String(80), nullable=True)
    grade: Mapped[int | None] = mapped_column(Integer, nullable=True)
    subject_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    language: Mapped[str | None] = mapped_column(String(8), nullable=True)
    status: Mapped[ContentArtifactStatus] = mapped_column(
        Enum(ContentArtifactStatus, name="content_artifact_status", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        server_default=ContentArtifactStatus.GENERATED.value,
        index=True,
    )
    artifact_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    artifact_hash: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)
    schema_version: Mapped[str] = mapped_column(String(40), nullable=False, server_default="1.0")
    source_snapshot_hash: Mapped[str | None] = mapped_column(String(120), nullable=True)
    root_artifact_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("content_generation_artifacts.artifact_id", ondelete="RESTRICT"), nullable=True
    )
    supersedes_artifact_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("content_generation_artifacts.artifact_id", ondelete="RESTRICT"), nullable=True
    )
    superseded_by_artifact_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("content_generation_artifacts.artifact_id", ondelete="RESTRICT"), nullable=True
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
    row_version: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
    created_by_actor_id: Mapped[str | None] = mapped_column(String(80), nullable=True)
    approval_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    review_policy_version: Mapped[str] = mapped_column(String(40), nullable=False, server_default="phase3-v1")
    rubric_version: Mapped[str] = mapped_column(String(40), nullable=False, server_default="1.0")
    publication_eligible: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    provider: Mapped[str | None] = mapped_column(String(80), nullable=True)
    model: Mapped[str | None] = mapped_column(String(120), nullable=True)
    prompt_version: Mapped[str | None] = mapped_column(String(80), nullable=True)
    token_usage: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    cost_metadata: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    quality_score: Mapped[float | None] = mapped_column(Numeric(precision=5, scale=4), nullable=True)
    safety_status: Mapped[str | None] = mapped_column(String(40), nullable=True)
    answer_key_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    caps_alignment_score: Mapped[float | None] = mapped_column(Numeric(precision=5, scale=4), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    sources: Mapped[list["ContentArtifactSource"]] = relationship("ContentArtifactSource", back_populates="artifact", cascade="all, delete-orphan")
    reviews: Mapped[list["ContentArtifactReview"]] = relationship("ContentArtifactReview", back_populates="artifact", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("grade IS NULL OR (grade >= 0 AND grade <= 12)", name="ck_content_artifacts_grade_range"),
        CheckConstraint("quality_score IS NULL OR (quality_score >= 0 AND quality_score <= 1)", name="ck_content_artifacts_quality_range"),
        CheckConstraint("caps_alignment_score IS NULL OR (caps_alignment_score >= 0 AND caps_alignment_score <= 1)", name="ck_content_artifacts_caps_alignment_range"),
        CheckConstraint("version_number > 0", name="ck_content_artifacts_version_positive"),
        CheckConstraint("row_version > 0", name="ck_content_artifacts_row_version_positive"),
        CheckConstraint("approval_count >= 0", name="ck_content_artifacts_approval_count_non_negative"),
        Index("ix_content_artifacts_scope_caps_layer", "scope_id", "caps_ref", "content_layer"),
    )


class ContentArtifactSource(Base):
    __tablename__ = "content_artifact_sources"

    source_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid())
    artifact_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("content_generation_artifacts.artifact_id", ondelete="CASCADE"), nullable=False)
    source_document_id: Mapped[str] = mapped_column(String(120), nullable=False)
    source_chunk_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    source_title: Mapped[str | None] = mapped_column(String(240), nullable=True)
    source_type: Mapped[str | None] = mapped_column(String(80), nullable=True)
    source_uri: Mapped[str | None] = mapped_column(String(500), nullable=True)
    citation_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    caps_ref: Mapped[str | None] = mapped_column(String(80), nullable=True)
    grade: Mapped[int | None] = mapped_column(Integer, nullable=True)
    subject_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    language: Mapped[str | None] = mapped_column(String(8), nullable=True)
    license_status: Mapped[str | None] = mapped_column(String(80), nullable=True)
    source_quality_score: Mapped[float | None] = mapped_column(Numeric(precision=5, scale=4), nullable=True)
    etl_version: Mapped[str | None] = mapped_column(String(80), nullable=True)
    document_version_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    chunk_hash: Mapped[str | None] = mapped_column(String(120), nullable=True)
    curriculum_mapping_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    source_hash: Mapped[str | None] = mapped_column(String(120), nullable=True)
    source_role: Mapped[str] = mapped_column(String(40), nullable=False, server_default="primary_context")
    source_metadata: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    artifact: Mapped[ContentGenerationArtifact] = relationship("ContentGenerationArtifact", back_populates="sources")

    __table_args__ = (Index("ix_content_artifact_sources_document_chunk", "source_document_id", "source_chunk_id"),)


class ContentValidationReport(Base):
    __tablename__ = "content_validation_reports"

    validation_report_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid())
    artifact_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("content_generation_artifacts.artifact_id", ondelete="CASCADE"), nullable=True)
    task_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("content_generation_tasks.task_id", ondelete="CASCADE"), nullable=True)
    passed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    checks: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    errors: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        CheckConstraint(
            "artifact_id IS NOT NULL OR task_id IS NOT NULL",
            name="ck_content_validation_reports_subject_present",
        ),
        Index("ix_content_validation_reports_artifact", "artifact_id", "created_at"),
        Index("ix_content_validation_reports_task", "task_id", "created_at"),
    )


class ContentAnswerKeyVerification(Base):
    """Append-only, independently attributable answer-key verification."""

    __tablename__ = "content_answer_key_verifications"

    verification_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid()
    )
    artifact_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("content_generation_artifacts.artifact_id", ondelete="RESTRICT"), nullable=False
    )
    artifact_version: Mapped[int] = mapped_column(Integer, nullable=False)
    artifact_hash: Mapped[str] = mapped_column(String(80), nullable=False)
    method: Mapped[str] = mapped_column(String(40), nullable=False)
    passed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    verifier_actor_id: Mapped[str] = mapped_column(String(80), nullable=False)
    verifier_provider: Mapped[str | None] = mapped_column(String(80), nullable=True)
    verifier_model: Mapped[str | None] = mapped_column(String(120), nullable=True)
    details: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    idempotency_key: Mapped[str] = mapped_column(String(160), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (
        CheckConstraint("artifact_version > 0", name="ck_answer_key_verification_version_positive"),
        CheckConstraint(
            "method IN ('deterministic_recompute','independent_model','educator_recalculation')",
            name="ck_answer_key_verification_method",
        ),
        UniqueConstraint(
            "verifier_actor_id",
            "idempotency_key",
            name="uq_answer_key_verification_actor_idempotency",
        ),
        Index(
            "ix_answer_key_verification_artifact_version_created",
            "artifact_id",
            "artifact_version",
            "created_at",
        ),
    )

class ContentArtifactReview(Base):
    __tablename__ = "content_artifact_reviews"

    review_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid())
    artifact_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("content_generation_artifacts.artifact_id", ondelete="CASCADE"), nullable=False)
    reviewer_id: Mapped[str | None] = mapped_column(String(80), nullable=True)
    review_action: Mapped[ContentReviewAction] = mapped_column(
        Enum(ContentReviewAction, name="content_review_action", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    review_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    quality_score: Mapped[float | None] = mapped_column(Numeric(precision=5, scale=4), nullable=True)
    reviewed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    artifact: Mapped[ContentGenerationArtifact] = relationship("ContentGenerationArtifact", back_populates="reviews")


class ContentReviewAssignment(Base):
    __tablename__ = "content_review_assignments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid())
    artifact_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("content_generation_artifacts.artifact_id", ondelete="CASCADE"), nullable=False)
    assigned_to: Mapped[str] = mapped_column(String(80), nullable=False)
    assigned_by: Mapped[str] = mapped_column(String(80), nullable=False)
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    due_by: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    priority: Mapped[str] = mapped_column(String(20), nullable=False, server_default="normal")
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="assigned")
    artifact_version: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reminder_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    last_reminded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    escalated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reassigned_from_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("content_review_assignments.id", ondelete="RESTRICT"), nullable=True)
    conflict_of_interest: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    reviewer_competencies: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    policy_version: Mapped[str] = mapped_column(String(40), nullable=False, server_default="phase3-v1")
    idempotency_key: Mapped[str | None] = mapped_column(String(160), nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("ix_content_review_assignments_reviewer_status", "assigned_to", "status"),
        Index("ix_content_review_assignments_artifact_status", "artifact_id", "status"),
        CheckConstraint("reminder_count >= 0", name="ck_content_review_assignments_reminders_non_negative"),
        UniqueConstraint("artifact_id", "artifact_version", "assigned_to", name="uq_content_review_assignment_artifact_version_reviewer"),
        UniqueConstraint("assigned_to", "idempotency_key", name="uq_content_review_assignment_reviewer_idempotency"),
    )


class ContentReviewDecision(Base):
    __tablename__ = "content_review_decisions"

    decision_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid())
    artifact_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("content_generation_artifacts.artifact_id", ondelete="RESTRICT"), nullable=False)
    artifact_version: Mapped[int] = mapped_column(Integer, nullable=False)
    reviewer_id: Mapped[str] = mapped_column(String(80), nullable=False)
    review_action: Mapped[ContentReviewAction] = mapped_column(
        Enum(ContentReviewAction, name="content_review_action", values_callable=lambda x: [e.value for e in x], create_type=False),
        nullable=False,
    )
    reason_code: Mapped[str | None] = mapped_column(String(80), nullable=True)
    comments: Mapped[str | None] = mapped_column(Text, nullable=True)
    rubric_id: Mapped[str] = mapped_column(String(80), nullable=False, server_default="educator-content-review")
    rubric_version: Mapped[str] = mapped_column(String(40), nullable=False, server_default="1.0")
    rubric_results: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    policy_version: Mapped[str] = mapped_column(String(40), nullable=False, server_default="phase3-v1")
    idempotency_key: Mapped[str] = mapped_column(String(160), nullable=False)
    conflict_of_interest: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    reviewer_competencies: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    correlation_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        CheckConstraint("artifact_version > 0", name="ck_content_review_decisions_version_positive"),
        UniqueConstraint("artifact_id", "artifact_version", "reviewer_id", name="uq_content_review_decision_artifact_version_reviewer"),
        UniqueConstraint("reviewer_id", "idempotency_key", name="uq_content_review_decision_reviewer_idempotency"),
        Index("ix_content_review_decisions_artifact_created", "artifact_id", "created_at"),
    )


class ContentStateTransitionEvent(Base):
    __tablename__ = "content_state_transition_events"

    event_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid())
    artifact_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("content_generation_artifacts.artifact_id", ondelete="RESTRICT"), nullable=False)
    artifact_version: Mapped[int] = mapped_column(Integer, nullable=False)
    previous_status: Mapped[str] = mapped_column(String(40), nullable=False)
    new_status: Mapped[str] = mapped_column(String(40), nullable=False)
    actor_id: Mapped[str] = mapped_column(String(80), nullable=False)
    reason_code: Mapped[str | None] = mapped_column(String(80), nullable=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    triggering_decision_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("content_review_decisions.decision_id", ondelete="RESTRICT"), nullable=True)
    policy_version: Mapped[str] = mapped_column(String(40), nullable=False, server_default="phase3-v1")
    correlation_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        CheckConstraint("artifact_version > 0", name="ck_content_state_events_version_positive"),
        Index("ix_content_state_events_artifact_created", "artifact_id", "created_at"),
    )


class ContentSeedRun(Base):
    __tablename__ = "content_seed_runs"

    seed_run_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid())
    scope_id: Mapped[str] = mapped_column(String(80), nullable=False)
    dry_run: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    status: Mapped[str] = mapped_column(String(40), nullable=False, server_default="pending")
    summary: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


class ContentStagingVerificationRun(Base):
    __tablename__ = "content_staging_verification_runs"

    run_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid())
    status: Mapped[str] = mapped_column(String(40), nullable=False, server_default="completed")
    summary_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    created_by: Mapped[str | None] = mapped_column(String(80), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class ContentStagingVerificationScopeResult(Base):
    __tablename__ = "content_staging_verification_scope_results"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid())
    run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("content_staging_verification_runs.run_id", ondelete="CASCADE"), nullable=False)
    scope_id: Mapped[str] = mapped_column(String(80), nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False)
    can_seed_staging: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    can_promote_production: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    summary_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    blockers_json: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, nullable=False, default=list)
    created_by: Mapped[str | None] = mapped_column(String(80), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        UniqueConstraint("run_id", "scope_id", name="uq_content_staging_verification_run_scope"),
        Index("ix_content_staging_verification_scope_status", "scope_id", "status"),
    )


class ContentPromotionEvent(Base):
    __tablename__ = "content_promotion_events"

    promotion_event_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid())
    artifact_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("content_generation_artifacts.artifact_id"), nullable=False)
    promoted_table: Mapped[str] = mapped_column(String(80), nullable=False)
    promoted_record_id: Mapped[str] = mapped_column(String(120), nullable=False)
    promoted_by: Mapped[str | None] = mapped_column(String(80), nullable=True)
    promoted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    rollback_metadata: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)


class LessonBank(Base):
    __tablename__ = "lesson_bank"

    lesson_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid())
    artifact_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("content_generation_artifacts.artifact_id"), nullable=False)
    scope_id: Mapped[str] = mapped_column(String(80), nullable=False)
    caps_ref: Mapped[str] = mapped_column(String(80), nullable=False)
    grade: Mapped[int] = mapped_column(Integer, nullable=False)
    subject_code: Mapped[str] = mapped_column(String(20), nullable=False)
    language: Mapped[str] = mapped_column(String(8), nullable=False)
    title: Mapped[str] = mapped_column(String(240), nullable=False)
    lesson_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)
    review_status: Mapped[str] = mapped_column(String(40), nullable=False)
    safety_status: Mapped[str] = mapped_column(String(40), nullable=False)
    quality_score: Mapped[float | None] = mapped_column(Numeric(precision=5, scale=4), nullable=True)
    source_snapshot_hash: Mapped[str | None] = mapped_column(String(120), nullable=True)
    promoted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        CheckConstraint("grade >= 0 AND grade <= 12", name="ck_lesson_bank_grade_range"),
        Index("ix_lesson_bank_scope_caps", "scope_id", "caps_ref"),
    )


class AssessmentBlueprint(Base):
    __tablename__ = "assessment_blueprints"

    blueprint_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid())
    artifact_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("content_generation_artifacts.artifact_id"), nullable=False)
    scope_id: Mapped[str] = mapped_column(String(80), nullable=False)
    caps_ref: Mapped[str | None] = mapped_column(String(80), nullable=True)
    grade: Mapped[int | None] = mapped_column(Integer, nullable=True)
    subject_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    language: Mapped[str] = mapped_column(String(8), nullable=False, server_default="en")
    title: Mapped[str | None] = mapped_column(String(240), nullable=True)
    blueprint_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    referenced_artifact_ids: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    review_status: Mapped[str] = mapped_column(String(40), nullable=False, server_default="draft")
    validation_status: Mapped[str] = mapped_column(String(40), nullable=False, server_default="pending")
    created_by_run_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("content_generation_runs.run_id"), nullable=True)
    status: Mapped[str] = mapped_column(String(40), nullable=False, server_default="approved")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())


class StudyPlanTemplate(Base):
    __tablename__ = "study_plan_templates"

    template_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid())
    artifact_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("content_generation_artifacts.artifact_id"), nullable=False)
    scope_id: Mapped[str] = mapped_column(String(80), nullable=False)
    caps_ref: Mapped[str | None] = mapped_column(String(80), nullable=True)
    grade: Mapped[int | None] = mapped_column(Integer, nullable=True)
    subject_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    language: Mapped[str] = mapped_column(String(8), nullable=False, server_default="en")
    title: Mapped[str | None] = mapped_column(String(240), nullable=True)
    template_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    referenced_artifact_ids: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    review_status: Mapped[str] = mapped_column(String(40), nullable=False, server_default="draft")
    validation_status: Mapped[str] = mapped_column(String(40), nullable=False, server_default="pending")
    created_by_run_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("content_generation_runs.run_id"), nullable=True)
    status: Mapped[str] = mapped_column(String(40), nullable=False, server_default="approved")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())


class ContentStagingSeedItem(Base):
    __tablename__ = "content_staging_seed_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid())
    seed_run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("content_seed_runs.seed_run_id"), nullable=False)
    artifact_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("content_generation_artifacts.artifact_id"), nullable=False)
    scope_id: Mapped[str] = mapped_column(String(80), nullable=False)
    caps_ref: Mapped[str | None] = mapped_column(String(80), nullable=True)
    layer: Mapped[str] = mapped_column(String(40), nullable=False)
    artifact_type: Mapped[str] = mapped_column(String(40), nullable=False)
    target_table: Mapped[str] = mapped_column(String(80), nullable=False)
    target_record_id: Mapped[str | None] = mapped_column(String(80), nullable=True)
    status: Mapped[str] = mapped_column(String(40), nullable=False, server_default="pending")
    skip_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    seed_payload_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    rollback_payload_json: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


class ContentStagingArtifact(Base):
    __tablename__ = "content_staging_artifacts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid())
    artifact_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("content_generation_artifacts.artifact_id"), nullable=False)
    scope_id: Mapped[str] = mapped_column(String(80), nullable=False)
    caps_ref: Mapped[str | None] = mapped_column(String(80), nullable=True)
    layer: Mapped[str] = mapped_column(String(40), nullable=False)
    artifact_type: Mapped[str] = mapped_column(String(40), nullable=False)
    payload_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    source_artifact_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    staging_status: Mapped[str] = mapped_column(String(40), nullable=False, server_default="pending")
    created_by_seed_run_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("content_seed_runs.seed_run_id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())


class ContentProductionArtifact(Base):
    __tablename__ = "content_production_artifacts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid())
    artifact_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("content_generation_artifacts.artifact_id"), nullable=False)
    staging_artifact_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("content_staging_artifacts.id"), nullable=True)
    scope_id: Mapped[str] = mapped_column(String(80), nullable=False)
    caps_ref: Mapped[str | None] = mapped_column(String(80), nullable=True)
    layer: Mapped[str] = mapped_column(String(40), nullable=False)
    artifact_type: Mapped[str] = mapped_column(String(40), nullable=False)
    payload_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    source_artifact_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    production_status: Mapped[str] = mapped_column(String(40), nullable=False, server_default="active")
    created_by_promotion_event_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("content_promotion_events.promotion_event_id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
