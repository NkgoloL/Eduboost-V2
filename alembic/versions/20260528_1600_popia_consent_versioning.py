"""POPIA consent versioning implementation.

Adds consent version history table for tracking consent lifecycle
and policy version changes per POPIA compliance requirements.

Revision ID: 20260528_1600
Revises: 20260526_0300
Create Date: 2026-05-28 16:00:00.000000

"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260528_1600"
down_revision = "20260526_0300"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create consent_version_history table
    op.create_table(
        "consent_version_history",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("consent_id", sa.String(36), sa.ForeignKey("parental_consents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("policy_version", sa.String(20), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("granted_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("transition_reason", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Index("ix_consent_version_history_consent_id", "consent_id"),
        sa.Index("ix_consent_version_history_created_at", "created_at"),
    )

    # Add comment to table
    op.execute(
        """
        COMMENT ON TABLE consent_version_history IS
        'POPIA consent version history for tracking consent lifecycle and policy version changes';
        """
    )


def downgrade() -> None:
    op.drop_table("consent_version_history")
