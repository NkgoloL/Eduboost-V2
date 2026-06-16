"""Phase 7 curriculum expansion and training-data governance models."""
from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Index, Integer, Numeric, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class CurriculumCoverageSnapshot(Base):
    __tablename__ = "curriculum_coverage_snapshots"

    snapshot_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid())
    scope_id: Mapped[str] = mapped_column(String(80), nullable=False)
    language: Mapped[str] = mapped_column(String(12), nullable=False)
    source_commit_sha: Mapped[str | None] = mapped_column(String(64), nullable=True)
    target_total: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    approved_total: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    published_total: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    gap_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    status: Mapped[str] = mapped_column(String(24), nullable=False)
    coverage_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        CheckConstraint("target_total >= 0", name="ck_p7_snapshot_target_nonnegative"),
        CheckConstraint("approved_total >= 0", name="ck_p7_snapshot_approved_nonnegative"),
        CheckConstraint("published_total >= 0", name="ck_p7_snapshot_published_nonnegative"),
        CheckConstraint("gap_count >= 0", name="ck_p7_snapshot_gap_nonnegative"),
        Index("ix_p7_snapshot_scope_captured", "scope_id", "captured_at"),
    )


class CurriculumExpansionRun(Base):
    __tablename__ = "curriculum_expansion_runs"

    run_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid())
    requested_by: Mapped[str] = mapped_column(String(120), nullable=False)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="planned", server_default="planned")
    scope_ids: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    languages: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    layers: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    dry_run: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
    plan_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (CheckConstraint("status IN ('planned','completed','cancelled','failed')", name="ck_p7_expansion_run_status"),)


class TrainingDatasetManifest(Base):
    __tablename__ = "training_dataset_manifests"

    manifest_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid())
    dataset_version: Mapped[str] = mapped_column(String(96), nullable=False, unique=True)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="draft", server_default="draft")
    policy_version: Mapped[str] = mapped_column(String(40), nullable=False)
    rubric_version: Mapped[str] = mapped_column(String(40), nullable=False)
    require_published: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
    min_quality_score: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False, default=Decimal("0.8000"), server_default="0.8000")
    min_caps_alignment_score: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False, default=Decimal("0.8000"), server_default="0.8000")
    artifact_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    language_counts: Mapped[dict[str, int]] = mapped_column(JSONB, nullable=False, default=dict)
    scope_counts: Mapped[dict[str, int]] = mapped_column(JSONB, nullable=False, default=dict)
    dataset_sha256: Mapped[str | None] = mapped_column(String(64), nullable=True)
    output_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_by: Mapped[str] = mapped_column(String(120), nullable=False)
    approved_by: Mapped[str | None] = mapped_column(String(120), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        CheckConstraint("status IN ('draft','ready','approved','rejected','superseded')", name="ck_p7_manifest_status"),
        CheckConstraint("artifact_count >= 0", name="ck_p7_manifest_artifact_count"),
        CheckConstraint("min_quality_score >= 0 AND min_quality_score <= 1", name="ck_p7_manifest_quality"),
        CheckConstraint("min_caps_alignment_score >= 0 AND min_caps_alignment_score <= 1", name="ck_p7_manifest_caps"),
        Index("ix_p7_manifest_status_created", "status", "created_at"),
    )


class TrainingDatasetEntry(Base):
    __tablename__ = "training_dataset_entries"

    entry_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid())
    manifest_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("training_dataset_manifests.manifest_id", ondelete="CASCADE"), nullable=False)
    artifact_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("content_generation_artifacts.artifact_id", ondelete="RESTRICT"), nullable=False)
    artifact_hash: Mapped[str] = mapped_column(String(80), nullable=False)
    artifact_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1, server_default="1")
    scope_id: Mapped[str] = mapped_column(String(80), nullable=False)
    caps_ref: Mapped[str | None] = mapped_column(String(80), nullable=True)
    language: Mapped[str] = mapped_column(String(12), nullable=False)
    content_layer: Mapped[str] = mapped_column(String(48), nullable=False)
    quality_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 4), nullable=True)
    caps_alignment_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 4), nullable=True)
    source_snapshot_hash: Mapped[str] = mapped_column(String(120), nullable=False)
    record_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("manifest_id", "artifact_id", "artifact_hash", name="uq_p7_manifest_artifact_hash"),
        CheckConstraint("artifact_version > 0", name="ck_p7_entry_version_positive"),
        Index("ix_p7_entry_manifest_language", "manifest_id", "language"),
        Index("ix_p7_entry_scope_caps", "scope_id", "caps_ref"),
    )
