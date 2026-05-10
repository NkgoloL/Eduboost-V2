"""Add diagnostics assessment lifecycle and mastery tables.

Revision ID: 20260510_0200
Revises: 20260510_0100
Create Date: 2026-05-10
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260510_0200"
down_revision = "20260510_0100"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("diagnostic_sessions", sa.Column("se_estimate", sa.Float(), nullable=False, server_default="1.0"))
    op.add_column("diagnostic_sessions", sa.Column("session_state", sa.String(length=40), nullable=False, server_default="initialising"))
    op.add_column("diagnostic_sessions", sa.Column("gap_topics", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"))
    op.add_column("diagnostic_sessions", sa.Column("misconception_tags", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"))
    op.add_column("diagnostic_sessions", sa.Column("items_served", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("diagnostic_sessions", sa.Column("theta_history", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"))
    op.create_check_constraint("ck_diagnostic_sessions_se_non_negative", "diagnostic_sessions", "se_estimate >= 0")
    op.create_check_constraint("ck_diagnostic_sessions_items_served_non_negative", "diagnostic_sessions", "items_served >= 0")
    op.create_index("ix_diagnostic_sessions_state", "diagnostic_sessions", ["session_state"])

    op.create_table(
        "topic_mastery",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("learner_id", sa.String(length=36), sa.ForeignKey("learner_profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("caps_ref", sa.String(length=80), nullable=False),
        sa.Column("mastery_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("mastery_label", sa.String(length=40), nullable=False, server_default="needs_practice"),
        sa.Column("theta_estimate", sa.Float(), nullable=True),
        sa.Column("theta_se", sa.Float(), nullable=True),
        sa.Column("last_updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.CheckConstraint("mastery_score >= 0 AND mastery_score <= 1", name="ck_topic_mastery_score_range"),
        sa.UniqueConstraint("learner_id", "caps_ref", name="uq_topic_mastery_learner_caps_ref"),
    )
    op.create_index("ix_topic_mastery_learner", "topic_mastery", ["learner_id"])
    op.create_index("ix_topic_mastery_caps_ref", "topic_mastery", ["caps_ref"])

    op.create_table(
        "mastery_snapshots",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("learner_id", sa.String(length=36), sa.ForeignKey("learner_profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("caps_ref", sa.String(length=80), nullable=False),
        sa.Column("mastery_score", sa.Float(), nullable=False),
        sa.Column("mastery_label", sa.String(length=40), nullable=False),
        sa.Column("theta_estimate", sa.Float(), nullable=True),
        sa.Column("theta_se", sa.Float(), nullable=True),
        sa.Column("practice_accuracy", sa.Float(), nullable=True),
        sa.Column("trigger", sa.String(length=60), nullable=False),
        sa.Column("snapshot_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.CheckConstraint("mastery_score >= 0 AND mastery_score <= 1", name="ck_mastery_snapshots_score_range"),
    )
    op.create_index("ix_mastery_snapshots_learner_caps_ref", "mastery_snapshots", ["learner_id", "caps_ref"])
    op.create_index("ix_mastery_snapshots_at", "mastery_snapshots", ["snapshot_at"])

    op.create_table(
        "practice_queue",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("learner_id", sa.String(length=36), sa.ForeignKey("learner_profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("caps_ref", sa.String(length=80), nullable=False),
        sa.Column("item_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("response", sa.Text(), nullable=True),
        sa.Column("correct", sa.Boolean(), nullable=True),
    )
    op.create_index("ix_practice_queue_learner_due", "practice_queue", ["learner_id", "scheduled_at"])

    op.create_table(
        "spaced_review_schedule",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("learner_id", sa.String(length=36), sa.ForeignKey("learner_profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("caps_ref", sa.String(length=80), nullable=False),
        sa.Column("next_review_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("interval_days", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("easiness_factor", sa.Float(), nullable=False, server_default="2.5"),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.CheckConstraint("interval_days >= 1", name="ck_spaced_review_interval_positive"),
        sa.UniqueConstraint("learner_id", "caps_ref", name="uq_spaced_review_learner_caps_ref"),
    )
    op.create_index("ix_spaced_review_due", "spaced_review_schedule", ["next_review_at"])

    op.create_table(
        "calibration_audits",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("item_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("response_count", sa.Integer(), nullable=False),
        sa.Column("old_parameters", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("new_parameters", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("review_required", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
    )
    op.create_index("ix_calibration_audits_item", "calibration_audits", ["item_id"])


def downgrade() -> None:
    op.drop_index("ix_calibration_audits_item", table_name="calibration_audits")
    op.drop_table("calibration_audits")
    op.drop_index("ix_spaced_review_due", table_name="spaced_review_schedule")
    op.drop_table("spaced_review_schedule")
    op.drop_index("ix_practice_queue_learner_due", table_name="practice_queue")
    op.drop_table("practice_queue")
    op.drop_index("ix_mastery_snapshots_at", table_name="mastery_snapshots")
    op.drop_index("ix_mastery_snapshots_learner_caps_ref", table_name="mastery_snapshots")
    op.drop_table("mastery_snapshots")
    op.drop_index("ix_topic_mastery_caps_ref", table_name="topic_mastery")
    op.drop_index("ix_topic_mastery_learner", table_name="topic_mastery")
    op.drop_table("topic_mastery")
    op.drop_index("ix_diagnostic_sessions_state", table_name="diagnostic_sessions")
    op.drop_constraint("ck_diagnostic_sessions_items_served_non_negative", "diagnostic_sessions", type_="check")
    op.drop_constraint("ck_diagnostic_sessions_se_non_negative", "diagnostic_sessions", type_="check")
    for column in ("theta_history", "items_served", "misconception_tags", "gap_topics", "session_state", "se_estimate"):
        op.drop_column("diagnostic_sessions", column)
