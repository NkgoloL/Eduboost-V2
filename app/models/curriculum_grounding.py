"""Phase 2R gates 2R.2-2R.8 authoritative corpus, grounding, and audit models.

The tables in this module extend the Gate 2R.1 source/rights authority
control plane. They deliberately separate immutable authority records from
mutable operational projections:

* acquisition, extraction, page, section, chunk, mapping, corpus membership,
  grounding, verification, legacy, evaluation, and audit records are append-only;
* active corpus bindings and outbox processing status are mutable projections.

No generated lesson, assessment, or tutor answer should treat retrieval-index rows
as authority unless they resolve back to an active corpus version and immutable
source/chunk/mapping records defined here.
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
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class AcquisitionStatus(str, enum.Enum):
    REQUESTED = "requested"
    ACQUIRED = "acquired"
    QUARANTINED = "quarantined"
    FAILED = "failed"


class ExtractionStatus(str, enum.Enum):
    REQUESTED = "requested"
    COMPLETED = "completed"
    REVIEW_REQUIRED = "review_required"
    REJECTED = "rejected"
    FAILED = "failed"


class ReviewStatus(str, enum.Enum):
    DRAFT = "draft"
    REVIEW_REQUIRED = "review_required"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUPERSEDED = "superseded"


class CorpusStatus(str, enum.Enum):
    DRAFT = "draft"
    BUILT = "built"
    REVIEW_APPROVED = "review_approved"
    ACTIVE = "active"
    SUPERSEDED = "superseded"
    WITHDRAWN = "withdrawn"


class GroundingStatus(str, enum.Enum):
    PASSED = "passed"
    FAILED = "failed"
    FALLBACK = "fallback"


class ValidationStatus(str, enum.Enum):
    PASSED = "passed"
    FAILED = "failed"
    REVIEW_REQUIRED = "review_required"


class LegacyDisposition(str, enum.Enum):
    GROUNDED_VERIFIED = "grounded_verified"
    GROUNDED_UNVERIFIED = "grounded_unverified"
    SYNTHETIC_FIXTURE = "synthetic_fixture"
    LEGACY_UNGROUNDED = "legacy_ungrounded"
    PUBLISHED_REQUIRES_REVIEW = "published_requires_review"
    QUARANTINED = "quarantined"
    REGENERATED = "regenerated"
    WITHDRAWN = "withdrawn"


class AuditSeverity(str, enum.Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AuditFindingStatus(str, enum.Enum):
    OPEN = "open"
    MITIGATED = "mitigated"
    ACCEPTED = "accepted"
    CLOSED = "closed"


class CurriculumSourceAcquisitionRun(Base):
    """Append-only acquisition attempt for an approved source version."""

    __tablename__ = "curriculum_source_acquisition_runs"

    acquisition_run_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_version_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("curriculum_source_versions.source_version_id", ondelete="RESTRICT"), nullable=False
    )
    acquisition_method: Mapped[str] = mapped_column(String(40), nullable=False)
    requested_uri: Mapped[str] = mapped_column(String(1000), nullable=False)
    final_uri: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    operator_id: Mapped[str] = mapped_column(String(120), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    http_metadata: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    redirect_chain: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, default=list)
    malware_scan_status: Mapped[str] = mapped_column(String(40), nullable=False, server_default="not_run")
    failure_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        CheckConstraint("acquisition_method IN ('authorised_upload','approved_url','approved_api','checksum_refresh')", name="ck_curriculum_acquisition_method"),
        CheckConstraint("status IN ('requested','acquired','quarantined','failed')", name="ck_curriculum_acquisition_status"),
        CheckConstraint("finished_at IS NULL OR finished_at >= started_at", name="ck_curriculum_acquisition_time_order"),
        Index("ix_curriculum_acquisition_source_version", "source_version_id", "created_at"),
    )


class CurriculumOriginalObject(Base):
    """Immutable original object acquired into controlled storage."""

    __tablename__ = "curriculum_original_objects"

    original_object_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_version_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("curriculum_source_versions.source_version_id", ondelete="RESTRICT"), nullable=False
    )
    acquisition_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("curriculum_source_acquisition_runs.acquisition_run_id", ondelete="RESTRICT"), nullable=False
    )
    object_uri: Mapped[str] = mapped_column(String(1000), nullable=False)
    sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    media_type: Mapped[str] = mapped_column(String(120), nullable=False)
    storage_backend: Mapped[str] = mapped_column(String(80), nullable=False)
    encryption_state: Mapped[str] = mapped_column(String(40), nullable=False, server_default="managed")
    malware_scan_status: Mapped[str] = mapped_column(String(40), nullable=False)
    acquired_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_by: Mapped[str] = mapped_column(String(120), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("source_version_id", "sha256", name="uq_curriculum_original_objects_source_hash"),
        CheckConstraint("sha256 ~ '^[0-9a-f]{64}$'", name="ck_curriculum_original_objects_sha256"),
        CheckConstraint("size_bytes > 0", name="ck_curriculum_original_objects_size"),
        CheckConstraint("malware_scan_status IN ('passed','quarantined','failed','not_required')", name="ck_curriculum_original_objects_malware"),
    )


class CurriculumExtractionRun(Base):
    """Append-only extraction version with page-level provenance."""

    __tablename__ = "curriculum_extraction_runs"

    extraction_run_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_version_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("curriculum_source_versions.source_version_id", ondelete="RESTRICT"), nullable=False
    )
    original_object_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("curriculum_original_objects.original_object_id", ondelete="RESTRICT"), nullable=False
    )
    extractor_name: Mapped[str] = mapped_column(String(120), nullable=False)
    extractor_version: Mapped[str] = mapped_column(String(80), nullable=False)
    extraction_mode: Mapped[str] = mapped_column(String(40), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    page_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    warnings: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, default=list)
    quality_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    text_sha256: Mapped[str | None] = mapped_column(String(64), nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by: Mapped[str] = mapped_column(String(120), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        CheckConstraint("status IN ('requested','completed','review_required','rejected','failed')", name="ck_curriculum_extraction_runs_status"),
        CheckConstraint("extraction_mode IN ('native_pdf','ocr','text_fixture','manual_review')", name="ck_curriculum_extraction_runs_mode"),
        CheckConstraint("page_count >= 0", name="ck_curriculum_extraction_runs_page_count"),
        CheckConstraint("quality_score IS NULL OR (quality_score >= 0 AND quality_score <= 1)", name="ck_curriculum_extraction_runs_quality"),
        CheckConstraint("text_sha256 IS NULL OR text_sha256 ~ '^[0-9a-f]{64}$'", name="ck_curriculum_extraction_runs_text_sha"),
        CheckConstraint("finished_at IS NULL OR finished_at >= started_at", name="ck_curriculum_extraction_runs_time_order"),
        Index("ix_curriculum_extraction_runs_source_status", "source_version_id", "status", "created_at"),
    )


class CurriculumSourcePage(Base):
    __tablename__ = "curriculum_source_pages"

    page_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    extraction_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("curriculum_extraction_runs.extraction_run_id", ondelete="RESTRICT"), nullable=False
    )
    source_version_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("curriculum_source_versions.source_version_id", ondelete="RESTRICT"), nullable=False
    )
    page_number: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    text_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    language: Mapped[str] = mapped_column(String(8), nullable=False)
    extraction_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    coordinate_metadata: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    warnings: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("extraction_run_id", "page_number", name="uq_curriculum_source_pages_run_page"),
        CheckConstraint("page_number > 0", name="ck_curriculum_source_pages_number"),
        CheckConstraint("text_sha256 ~ '^[0-9a-f]{64}$'", name="ck_curriculum_source_pages_sha"),
        CheckConstraint("language IN ('en','af','nso')", name="ck_curriculum_source_pages_language"),
        CheckConstraint("extraction_confidence IS NULL OR (extraction_confidence >= 0 AND extraction_confidence <= 1)", name="ck_curriculum_source_pages_confidence"),
    )


class CurriculumSourceSection(Base):
    __tablename__ = "curriculum_source_sections"

    section_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    extraction_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("curriculum_extraction_runs.extraction_run_id", ondelete="RESTRICT"), nullable=False
    )
    source_version_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("curriculum_source_versions.source_version_id", ondelete="RESTRICT"), nullable=False
    )
    parent_section_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("curriculum_source_sections.section_id", ondelete="RESTRICT"), nullable=True
    )
    section_order: Mapped[int] = mapped_column(Integer, nullable=False)
    heading: Mapped[str | None] = mapped_column(String(500), nullable=True)
    page_start: Mapped[int] = mapped_column(Integer, nullable=False)
    page_end: Mapped[int] = mapped_column(Integer, nullable=False)
    text_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("extraction_run_id", "section_order", name="uq_curriculum_sections_run_order"),
        CheckConstraint("section_order >= 0", name="ck_curriculum_sections_order"),
        CheckConstraint("page_start > 0 AND page_end >= page_start", name="ck_curriculum_sections_pages"),
        CheckConstraint("text_sha256 ~ '^[0-9a-f]{64}$'", name="ck_curriculum_sections_sha"),
    )


class CurriculumChunkVersion(Base):
    __tablename__ = "curriculum_chunk_versions"

    chunk_version_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_version_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("curriculum_source_versions.source_version_id", ondelete="RESTRICT"), nullable=False
    )
    extraction_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("curriculum_extraction_runs.extraction_run_id", ondelete="RESTRICT"), nullable=False
    )
    section_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("curriculum_source_sections.section_id", ondelete="RESTRICT"), nullable=True
    )
    chunk_order: Mapped[int] = mapped_column(Integer, nullable=False)
    page_start: Mapped[int] = mapped_column(Integer, nullable=False)
    page_end: Mapped[int] = mapped_column(Integer, nullable=False)
    language: Mapped[str] = mapped_column(String(8), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    text_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    authority_tier: Mapped[str] = mapped_column(String(16), nullable=False)
    rights_decision_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("curriculum_rights_decisions.rights_decision_id", ondelete="RESTRICT"), nullable=False
    )
    review_status: Mapped[str] = mapped_column(String(32), nullable=False)
    quality_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    embedding_model: Mapped[str | None] = mapped_column(String(120), nullable=True)
    embedding_version: Mapped[str | None] = mapped_column(String(80), nullable=True)
    embedding_sha256: Mapped[str | None] = mapped_column(String(64), nullable=True)
    active_from: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    active_to: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("extraction_run_id", "chunk_order", name="uq_curriculum_chunk_versions_run_order"),
        CheckConstraint("chunk_order >= 0", name="ck_curriculum_chunk_versions_order"),
        CheckConstraint("page_start > 0 AND page_end >= page_start", name="ck_curriculum_chunk_versions_pages"),
        CheckConstraint("language IN ('en','af','nso')", name="ck_curriculum_chunk_versions_language"),
        CheckConstraint("text_sha256 ~ '^[0-9a-f]{64}$'", name="ck_curriculum_chunk_versions_text_sha"),
        CheckConstraint("embedding_sha256 IS NULL OR embedding_sha256 ~ '^[0-9a-f]{64}$'", name="ck_curriculum_chunk_versions_embedding_sha"),
        CheckConstraint("authority_tier IN ('tier_1','tier_2','tier_3')", name="ck_curriculum_chunk_versions_authority_tier"),
        CheckConstraint("review_status IN ('draft','review_required','approved','rejected','superseded')", name="ck_curriculum_chunk_versions_review_status"),
        CheckConstraint("quality_score IS NULL OR (quality_score >= 0 AND quality_score <= 1)", name="ck_curriculum_chunk_versions_quality"),
        CheckConstraint("active_to IS NULL OR active_from IS NULL OR active_to >= active_from", name="ck_curriculum_chunk_versions_active_dates"),
        Index("ix_curriculum_chunk_versions_source_review", "source_version_id", "review_status", "language"),
    )


class CurriculumGraphNode(Base):
    __tablename__ = "curriculum_graph_nodes"

    node_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    node_type: Mapped[str] = mapped_column(String(80), nullable=False)
    code: Mapped[str] = mapped_column(String(180), nullable=False)
    label: Mapped[str] = mapped_column(String(500), nullable=False)
    curriculum: Mapped[str] = mapped_column(String(80), nullable=False)
    grade: Mapped[int | None] = mapped_column(Integer, nullable=True)
    subject: Mapped[str | None] = mapped_column(String(120), nullable=True)
    language: Mapped[str | None] = mapped_column(String(8), nullable=True)
    parent_node_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("curriculum_graph_nodes.node_id", ondelete="RESTRICT"), nullable=True
    )
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    created_by: Mapped[str] = mapped_column(String(120), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("curriculum", "grade", "subject", "language", "node_type", "code", name="uq_curriculum_graph_nodes_scope_code"),
        CheckConstraint("node_type IN ('curriculum','phase','grade','subject','term','strand','topic','subtopic','skill','learning_objective','assessment_requirement','prerequisite','vocabulary')", name="ck_curriculum_graph_nodes_type"),
        CheckConstraint("grade IS NULL OR (grade >= 0 AND grade <= 12)", name="ck_curriculum_graph_nodes_grade"),
        CheckConstraint("language IS NULL OR language IN ('en','af','nso')", name="ck_curriculum_graph_nodes_language"),
    )


class CurriculumMappingVersion(Base):
    __tablename__ = "curriculum_mapping_versions"

    mapping_version_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chunk_version_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("curriculum_chunk_versions.chunk_version_id", ondelete="RESTRICT"), nullable=False
    )
    node_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("curriculum_graph_nodes.node_id", ondelete="RESTRICT"), nullable=False
    )
    relationship_type: Mapped[str] = mapped_column(String(80), nullable=False)
    proposal_method: Mapped[str] = mapped_column(String(80), nullable=False)
    review_status: Mapped[str] = mapped_column(String(32), nullable=False)
    reviewed_by: Mapped[str | None] = mapped_column(String(120), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    rationale: Mapped[str | None] = mapped_column(Text, nullable=True)
    supersedes_mapping_version_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("curriculum_mapping_versions.mapping_version_id", ondelete="RESTRICT"), nullable=True
    )
    idempotency_key: Mapped[str] = mapped_column(String(180), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("chunk_version_id", "node_id", "relationship_type", "idempotency_key", name="uq_curriculum_mapping_versions_idempotent"),
        CheckConstraint("relationship_type IN ('DEFINED_IN','EXEMPLIFIED_BY','ASSESSED_BY','CONTAINS','REQUIRES','PRECEDES','DEPENDS_ON','AMENDED_BY','SUPERSEDES','TRANSLATION_OF')", name="ck_curriculum_mapping_versions_relationship"),
        CheckConstraint("proposal_method IN ('manual','machine_proposed','imported')", name="ck_curriculum_mapping_versions_method"),
        CheckConstraint("review_status IN ('draft','review_required','approved','rejected','superseded')", name="ck_curriculum_mapping_versions_status"),
        CheckConstraint("review_status <> 'approved' OR (reviewed_by IS NOT NULL AND reviewed_at IS NOT NULL)", name="ck_curriculum_mapping_versions_approval_metadata"),
        CheckConstraint("supersedes_mapping_version_id IS NULL OR supersedes_mapping_version_id <> mapping_version_id", name="ck_curriculum_mapping_versions_no_self_supersession"),
        Index("ix_curriculum_mapping_versions_node_status", "node_id", "review_status"),
    )


class CurriculumCorpusVersion(Base):
    __tablename__ = "curriculum_corpus_versions"

    corpus_version_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    corpus_code: Mapped[str] = mapped_column(String(180), nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    scope: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    language: Mapped[str] = mapped_column(String(8), nullable=False)
    source_version_ids: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, default=list)
    chunk_version_ids: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, default=list)
    mapping_version_ids: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, default=list)
    embedding_model: Mapped[str] = mapped_column(String(120), nullable=False)
    embedding_version: Mapped[str] = mapped_column(String(80), nullable=False)
    manifest_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    review_status: Mapped[str] = mapped_column(String(32), nullable=False)
    built_by: Mapped[str] = mapped_column(String(120), nullable=False)
    built_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    supersedes_corpus_version_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("curriculum_corpus_versions.corpus_version_id", ondelete="RESTRICT"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("corpus_code", "version_number", name="uq_curriculum_corpus_versions_code_version"),
        CheckConstraint("version_number > 0", name="ck_curriculum_corpus_versions_number"),
        CheckConstraint("language IN ('en','af','nso')", name="ck_curriculum_corpus_versions_language"),
        CheckConstraint("manifest_sha256 ~ '^[0-9a-f]{64}$'", name="ck_curriculum_corpus_versions_manifest_sha"),
        CheckConstraint("status IN ('draft','built','review_approved','active','superseded','withdrawn')", name="ck_curriculum_corpus_versions_status"),
        CheckConstraint("review_status IN ('draft','review_required','approved','rejected','superseded')", name="ck_curriculum_corpus_versions_review_status"),
        CheckConstraint("supersedes_corpus_version_id IS NULL OR supersedes_corpus_version_id <> corpus_version_id", name="ck_curriculum_corpus_versions_no_self_supersession"),
    )


class CurriculumCorpusMembership(Base):
    __tablename__ = "curriculum_corpus_memberships"

    corpus_membership_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    corpus_version_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("curriculum_corpus_versions.corpus_version_id", ondelete="RESTRICT"), nullable=False
    )
    chunk_version_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("curriculum_chunk_versions.chunk_version_id", ondelete="RESTRICT"), nullable=False
    )
    mapping_version_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("curriculum_mapping_versions.mapping_version_id", ondelete="RESTRICT"), nullable=False
    )
    authority_tier: Mapped[str] = mapped_column(String(16), nullable=False)
    retrieval_eligible: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    eligibility_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    added_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("corpus_version_id", "chunk_version_id", "mapping_version_id", name="uq_curriculum_corpus_memberships_unique"),
        CheckConstraint("authority_tier IN ('tier_1','tier_2','tier_3')", name="ck_curriculum_corpus_memberships_tier"),
    )


class CurriculumCorpusActivationEvent(Base):
    __tablename__ = "curriculum_corpus_activation_events"

    activation_event_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    corpus_version_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("curriculum_corpus_versions.corpus_version_id", ondelete="RESTRICT"), nullable=False
    )
    activation_key: Mapped[str] = mapped_column(String(240), nullable=False)
    event_type: Mapped[str] = mapped_column(String(32), nullable=False)
    previous_corpus_version_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("curriculum_corpus_versions.corpus_version_id", ondelete="RESTRICT"), nullable=True
    )
    actor_id: Mapped[str] = mapped_column(String(120), nullable=False)
    rationale: Mapped[str] = mapped_column(Text, nullable=False)
    binding_epoch: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        CheckConstraint("event_type IN ('activate','rollback','withdraw')", name="ck_curriculum_corpus_activation_event_type"),
        CheckConstraint("binding_epoch > 0", name="ck_curriculum_corpus_activation_epoch"),
        Index("ix_curriculum_corpus_activation_key_created", "activation_key", "created_at"),
    )


class CurriculumCorpusActiveBinding(Base):
    """Mutable projection of the active corpus binding.

    This is intentionally not authority. The activation event ledger and corpus
    manifest remain authoritative.
    """

    __tablename__ = "curriculum_corpus_active_bindings"

    activation_key: Mapped[str] = mapped_column(String(240), primary_key=True)
    corpus_version_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("curriculum_corpus_versions.corpus_version_id", ondelete="RESTRICT"), nullable=False
    )
    activation_event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("curriculum_corpus_activation_events.activation_event_id", ondelete="RESTRICT"), nullable=False
    )
    binding_epoch: Mapped[int] = mapped_column(Integer, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    __table_args__ = (CheckConstraint("binding_epoch > 0", name="ck_curriculum_corpus_active_bindings_epoch"),)


class CurriculumCorpusOutboxEvent(Base):
    __tablename__ = "curriculum_corpus_outbox_events"

    outbox_event_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    activation_event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("curriculum_corpus_activation_events.activation_event_id", ondelete="RESTRICT"), nullable=False
    )
    event_type: Mapped[str] = mapped_column(String(80), nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    processing_status: Mapped[str] = mapped_column(String(32), nullable=False, server_default="pending")
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    next_attempt_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        CheckConstraint("processing_status IN ('pending','processing','processed','failed')", name="ck_curriculum_corpus_outbox_status"),
        CheckConstraint("attempts >= 0", name="ck_curriculum_corpus_outbox_attempts"),
    )


class CurriculumGenerationGroundingRecord(Base):
    __tablename__ = "curriculum_generation_grounding_records"

    grounding_record_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    artifact_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    request_id: Mapped[str] = mapped_column(String(160), nullable=False)
    corpus_version_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("curriculum_corpus_versions.corpus_version_id", ondelete="RESTRICT"), nullable=False
    )
    policy_version: Mapped[str] = mapped_column(String(80), nullable=False)
    retrieval_query: Mapped[str] = mapped_column(Text, nullable=False)
    requested_objective_ids: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, default=list)
    chunk_version_ids: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, default=list)
    mapping_version_ids: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, default=list)
    source_version_ids: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, default=list)
    retrieval_scores: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, default=list)
    source_snapshot_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    grounding_status: Mapped[str] = mapped_column(String(32), nullable=False)
    failure_reasons: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, default=list)
    provider: Mapped[str | None] = mapped_column(String(80), nullable=True)
    model: Mapped[str | None] = mapped_column(String(120), nullable=True)
    prompt_version: Mapped[str | None] = mapped_column(String(80), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("request_id", name="uq_curriculum_generation_grounding_request"),
        CheckConstraint("source_snapshot_hash ~ '^[0-9a-f]{64}$'", name="ck_curriculum_generation_grounding_snapshot"),
        CheckConstraint("grounding_status IN ('passed','failed','fallback')", name="ck_curriculum_generation_grounding_status"),
    )


class CurriculumClaimValidationRecord(Base):
    __tablename__ = "curriculum_claim_validation_records"

    claim_validation_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    grounding_record_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("curriculum_generation_grounding_records.grounding_record_id", ondelete="RESTRICT"), nullable=False
    )
    claim_type: Mapped[str] = mapped_column(String(80), nullable=False)
    claim_text: Mapped[str] = mapped_column(Text, nullable=False)
    supporting_chunk_version_ids: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, default=list)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    validator_version: Mapped[str] = mapped_column(String(80), nullable=False)
    evidence: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        CheckConstraint("claim_type IN ('curriculum_requirement','pedagogical_guidance','mathematical_fact','assessment_claim','enrichment')", name="ck_curriculum_claim_validation_type"),
        CheckConstraint("status IN ('passed','failed','review_required')", name="ck_curriculum_claim_validation_status"),
    )


class CurriculumAnswerVerificationRecord(Base):
    __tablename__ = "curriculum_answer_verification_records"

    answer_verification_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    artifact_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    question_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    answer_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    reasoning_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    checker_type: Mapped[str] = mapped_column(String(80), nullable=False)
    checker_version: Mapped[str] = mapped_column(String(80), nullable=False)
    verification_status: Mapped[str] = mapped_column(String(32), nullable=False)
    expected_answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    observed_answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    evidence: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        CheckConstraint("question_hash ~ '^[0-9a-f]{64}$'", name="ck_curriculum_answer_verification_question_hash"),
        CheckConstraint("answer_hash ~ '^[0-9a-f]{64}$'", name="ck_curriculum_answer_verification_answer_hash"),
        CheckConstraint("reasoning_hash IS NULL OR reasoning_hash ~ '^[0-9a-f]{64}$'", name="ck_curriculum_answer_verification_reasoning_hash"),
        CheckConstraint("verification_status IN ('passed','failed','review_required')", name="ck_curriculum_answer_verification_status"),
    )


class TutorGroundingRecord(Base):
    __tablename__ = "tutor_grounding_records"

    tutor_grounding_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[str | None] = mapped_column(String(80), nullable=True)
    message_id: Mapped[str | None] = mapped_column(String(80), nullable=True)
    learner_id: Mapped[str | None] = mapped_column(String(80), nullable=True)
    corpus_version_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("curriculum_corpus_versions.corpus_version_id", ondelete="RESTRICT"), nullable=True
    )
    retrieval_query: Mapped[str] = mapped_column(Text, nullable=False)
    source_chunk_ids: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, default=list)
    published_artifact_ids: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, default=list)
    curriculum_node_ids: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, default=list)
    grounding_status: Mapped[str] = mapped_column(String(32), nullable=False)
    fallback_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_snapshot_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    safety_metadata: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        CheckConstraint("grounding_status IN ('passed','failed','fallback')", name="ck_tutor_grounding_records_status"),
        CheckConstraint("grounding_status = 'passed' OR fallback_reason IS NOT NULL", name="ck_tutor_grounding_records_fallback_reason"),
        CheckConstraint("source_snapshot_hash IS NULL OR source_snapshot_hash ~ '^[0-9a-f]{64}$'", name="ck_tutor_grounding_records_snapshot"),
    )


class CurriculumLegacyDisposition(Base):
    __tablename__ = "curriculum_legacy_dispositions"

    legacy_disposition_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    artifact_type: Mapped[str] = mapped_column(String(80), nullable=False)
    artifact_id: Mapped[str] = mapped_column(String(160), nullable=False)
    previous_publication_state: Mapped[str | None] = mapped_column(String(80), nullable=True)
    disposition: Mapped[str] = mapped_column(String(80), nullable=False)
    learner_serving_allowed: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    rationale: Mapped[str] = mapped_column(Text, nullable=False)
    evidence: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    decided_by: Mapped[str] = mapped_column(String(120), nullable=False)
    decided_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    supersedes_disposition_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("curriculum_legacy_dispositions.legacy_disposition_id", ondelete="RESTRICT"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("artifact_type", "artifact_id", "decided_at", name="uq_curriculum_legacy_disposition_event"),
        CheckConstraint("disposition IN ('grounded_verified','grounded_unverified','synthetic_fixture','legacy_ungrounded','published_requires_review','quarantined','regenerated','withdrawn')", name="ck_curriculum_legacy_dispositions_value"),
        CheckConstraint("learner_serving_allowed IS FALSE OR disposition = 'grounded_verified'", name="ck_curriculum_legacy_dispositions_serving_allowed"),
        CheckConstraint("supersedes_disposition_id IS NULL OR supersedes_disposition_id <> legacy_disposition_id", name="ck_curriculum_legacy_dispositions_no_self_supersession"),
    )


class CurriculumRetrievalEvaluationRun(Base):
    __tablename__ = "curriculum_retrieval_evaluation_runs"

    evaluation_run_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    corpus_version_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("curriculum_corpus_versions.corpus_version_id", ondelete="RESTRICT"), nullable=False
    )
    dataset_version: Mapped[str] = mapped_column(String(120), nullable=False)
    metrics: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    prohibited_hit_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    wrong_version_hit_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    wrong_language_hit_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    fallback_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(120), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        CheckConstraint("prohibited_hit_count >= 0 AND wrong_version_hit_count >= 0 AND wrong_language_hit_count >= 0", name="ck_curriculum_eval_counts"),
        CheckConstraint("fallback_rate IS NULL OR (fallback_rate >= 0 AND fallback_rate <= 1)", name="ck_curriculum_eval_fallback_rate"),
        CheckConstraint("status IN ('passed','failed','review_required')", name="ck_curriculum_eval_status"),
    )


class CurriculumRetrievalEvaluationCase(Base):
    __tablename__ = "curriculum_retrieval_evaluation_cases"

    evaluation_case_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    evaluation_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("curriculum_retrieval_evaluation_runs.evaluation_run_id", ondelete="RESTRICT"), nullable=False
    )
    case_id: Mapped[str] = mapped_column(String(160), nullable=False)
    language: Mapped[str] = mapped_column(String(8), nullable=False)
    strand: Mapped[str] = mapped_column(String(160), nullable=False)
    term: Mapped[int | None] = mapped_column(Integer, nullable=True)
    query: Mapped[str] = mapped_column(Text, nullable=False)
    expected_chunk_version_ids: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, default=list)
    retrieved_chunk_version_ids: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, default=list)
    is_negative_case: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    metrics: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("evaluation_run_id", "case_id", name="uq_curriculum_eval_cases_case"),
        CheckConstraint("language IN ('en','af','nso')", name="ck_curriculum_eval_cases_language"),
        CheckConstraint("term IS NULL OR (term >= 1 AND term <= 4)", name="ck_curriculum_eval_cases_term"),
        CheckConstraint("status IN ('passed','failed','review_required')", name="ck_curriculum_eval_cases_status"),
    )


class Phase02RAuditFinding(Base):
    __tablename__ = "phase02r_audit_findings"

    audit_finding_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    gate: Mapped[str] = mapped_column(String(16), nullable=False)
    finding_code: Mapped[str] = mapped_column(String(120), nullable=False)
    severity: Mapped[str] = mapped_column(String(16), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    finding: Mapped[str] = mapped_column(Text, nullable=False)
    corrective_action: Mapped[str | None] = mapped_column(Text, nullable=True)
    evidence: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    auditor_id: Mapped[str] = mapped_column(String(120), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("gate", "finding_code", "created_at", name="uq_phase02r_audit_findings_event"),
        CheckConstraint("severity IN ('info','low','medium','high','critical')", name="ck_phase02r_audit_findings_severity"),
        CheckConstraint("status IN ('open','mitigated','accepted','closed')", name="ck_phase02r_audit_findings_status"),
        CheckConstraint("gate IN ('2R.2','2R.3','2R.4','2R.5','2R.6','2R.7','2R.8')", name="ck_phase02r_audit_findings_gate"),
    )
