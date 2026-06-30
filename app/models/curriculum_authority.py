"""Phase 2R authoritative curriculum-source and rights-governance models.

These tables are the authoritative, append-only control plane for curriculum
sources.  Retrieval tables remain rebuildable projections and must never be
used as source-version or rights authority.
"""
from __future__ import annotations

import enum
import uuid
from datetime import date, datetime
from typing import Any

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class AuthorityTier(str, enum.Enum):
    TIER_1 = "tier_1"
    TIER_2 = "tier_2"
    TIER_3 = "tier_3"


class RightsDecisionStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    APPROVED_WITH_CONDITIONS = "approved_with_conditions"
    DENIED = "denied"
    EXPIRED = "expired"
    WITHDRAWN = "withdrawn"
    DISPUTED = "disputed"


class InventoryStatus(str, enum.Enum):
    DRAFT = "draft"
    FROZEN = "frozen"
    SUPERSEDED = "superseded"


class InventoryItemStatus(str, enum.Enum):
    PENDING = "pending"
    LOCATED = "located"
    ABSENCE_APPROVED = "absence_approved"
    REJECTED = "rejected"


class ReviewDomain(str, enum.Enum):
    SOURCE_AUTHORITY = "source_authority"
    RIGHTS = "rights"
    INVENTORY_COMPLETENESS = "inventory_completeness"
    EXTRACTION = "extraction"
    CURRICULUM_MAPPING = "curriculum_mapping"
    GENERATED_CONTENT = "generated_content"
    ANSWER_VERIFICATION = "answer_verification"


class ReviewDecision(str, enum.Enum):
    APPROVE = "approve"
    REJECT = "reject"
    REQUEST_CHANGES = "request_changes"


class CurriculumSource(Base):
    """Logical source identity.  Rows are immutable after creation."""

    __tablename__ = "curriculum_sources"

    source_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    publisher: Mapped[str] = mapped_column(String(200), nullable=False)
    authority_tier: Mapped[str] = mapped_column(String(16), nullable=False)
    official_source_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    document_title: Mapped[str] = mapped_column(String(500), nullable=False)
    document_type: Mapped[str] = mapped_column(String(80), nullable=False)
    country: Mapped[str] = mapped_column(String(2), nullable=False, server_default="ZA")
    curriculum: Mapped[str] = mapped_column(String(80), nullable=False, server_default="CAPS")
    phase: Mapped[str | None] = mapped_column(String(80), nullable=True)
    grade: Mapped[int | None] = mapped_column(Integer, nullable=True)
    subject: Mapped[str | None] = mapped_column(String(120), nullable=True)
    language: Mapped[str] = mapped_column(String(8), nullable=False)
    created_by: Mapped[str] = mapped_column(String(120), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    versions: Mapped[list["CurriculumSourceVersion"]] = relationship(
        "CurriculumSourceVersion", back_populates="source"
    )

    __table_args__ = (
        CheckConstraint("authority_tier IN ('tier_1','tier_2','tier_3')", name="ck_curriculum_sources_authority_tier"),
        CheckConstraint("grade IS NULL OR (grade >= 0 AND grade <= 12)", name="ck_curriculum_sources_grade"),
        CheckConstraint("language IN ('en','af','nso')", name="ck_curriculum_sources_language"),
        Index("ix_curriculum_sources_scope", "curriculum", "grade", "subject", "language", "authority_tier"),
    )


class CurriculumSourceVersion(Base):
    """Immutable acquired source version and original-object identity."""

    __tablename__ = "curriculum_source_versions"

    source_version_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("curriculum_sources.source_id", ondelete="RESTRICT"), nullable=False
    )
    version_label: Mapped[str] = mapped_column(String(160), nullable=False)
    publication_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    effective_from: Mapped[date | None] = mapped_column(Date, nullable=True)
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    supersedes_source_version_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("curriculum_source_versions.source_version_id", ondelete="RESTRICT"), nullable=True
    )
    copyright_owner: Mapped[str | None] = mapped_column(String(300), nullable=True)
    original_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    original_object_uri: Mapped[str] = mapped_column(String(1000), nullable=False)
    media_type: Mapped[str] = mapped_column(String(120), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    retrieved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    retrieval_metadata: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    created_by: Mapped[str] = mapped_column(String(120), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    source: Mapped[CurriculumSource] = relationship("CurriculumSource", back_populates="versions")

    __table_args__ = (
        UniqueConstraint("source_id", "version_label", name="uq_curriculum_source_versions_source_label"),
        UniqueConstraint("source_id", "original_sha256", name="uq_curriculum_source_versions_source_hash"),
        CheckConstraint("original_sha256 ~ '^[0-9a-f]{64}$'", name="ck_curriculum_source_versions_sha256"),
        CheckConstraint("file_size_bytes > 0", name="ck_curriculum_source_versions_file_size"),
        CheckConstraint(
            "effective_to IS NULL OR effective_from IS NULL OR effective_to >= effective_from",
            name="ck_curriculum_source_versions_effective_dates",
        ),
        CheckConstraint(
            "supersedes_source_version_id IS NULL OR supersedes_source_version_id <> source_version_id",
            name="ck_curriculum_source_versions_no_self_supersession",
        ),
        Index("ix_curriculum_source_versions_source_effective", "source_id", "effective_from", "effective_to"),
    )


class CurriculumRightsDecision(Base):
    """Append-only, per-use legal/rights decision bound to one source version."""

    __tablename__ = "curriculum_rights_decisions"

    rights_decision_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_version_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("curriculum_source_versions.source_version_id", ondelete="RESTRICT"), nullable=False
    )
    decision_status: Mapped[str] = mapped_column(String(40), nullable=False)
    may_store_original: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    may_extract: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    may_embed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    may_use_for_retrieval: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    may_include_in_model_prompt: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    may_generate_derivatives: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    may_translate: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    may_publish_translation: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    may_show_excerpt_to_educator: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    may_show_excerpt_to_learner: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    may_redistribute: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    may_use_commercially: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    may_use_for_model_training: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    requires_attribution: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    conditions: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    decision_basis: Mapped[str] = mapped_column(Text, nullable=False)
    evidence_uri: Mapped[str] = mapped_column(String(1000), nullable=False)
    reviewed_by: Mapped[str] = mapped_column(String(120), nullable=False)
    reviewed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    supersedes_decision_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("curriculum_rights_decisions.rights_decision_id", ondelete="RESTRICT"), nullable=True
    )
    idempotency_key: Mapped[str] = mapped_column(String(180), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        CheckConstraint(
            "decision_status IN ('pending','approved','approved_with_conditions','denied','expired','withdrawn','disputed')",
            name="ck_curriculum_rights_decisions_status",
        ),
        CheckConstraint(
            "supersedes_decision_id IS NULL OR supersedes_decision_id <> rights_decision_id",
            name="ck_curriculum_rights_decisions_no_self_supersession",
        ),
        CheckConstraint(
            "decision_status <> 'approved_with_conditions' OR conditions <> '{}'::jsonb",
            name="ck_curriculum_rights_decisions_conditions_required",
        ),
        UniqueConstraint("reviewed_by", "idempotency_key", name="uq_curriculum_rights_decisions_actor_idempotency"),
        Index("ix_curriculum_rights_decisions_version_reviewed", "source_version_id", "reviewed_at"),
    )


class CurriculumInventoryVersion(Base):
    """Immutable completeness-register version."""

    __tablename__ = "curriculum_inventory_versions"

    inventory_version_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    inventory_code: Mapped[str] = mapped_column(String(160), nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    curriculum: Mapped[str] = mapped_column(String(80), nullable=False)
    grade: Mapped[int] = mapped_column(Integer, nullable=False)
    subject: Mapped[str] = mapped_column(String(120), nullable=False)
    delivery_languages: Mapped[list[str]] = mapped_column(JSONB, nullable=False)
    terms: Mapped[list[int]] = mapped_column(JSONB, nullable=False)
    strands: Mapped[list[str]] = mapped_column(JSONB, nullable=False)
    status: Mapped[str] = mapped_column(String(24), nullable=False)
    manifest_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    supersedes_inventory_version_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("curriculum_inventory_versions.inventory_version_id", ondelete="RESTRICT"), nullable=True
    )
    frozen_by: Mapped[str | None] = mapped_column(String(120), nullable=True)
    frozen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by: Mapped[str] = mapped_column(String(120), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    items: Mapped[list["CurriculumInventoryItem"]] = relationship(
        "CurriculumInventoryItem", back_populates="inventory_version"
    )

    __table_args__ = (
        UniqueConstraint("inventory_code", "version_number", name="uq_curriculum_inventory_versions_code_version"),
        CheckConstraint("version_number > 0", name="ck_curriculum_inventory_versions_version_positive"),
        CheckConstraint("grade >= 0 AND grade <= 12", name="ck_curriculum_inventory_versions_grade"),
        CheckConstraint("status IN ('draft','frozen','superseded')", name="ck_curriculum_inventory_versions_status"),
        CheckConstraint("manifest_sha256 ~ '^[0-9a-f]{64}$'", name="ck_curriculum_inventory_versions_sha256"),
        CheckConstraint(
            "status <> 'frozen' OR (frozen_by IS NOT NULL AND frozen_at IS NOT NULL)",
            name="ck_curriculum_inventory_versions_frozen_metadata",
        ),
        CheckConstraint(
            "supersedes_inventory_version_id IS NULL OR supersedes_inventory_version_id <> inventory_version_id",
            name="ck_curriculum_inventory_versions_no_self_supersession",
        ),
    )


class CurriculumInventoryItem(Base):
    """Append-only requirement or approved absence within an inventory version."""

    __tablename__ = "curriculum_inventory_items"

    inventory_item_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    inventory_version_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("curriculum_inventory_versions.inventory_version_id", ondelete="RESTRICT"), nullable=False
    )
    requirement_code: Mapped[str] = mapped_column(String(180), nullable=False)
    requirement_type: Mapped[str] = mapped_column(String(80), nullable=False)
    authority_tier: Mapped[str] = mapped_column(String(16), nullable=False)
    term: Mapped[int | None] = mapped_column(Integer, nullable=True)
    strand: Mapped[str | None] = mapped_column(String(160), nullable=True)
    language: Mapped[str | None] = mapped_column(String(8), nullable=True)
    source_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("curriculum_sources.source_id", ondelete="RESTRICT"), nullable=True
    )
    source_version_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("curriculum_source_versions.source_version_id", ondelete="RESTRICT"),
        nullable=True,
    )
    item_status: Mapped[str] = mapped_column(String(32), nullable=False)
    absence_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    evidence: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    reviewed_by: Mapped[str | None] = mapped_column(String(120), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    inventory_version: Mapped[CurriculumInventoryVersion] = relationship(
        "CurriculumInventoryVersion", back_populates="items"
    )

    __table_args__ = (
        UniqueConstraint("inventory_version_id", "requirement_code", name="uq_curriculum_inventory_items_requirement"),
        CheckConstraint("authority_tier IN ('tier_1','tier_2','tier_3')", name="ck_curriculum_inventory_items_authority_tier"),
        CheckConstraint("term IS NULL OR term BETWEEN 1 AND 4", name="ck_curriculum_inventory_items_term"),
        CheckConstraint("language IS NULL OR language IN ('en','af','nso')", name="ck_curriculum_inventory_items_language"),
        CheckConstraint(
            "item_status IN ('pending','located','absence_approved','rejected')",
            name="ck_curriculum_inventory_items_status",
        ),
        CheckConstraint(
            "item_status <> 'located' OR (source_id IS NOT NULL AND source_version_id IS NOT NULL)",
            name="ck_curriculum_inventory_items_located_source_version",
        ),
        CheckConstraint(
            "item_status <> 'absence_approved' OR (absence_reason IS NOT NULL AND reviewed_by IS NOT NULL AND reviewed_at IS NOT NULL)",
            name="ck_curriculum_inventory_items_absence_review",
        ),
        Index("ix_curriculum_inventory_items_scope", "inventory_version_id", "term", "strand", "language"),
    )


class CurriculumReviewDecision(Base):
    """Independent append-only review-domain decision ledger."""

    __tablename__ = "curriculum_review_decisions"

    review_decision_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    review_domain: Mapped[str] = mapped_column(String(40), nullable=False)
    subject_type: Mapped[str] = mapped_column(String(80), nullable=False)
    subject_id: Mapped[str] = mapped_column(String(120), nullable=False)
    decision: Mapped[str] = mapped_column(String(32), nullable=False)
    reviewer_id: Mapped[str] = mapped_column(String(120), nullable=False)
    reviewer_role: Mapped[str] = mapped_column(String(120), nullable=False)
    rationale: Mapped[str] = mapped_column(Text, nullable=False)
    evidence: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    supersedes_review_decision_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("curriculum_review_decisions.review_decision_id", ondelete="RESTRICT"), nullable=True
    )
    idempotency_key: Mapped[str] = mapped_column(String(180), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        CheckConstraint(
            "review_domain IN ('source_authority','rights','inventory_completeness','extraction','curriculum_mapping','generated_content','answer_verification')",
            name="ck_curriculum_review_decisions_domain",
        ),
        CheckConstraint(
            "decision IN ('approve','reject','request_changes')",
            name="ck_curriculum_review_decisions_decision",
        ),
        CheckConstraint(
            "supersedes_review_decision_id IS NULL OR supersedes_review_decision_id <> review_decision_id",
            name="ck_curriculum_review_decisions_no_self_supersession",
        ),
        UniqueConstraint("reviewer_id", "idempotency_key", name="uq_curriculum_review_decisions_actor_idempotency"),
        Index("ix_curriculum_review_decisions_subject", "review_domain", "subject_type", "subject_id", "created_at"),
    )
