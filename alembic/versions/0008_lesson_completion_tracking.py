"""Track lesson completion timestamps for parent reporting and offline sync.

Revision ID: 0008_lesson_completion_tracking
Revises: 0007_caps_irt_item_bank
Create Date: 2026-05-04
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0008_lesson_completion_tracking"
down_revision = "0007_caps_irt_item_bank"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("lessons", sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("lessons", "completed_at")
