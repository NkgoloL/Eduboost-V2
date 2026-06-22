"""SQLAlchemy models for Phase 02R Gate 2R.4 curriculum graph controls.

The tables in this module are the controlled graph/mapping review layer for Gate
2R.4. They are intentionally separate from Gate 2R.5 corpus activation and from
retrieval/generation/tutor projections.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class CurriculumNode(Base):
    __tablename__ = "curriculum_nodes"

    curriculum_node_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    curriculum_code: Mapped[str] = mapped_column(String(40), nullable=False)
    grade: Mapped[int] = mapped_column(Integer, nullable=False)
    subject_code: Mapped[str] = mapped_column(String(80), nullable=False)
    stable_code: Mapped[str] = mapped_column(String(180), nullable=False)
    node_type: Mapped[str] = mapped_column(String(80), nullable=False)
    created_by: Mapped[str] = mapped_column(String(120), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("curriculum_code", "grade", "subject_code", "stable_code", name="uq_curriculum_nodes_scope_stable_code"),
        CheckConstraint("grade >= 0 AND grade <= 12", name="ck_curriculum_nodes_grade"),
        CheckConstraint(
            "node_type IN ('curriculum','phase','grade','subject','term','strand','topic','subtopic','skill','learning_objective','assessment_requirement','assessment_statement','prerequisite','vocabulary')",
            name="ck_curriculum_nodes_type",
        ),
        Index("ix_curriculum_nodes_scope", "curriculum_code", "grade", "subject_code"),
    )


class CurriculumNodeVersion(Base):
    __tablename__ = "curriculum_node_versions"

    curriculum_node_version_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    curriculum_node_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("curriculum_nodes.curriculum_node_id", ondelete="RESTRICT"), nullable=False)
    curriculum_code: Mapped[str] = mapped_column(String(40), nullable=False)
    grade: Mapped[int] = mapped_column(Integer, nullable=False)
    subject_code: Mapped[str] = mapped_column(String(80), nullable=False)
    strand: Mapped[str] = mapped_column(String(180), nullable=False)
    term: Mapped[str | None] = mapped_column(String(40), nullable=True)
    topic: Mapped[str] = mapped_column(String(240), nullable=False)
    subtopic: Mapped[str | None] = mapped_column(String(240), nullable=True)
    skill: Mapped[str | None] = mapped_column(String(240), nullable=True)
    learning_objective: Mapped[str] = mapped_column(Text, nullable=False)
    assessment_statement: Mapped[str | None] = mapped_column(Text, nullable=True)
    language: Mapped[str] = mapped_column(String(8), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    effective_from: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    effective_to: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    supersedes_version_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("curriculum_node_versions.curriculum_node_version_id", ondelete="RESTRICT"), nullable=True)
    created_by: Mapped[str] = mapped_column(String(120), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)

    __table_args__ = (
        UniqueConstraint("curriculum_node_id", "created_at", name="uq_curriculum_node_versions_node_created"),
        CheckConstraint("grade >= 0 AND grade <= 12", name="ck_curriculum_node_versions_grade"),
        CheckConstraint("language IN ('en','af','nso','zu','xh')", name="ck_curriculum_node_versions_language"),
        CheckConstraint("status IN ('draft','in_review','approved','superseded','withdrawn')", name="ck_curriculum_node_versions_status"),
        CheckConstraint("effective_to IS NULL OR effective_from IS NULL OR effective_to >= effective_from", name="ck_curriculum_node_versions_effective_order"),
        CheckConstraint("supersedes_version_id IS NULL OR supersedes_version_id <> curriculum_node_version_id", name="ck_curriculum_node_versions_no_self_supersession"),
        Index("ix_curriculum_node_versions_requirement", "curriculum_code", "grade", "subject_code", "status"),
    )


class CurriculumEdgeVersion(Base):
    __tablename__ = "curriculum_edge_versions"

    edge_version_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    from_curriculum_node_version_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("curriculum_node_versions.curriculum_node_version_id", ondelete="RESTRICT"), nullable=False)
    to_curriculum_node_version_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("curriculum_node_versions.curriculum_node_version_id", ondelete="RESTRICT"), nullable=False)
    edge_type: Mapped[str] = mapped_column(String(40), nullable=False)
    review_status: Mapped[str] = mapped_column(String(32), nullable=False)
    proposed_by: Mapped[str] = mapped_column(String(120), nullable=False)
    proposed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    reviewed_by: Mapped[str | None] = mapped_column(String(120), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    review_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    supersedes_edge_version_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("curriculum_edge_versions.edge_version_id", ondelete="RESTRICT"), nullable=True)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)

    __table_args__ = (
        CheckConstraint("from_curriculum_node_version_id <> to_curriculum_node_version_id", name="ck_curriculum_edge_versions_distinct_nodes"),
        CheckConstraint("edge_type IN ('prerequisite_of','sequence_before','supports','assesses','same_concept_as','translation_of')", name="ck_curriculum_edge_versions_type"),
        CheckConstraint("review_status IN ('proposed','in_review','approved','rejected','needs_revision','superseded','withdrawn')", name="ck_curriculum_edge_versions_status"),
        CheckConstraint("review_status <> 'approved' OR (reviewed_by IS NOT NULL AND reviewed_at IS NOT NULL)", name="ck_curriculum_edge_versions_approval_metadata"),
        CheckConstraint("reviewed_by IS NULL OR reviewed_by <> proposed_by OR metadata_json ? 'maker_checker_exception_id'", name="ck_curriculum_edge_versions_maker_checker"),
        CheckConstraint("supersedes_edge_version_id IS NULL OR supersedes_edge_version_id <> edge_version_id", name="ck_curriculum_edge_versions_no_self_supersession"),
        Index("ix_curriculum_edge_versions_from", "from_curriculum_node_version_id", "edge_type"),
        Index("ix_curriculum_edge_versions_to", "to_curriculum_node_version_id", "edge_type"),
    )


class CurriculumSourceMappingVersion(Base):
    __tablename__ = "curriculum_source_mapping_versions"

    mapping_version_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mapping_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    source_chunk_version_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("curriculum_chunk_versions.chunk_version_id", ondelete="RESTRICT"), nullable=False)
    source_page_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("curriculum_source_pages.page_id", ondelete="RESTRICT"), nullable=True)
    source_section_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("curriculum_source_sections.section_id", ondelete="RESTRICT"), nullable=True)
    curriculum_node_version_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("curriculum_node_versions.curriculum_node_version_id", ondelete="RESTRICT"), nullable=False)
    support_type: Mapped[str] = mapped_column(String(60), nullable=False)
    authority_tier: Mapped[str] = mapped_column(String(16), nullable=False)
    language: Mapped[str] = mapped_column(String(8), nullable=False)
    language_status: Mapped[str] = mapped_column(String(60), nullable=False)
    mapping_rationale: Mapped[str] = mapped_column(Text, nullable=False)
    proposed_by: Mapped[str] = mapped_column(String(120), nullable=False)
    proposed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    review_status: Mapped[str] = mapped_column(String(32), nullable=False)
    reviewed_by: Mapped[str | None] = mapped_column(String(120), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    review_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    supersedes_mapping_version_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("curriculum_source_mapping_versions.mapping_version_id", ondelete="RESTRICT"), nullable=True)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("mapping_id", "mapping_version_id", name="uq_curriculum_source_mapping_versions_identity"),
        CheckConstraint("support_type IN ('direct_support','example','assessment_evidence','teaching_guidance','background_context')", name="ck_curriculum_source_mapping_versions_support_type"),
        CheckConstraint("authority_tier IN ('tier_1','tier_2','tier_3')", name="ck_curriculum_source_mapping_versions_tier"),
        CheckConstraint("language IN ('en','af','nso','zu','xh')", name="ck_curriculum_source_mapping_versions_language"),
        CheckConstraint("language_status IN ('official_source','approved_human_translation','machine_translation_draft','generated_learner_explanation')", name="ck_curriculum_source_mapping_versions_language_status"),
        CheckConstraint("NOT (language_status = 'machine_translation_draft' AND authority_tier = 'tier_1')", name="ck_curriculum_source_mapping_versions_machine_not_tier1"),
        CheckConstraint("review_status IN ('proposed','in_review','approved','rejected','needs_revision','superseded','withdrawn')", name="ck_curriculum_source_mapping_versions_review_status"),
        CheckConstraint("review_status <> 'approved' OR (reviewed_by IS NOT NULL AND reviewed_at IS NOT NULL)", name="ck_curriculum_source_mapping_versions_approval_metadata"),
        CheckConstraint("reviewed_by IS NULL OR reviewed_by <> proposed_by OR metadata_json ? 'maker_checker_exception_id'", name="ck_curriculum_source_mapping_versions_maker_checker"),
        CheckConstraint("supersedes_mapping_version_id IS NULL OR supersedes_mapping_version_id <> mapping_version_id", name="ck_curriculum_source_mapping_versions_no_self_supersession"),
        Index("ix_curriculum_source_mapping_versions_node_status", "curriculum_node_version_id", "review_status"),
        Index("ix_curriculum_source_mapping_versions_chunk", "source_chunk_version_id"),
    )


class CurriculumMappingReviewEvent(Base):
    __tablename__ = "curriculum_mapping_review_events"

    review_event_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mapping_version_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("curriculum_source_mapping_versions.mapping_version_id", ondelete="RESTRICT"), nullable=False)
    event_type: Mapped[str] = mapped_column(String(60), nullable=False)
    actor_id: Mapped[str] = mapped_column(String(120), nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    previous_status: Mapped[str | None] = mapped_column(String(32), nullable=True)
    next_status: Mapped[str | None] = mapped_column(String(32), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    exception_id: Mapped[str | None] = mapped_column(String(160), nullable=True)
    per_item_trace_id: Mapped[str | None] = mapped_column(String(240), nullable=True)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)

    __table_args__ = (
        CheckConstraint("event_type IN ('proposed','moved_to_review','approved','rejected','needs_revision','withdrawn','superseded','single_developer_exception_recorded')", name="ck_curriculum_mapping_review_events_type"),
        CheckConstraint("event_type <> 'approved' OR per_item_trace_id IS NOT NULL", name="ck_curriculum_mapping_review_events_approval_trace"),
        Index("ix_curriculum_mapping_review_events_mapping_time", "mapping_version_id", "occurred_at"),
    )


class CurriculumLanguageLink(Base):
    __tablename__ = "curriculum_language_links"

    language_link_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_node_version_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("curriculum_node_versions.curriculum_node_version_id", ondelete="RESTRICT"), nullable=False)
    target_node_version_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("curriculum_node_versions.curriculum_node_version_id", ondelete="RESTRICT"), nullable=False)
    language_status: Mapped[str] = mapped_column(String(60), nullable=False)
    review_status: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[str] = mapped_column(String(120), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    reviewed_by: Mapped[str | None] = mapped_column(String(120), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        CheckConstraint("source_node_version_id <> target_node_version_id", name="ck_curriculum_language_links_distinct_nodes"),
        CheckConstraint("language_status IN ('official_source','approved_human_translation','machine_translation_draft','generated_learner_explanation')", name="ck_curriculum_language_links_status"),
        CheckConstraint("review_status IN ('proposed','in_review','approved','rejected','needs_revision','superseded','withdrawn')", name="ck_curriculum_language_links_review_status"),
        CheckConstraint("NOT (language_status = 'machine_translation_draft' AND review_status = 'approved')", name="ck_curriculum_language_links_machine_not_official"),
        UniqueConstraint("source_node_version_id", "target_node_version_id", "language_status", name="uq_curriculum_language_links_pair_status"),
    )
