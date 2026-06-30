"""Phase 7 curriculum coverage and training-data governance.

Revision ID: 20260615_1800_p7_curriculum
Revises: 20260615_1500_p6_ai_ops
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260615_1800_p7_curriculum"
down_revision = "20260615_1500_p6_ai_ops"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "curriculum_coverage_snapshots",
        sa.Column("snapshot_id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("scope_id", sa.String(length=80), nullable=False),
        sa.Column("language", sa.String(length=12), nullable=False),
        sa.Column("source_commit_sha", sa.String(length=64), nullable=True),
        sa.Column("target_total", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("approved_total", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("gap_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("coverage_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("target_total >= 0", name="ck_p7_snapshot_target_nonnegative"),
        sa.CheckConstraint("approved_total >= 0", name="ck_p7_snapshot_approved_nonnegative"),
        sa.CheckConstraint("gap_count >= 0", name="ck_p7_snapshot_gap_nonnegative"),
    )
    op.create_index("ix_p7_snapshot_scope_captured", "curriculum_coverage_snapshots", ["scope_id", "captured_at"])

    op.create_table(
        "curriculum_expansion_runs",
        sa.Column("run_id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("requested_by", sa.String(length=120), nullable=False),
        sa.Column("status", sa.String(length=24), nullable=False, server_default="planned"),
        sa.Column("scope_ids", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("languages", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("layers", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("dry_run", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("plan_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("status IN ('planned','completed','cancelled','failed')", name="ck_p7_expansion_run_status"),
    )

    op.create_table(
        "training_dataset_manifests",
        sa.Column("manifest_id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("dataset_version", sa.String(length=96), nullable=False, unique=True),
        sa.Column("status", sa.String(length=24), nullable=False, server_default="draft"),
        sa.Column("policy_version", sa.String(length=40), nullable=False),
        sa.Column("rubric_version", sa.String(length=40), nullable=False),
        sa.Column("require_published", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("min_quality_score", sa.Numeric(precision=5, scale=4), nullable=False, server_default="0.8000"),
        sa.Column("min_caps_alignment_score", sa.Numeric(precision=5, scale=4), nullable=False, server_default="0.8000"),
        sa.Column("artifact_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("language_counts", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("scope_counts", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("dataset_sha256", sa.String(length=64), nullable=True),
        sa.Column("output_path", sa.String(length=500), nullable=True),
        sa.Column("created_by", sa.String(length=120), nullable=False),
        sa.Column("approved_by", sa.String(length=120), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("status IN ('draft','ready','approved','rejected','superseded')", name="ck_p7_manifest_status"),
        sa.CheckConstraint("artifact_count >= 0", name="ck_p7_manifest_artifact_count"),
        sa.CheckConstraint("min_quality_score >= 0 AND min_quality_score <= 1", name="ck_p7_manifest_quality"),
        sa.CheckConstraint("min_caps_alignment_score >= 0 AND min_caps_alignment_score <= 1", name="ck_p7_manifest_caps"),
        sa.CheckConstraint(
            "(status <> 'approved') OR (dataset_sha256 IS NOT NULL AND approved_by IS NOT NULL AND approved_at IS NOT NULL)",
            name="ck_p7_manifest_approved_fields",
        ),
    )
    op.create_index("ix_p7_manifest_status_created", "training_dataset_manifests", ["status", "created_at"])

    op.create_table(
        "training_dataset_entries",
        sa.Column("entry_id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("manifest_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("training_dataset_manifests.manifest_id", ondelete="CASCADE"), nullable=False),
        sa.Column("artifact_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("content_generation_artifacts.artifact_id", ondelete="RESTRICT"), nullable=False),
        sa.Column("artifact_hash", sa.String(length=80), nullable=False),
        sa.Column("artifact_version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("scope_id", sa.String(length=80), nullable=False),
        sa.Column("caps_ref", sa.String(length=80), nullable=True),
        sa.Column("language", sa.String(length=12), nullable=False),
        sa.Column("content_layer", sa.String(length=48), nullable=False),
        sa.Column("quality_score", sa.Numeric(precision=5, scale=4), nullable=True),
        sa.Column("caps_alignment_score", sa.Numeric(precision=5, scale=4), nullable=True),
        sa.Column("source_snapshot_hash", sa.String(length=120), nullable=False),
        sa.Column("record_sha256", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("manifest_id", "artifact_id", "artifact_hash", name="uq_p7_manifest_artifact_hash"),
        sa.CheckConstraint("artifact_version > 0", name="ck_p7_entry_version_positive"),
    )
    op.create_index("ix_p7_entry_manifest_language", "training_dataset_entries", ["manifest_id", "language"])
    op.create_index("ix_p7_entry_scope_caps", "training_dataset_entries", ["scope_id", "caps_ref"])

    op.execute(
        """
        CREATE OR REPLACE FUNCTION phase7_prevent_dataset_entry_mutation()
        RETURNS trigger AS $$
        BEGIN
          RAISE EXCEPTION 'training dataset entries are append-only';
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_phase7_dataset_entry_immutable
        BEFORE UPDATE OR DELETE ON training_dataset_entries
        FOR EACH ROW EXECUTE FUNCTION phase7_prevent_dataset_entry_mutation();
        """
    )
    op.execute(
        """
        CREATE OR REPLACE FUNCTION phase7_prevent_approved_manifest_mutation()
        RETURNS trigger AS $$
        BEGIN
          IF OLD.status = 'approved' THEN
            RAISE EXCEPTION 'approved training dataset manifests are immutable';
          END IF;
          RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_phase7_approved_manifest_immutable
        BEFORE UPDATE OR DELETE ON training_dataset_manifests
        FOR EACH ROW EXECUTE FUNCTION phase7_prevent_approved_manifest_mutation();
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_phase7_approved_manifest_immutable ON training_dataset_manifests")
    op.execute("DROP FUNCTION IF EXISTS phase7_prevent_approved_manifest_mutation")
    op.execute("DROP TRIGGER IF EXISTS trg_phase7_dataset_entry_immutable ON training_dataset_entries")
    op.execute("DROP FUNCTION IF EXISTS phase7_prevent_dataset_entry_mutation")
    op.drop_index("ix_p7_entry_scope_caps", table_name="training_dataset_entries")
    op.drop_index("ix_p7_entry_manifest_language", table_name="training_dataset_entries")
    op.drop_table("training_dataset_entries")
    op.drop_index("ix_p7_manifest_status_created", table_name="training_dataset_manifests")
    op.drop_table("training_dataset_manifests")
    op.drop_table("curriculum_expansion_runs")
    op.drop_index("ix_p7_snapshot_scope_captured", table_name="curriculum_coverage_snapshots")
    op.drop_table("curriculum_coverage_snapshots")
