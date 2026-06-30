"""POPIA erasure request state machine implementation.

Adds erasure_request table for tracking POPIA Right to Erasure workflow
with explicit state machine and safety checks.

Revision ID: 20260528_1700
Revises: 20260528_1600
Create Date: 2026-05-28 17:00:00.000000

"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260528_1700"
down_revision = "20260528_1600"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create erasure_request table
    op.create_table(
        "erasure_request",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("learner_id", sa.String(36), sa.ForeignKey("learner_profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("requester_id", sa.String(36), nullable=False),
        sa.Column("requester_role", sa.String(20), nullable=False),  # guardian, admin, data_subject
        sa.Column("state", sa.String(20), nullable=False, default="requested"),  # requested, verified, scheduled, cancelled, executed, failed
        sa.Column("reason", sa.String(255), nullable=True),
        sa.Column("legal_basis", sa.String(100), nullable=True),
        sa.Column("export_offered", sa.Boolean, nullable=False, default=False),
        sa.Column("export_waived", sa.Boolean, nullable=False, default=False),
        sa.Column("legal_hold", sa.Boolean, nullable=False, default=False),
        sa.Column("grace_period_end_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("executed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("execution_method", sa.String(20), nullable=True),  # soft, physical, purge
        sa.Column("preflight_result", sa.JSON, nullable=True),
        sa.Column("postflight_result", sa.JSON, nullable=True),
        sa.Column("admin_override", sa.Boolean, nullable=False, default=False),
        sa.Column("admin_override_reason", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Index("ix_erasure_request_learner_id", "learner_id"),
        sa.Index("ix_erasure_request_state", "state"),
        sa.Index("ix_erasure_request_grace_period_end", "grace_period_end_at"),
    )

    # Add comment to table
    op.execute(
        """
        COMMENT ON TABLE erasure_request IS
        'POPIA Right to Erasure request state machine with safety checks and audit trail';
        """
    )


def downgrade() -> None:
    op.drop_table("erasure_request")
