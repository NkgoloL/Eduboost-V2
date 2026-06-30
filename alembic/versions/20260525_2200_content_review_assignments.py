"""Add Content Factory review assignments.

Revision ID: 20260525_2200
Revises: 20260525_2100
Create Date: 2026-05-25 22:00:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260525_2200"
down_revision = "20260525_2100"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "content_review_assignments",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("artifact_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("assigned_to", sa.String(length=80), nullable=False),
        sa.Column("assigned_by", sa.String(length=80), nullable=False),
        sa.Column("assigned_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("due_by", sa.DateTime(timezone=True), nullable=True),
        sa.Column("priority", sa.String(length=20), nullable=False, server_default="normal"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="assigned"),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["artifact_id"], ["content_generation_artifacts.artifact_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_content_review_assignments_reviewer_status", "content_review_assignments", ["assigned_to", "status"])
    op.create_index("ix_content_review_assignments_artifact_status", "content_review_assignments", ["artifact_id", "status"])


def downgrade() -> None:
    op.drop_index("ix_content_review_assignments_artifact_status", table_name="content_review_assignments")
    op.drop_index("ix_content_review_assignments_reviewer_status", table_name="content_review_assignments")
    op.drop_table("content_review_assignments")
