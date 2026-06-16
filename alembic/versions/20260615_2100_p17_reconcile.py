"""Phases 1-7 reconciliation controls.

Revision ID: 20260615_2100_p17_reconcile
Revises: 20260615_1800_p7_curriculum
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260615_2100_p17_reconcile"
down_revision = "20260615_1800_p7_curriculum"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "content_answer_key_verifications",
        sa.Column("verification_id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("artifact_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("content_generation_artifacts.artifact_id", ondelete="RESTRICT"), nullable=False),
        sa.Column("artifact_version", sa.Integer(), nullable=False),
        sa.Column("artifact_hash", sa.String(length=80), nullable=False),
        sa.Column("method", sa.String(length=40), nullable=False),
        sa.Column("passed", sa.Boolean(), nullable=False),
        sa.Column("verifier_actor_id", sa.String(length=80), nullable=False),
        sa.Column("verifier_provider", sa.String(length=80), nullable=True),
        sa.Column("verifier_model", sa.String(length=120), nullable=True),
        sa.Column("details", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("idempotency_key", sa.String(length=160), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("artifact_version > 0", name="ck_answer_key_verification_version_positive"),
        sa.CheckConstraint(
            "method IN ('deterministic_recompute','independent_model','educator_recalculation')",
            name="ck_answer_key_verification_method",
        ),
        sa.UniqueConstraint("verifier_actor_id", "idempotency_key", name="uq_answer_key_verification_actor_idempotency"),
    )
    op.create_index(
        "ix_answer_key_verification_artifact_version_created",
        "content_answer_key_verifications",
        ["artifact_id", "artifact_version", "created_at"],
    )
    op.execute(
        """
        CREATE OR REPLACE FUNCTION prevent_answer_key_verification_mutation()
        RETURNS trigger AS $$
        BEGIN
          RAISE EXCEPTION 'answer-key verification records are append-only';
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_answer_key_verification_append_only
        BEFORE UPDATE OR DELETE ON content_answer_key_verifications
        FOR EACH ROW EXECUTE FUNCTION prevent_answer_key_verification_mutation();
        """
    )
    op.add_column(
        "curriculum_coverage_snapshots",
        sa.Column("published_total", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_check_constraint(
        "ck_p7_snapshot_published_nonnegative",
        "curriculum_coverage_snapshots",
        "published_total >= 0",
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_p7_snapshot_published_nonnegative",
        "curriculum_coverage_snapshots",
        type_="check",
    )
    op.drop_column("curriculum_coverage_snapshots", "published_total")
    op.execute("DROP TRIGGER IF EXISTS trg_answer_key_verification_append_only ON content_answer_key_verifications")
    op.execute("DROP FUNCTION IF EXISTS prevent_answer_key_verification_mutation")
    op.drop_index(
        "ix_answer_key_verification_artifact_version_created",
        table_name="content_answer_key_verifications",
    )
    op.drop_table("content_answer_key_verifications")
