"""Add educational validation traceability tables (LEV-WS03).

Revision ID: 20260922_1600_educational_validation_traceability
Revises: 20260913_2300_reconcile_consolidation_tables
Create Date: 2026-09-22 16:00:00.000000

Creates append-only telemetry tables:
- lev_interaction_events
- lev_mastery_state_transitions
- lev_validation_runs
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260922_1600_educational_validation_traceability"
down_revision = "20260913_2300_reconcile_consolidation_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. lev_interaction_events
    op.create_table(
        "lev_interaction_events",
        sa.Column("event_id", sa.Uuid(), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("learner_pseudonym", sa.String(length=64), nullable=False),
        sa.Column("concept_id", sa.String(length=128), nullable=False),
        sa.Column("item_id", sa.String(length=128), nullable=False),
        sa.Column("item_version", sa.String(length=32), nullable=False, server_default="1.0"),
        sa.Column("graph_version", sa.String(length=32), nullable=False, server_default="1.0.0"),
        sa.Column("model_version", sa.String(length=32), nullable=False, server_default="lev-1.0"),
        sa.Column("consent_state", sa.String(length=64), nullable=False, server_default="consented"),
        sa.Column("first_attempt_correct", sa.Boolean(), nullable=True),
        sa.Column("attempt_count", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("hint_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("response_latency_ms", sa.Integer(), nullable=True),
        sa.Column("teacher_assistance", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("evidence_type", sa.String(length=32), nullable=False, server_default="synthetic_fixture"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("event_id"),
        sa.CheckConstraint(
            "evidence_type IN ('synthetic_fixture', 'empirical_field')",
            name="ck_lev_interaction_events_evidence_type",
        ),
    )
    op.create_index(
        "ix_lev_events_learner_concept",
        "lev_interaction_events",
        ["learner_pseudonym", "concept_id"],
        unique=False,
    )
    op.create_index(
        "ix_lev_events_occurred",
        "lev_interaction_events",
        ["occurred_at"],
        unique=False,
    )

    # 2. lev_mastery_state_transitions
    op.create_table(
        "lev_mastery_state_transitions",
        sa.Column("transition_id", sa.Uuid(), nullable=False),
        sa.Column("learner_pseudonym", sa.String(length=64), nullable=False),
        sa.Column("concept_id", sa.String(length=128), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("pre_state", sa.JSON(), nullable=False),
        sa.Column("post_state", sa.JSON(), nullable=False),
        sa.Column("evidence_event_ids", sa.JSON(), nullable=False),
        sa.Column("model_version", sa.String(length=32), nullable=False, server_default="lev-1.0"),
        sa.Column("graph_version", sa.String(length=32), nullable=False, server_default="1.0.0"),
        sa.Column("update_rationale", sa.Text(), nullable=False, server_default=""),
        sa.Column("state_hash", sa.String(length=64), nullable=False),
        sa.Column("evidence_type", sa.String(length=32), nullable=False, server_default="synthetic_fixture"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("transition_id"),
        sa.CheckConstraint(
            "evidence_type IN ('synthetic_fixture', 'empirical_field')",
            name="ck_lev_transitions_evidence_type",
        ),
    )
    op.create_index(
        "ix_lev_transitions_learner_concept",
        "lev_mastery_state_transitions",
        ["learner_pseudonym", "concept_id"],
        unique=False,
    )

    # 3. lev_validation_runs
    op.create_table(
        "lev_validation_runs",
        sa.Column("run_id", sa.Uuid(), nullable=False),
        sa.Column("run_type", sa.String(length=64), nullable=False),
        sa.Column("model_version", sa.String(length=32), nullable=False),
        sa.Column("evidence_type", sa.String(length=32), nullable=False, server_default="synthetic_fixture"),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="completed"),
        sa.Column("metrics", sa.JSON(), nullable=False),
        sa.Column("manifest_id", sa.String(length=128), nullable=True),
        sa.Column("executed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("run_id"),
        sa.CheckConstraint(
            "evidence_type IN ('synthetic_fixture', 'empirical_field')",
            name="ck_lev_validation_runs_evidence_type",
        ),
    )
    op.create_index(
        "ix_lev_validation_runs_type_status",
        "lev_validation_runs",
        ["run_type", "status"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_table("lev_validation_runs")
    op.drop_table("lev_mastery_state_transitions")
    op.drop_table("lev_interaction_events")
