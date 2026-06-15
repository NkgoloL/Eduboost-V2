"""Phase 4 IRT quality and self-healing controls.

Revision ID: 20260615_0900_p4_irt_quality
Revises: 20260614_1500_p3_consensus
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260615_0900_p4_irt_quality"
down_revision = "20260614_1500_p3_consensus"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("diagnostic_items", sa.Column("irt_quality_state", sa.String(32), nullable=False, server_default="uncalibrated"))
    op.add_column("diagnostic_items", sa.Column("irt_model_version", sa.String(64), nullable=True))
    op.add_column("diagnostic_items", sa.Column("irt_policy_version", sa.String(64), nullable=True))
    op.add_column("diagnostic_items", sa.Column("irt_response_count", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("diagnostic_items", sa.Column("irt_unique_learners", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("diagnostic_items", sa.Column("irt_strike_count", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("diagnostic_items", sa.Column("irt_last_calibrated_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("diagnostic_items", sa.Column("irt_last_run_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("diagnostic_items", sa.Column("irt_intervention_reason", sa.String(500), nullable=True))
    op.add_column("diagnostic_items", sa.Column("irt_manual_override_until", sa.DateTime(timezone=True), nullable=True))
    op.add_column("diagnostic_items", sa.Column("irt_manual_override_reason", sa.String(500), nullable=True))
    op.add_column("diagnostic_items", sa.Column("irt_rewrite_artifact_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("diagnostic_items", sa.Column("irt_row_version", sa.Integer(), nullable=False, server_default="1"))
    op.create_check_constraint(
        "ck_diagnostic_items_irt_state",
        "diagnostic_items",
        "irt_quality_state IN ('uncalibrated','healthy','monitor','review_required','quarantined','retired','rewrite_review','overridden')",
    )
    op.create_check_constraint("ck_diagnostic_items_irt_counts", "diagnostic_items", "irt_response_count >= 0 AND irt_unique_learners >= 0 AND irt_strike_count >= 0 AND irt_row_version > 0")
    op.create_foreign_key("fk_diagnostic_items_irt_rewrite_artifact", "diagnostic_items", "content_generation_artifacts", ["irt_rewrite_artifact_id"], ["artifact_id"], ondelete="SET NULL")
    op.create_index("ix_diagnostic_items_irt_quality_state", "diagnostic_items", ["irt_quality_state"])

    op.create_table(
        "irt_calibration_runs",
        sa.Column("run_id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("idempotency_key", sa.String(160), nullable=False, unique=True),
        sa.Column("status", sa.String(32), nullable=False, server_default="running"),
        sa.Column("dry_run", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("model_version", sa.String(64), nullable=False),
        sa.Column("policy_version", sa.String(64), nullable=False),
        sa.Column("requested_by", sa.String(80), nullable=True),
        sa.Column("summary", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("error", postgresql.JSONB(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("status IN ('running','completed','failed')", name="ck_irt_calibration_runs_status"),
    )
    op.create_index("ix_irt_calibration_runs_started", "irt_calibration_runs", ["started_at", "status"])

    op.create_table(
        "irt_calibration_events",
        sa.Column("event_id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("run_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("irt_calibration_runs.run_id", ondelete="RESTRICT"), nullable=False),
        sa.Column("item_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("diagnostic_items.item_id", ondelete="RESTRICT"), nullable=False),
        sa.Column("previous_state", sa.String(32), nullable=False),
        sa.Column("next_state", sa.String(32), nullable=False),
        sa.Column("action", sa.String(40), nullable=False),
        sa.Column("reason", sa.String(500), nullable=False),
        sa.Column("metrics", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("policy_version", sa.String(64), nullable=False),
        sa.Column("model_version", sa.String(64), nullable=False),
        sa.Column("actor_id", sa.String(80), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("run_id", "item_id", name="uq_irt_calibration_event_run_item"),
    )
    op.create_index("ix_irt_calibration_events_item_created", "irt_calibration_events", ["item_id", "created_at"])

    op.execute("""
    CREATE OR REPLACE FUNCTION prevent_irt_calibration_event_mutation()
    RETURNS trigger AS $$
    BEGIN
      RAISE EXCEPTION 'irt_calibration_events is append-only';
    END;
    $$ LANGUAGE plpgsql;
    """)
    op.execute("""
    CREATE TRIGGER trg_irt_calibration_events_append_only
    BEFORE UPDATE OR DELETE ON irt_calibration_events
    FOR EACH ROW EXECUTE FUNCTION prevent_irt_calibration_event_mutation();
    """)


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_irt_calibration_events_append_only ON irt_calibration_events")
    op.execute("DROP FUNCTION IF EXISTS prevent_irt_calibration_event_mutation()")
    op.drop_index("ix_irt_calibration_events_item_created", table_name="irt_calibration_events")
    op.drop_table("irt_calibration_events")
    op.drop_index("ix_irt_calibration_runs_started", table_name="irt_calibration_runs")
    op.drop_table("irt_calibration_runs")
    op.drop_index("ix_diagnostic_items_irt_quality_state", table_name="diagnostic_items")
    op.drop_constraint("fk_diagnostic_items_irt_rewrite_artifact", "diagnostic_items", type_="foreignkey")
    op.drop_constraint("ck_diagnostic_items_irt_counts", "diagnostic_items", type_="check")
    op.drop_constraint("ck_diagnostic_items_irt_state", "diagnostic_items", type_="check")
    for column in (
        "irt_row_version", "irt_rewrite_artifact_id", "irt_manual_override_reason",
        "irt_manual_override_until", "irt_intervention_reason", "irt_last_run_id",
        "irt_last_calibrated_at", "irt_strike_count", "irt_unique_learners",
        "irt_response_count", "irt_policy_version", "irt_model_version", "irt_quality_state",
    ):
        op.drop_column("diagnostic_items", column)
