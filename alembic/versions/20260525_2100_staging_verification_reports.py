"""Persist Content Factory staging verification reports.

Revision ID: 20260525_2100
Revises: 20260525_1900
Create Date: 2026-05-25 21:00:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260525_2100"
down_revision = "20260525_1900"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "content_staging_verification_runs",
        sa.Column("run_id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("status", sa.String(length=40), nullable=False, server_default="completed"),
        sa.Column("summary_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_by", sa.String(length=80), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("run_id"),
    )
    op.create_table(
        "content_staging_verification_scope_results",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("scope_id", sa.String(length=80), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("can_seed_staging", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("can_promote_production", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("summary_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("blockers_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("created_by", sa.String(length=80), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["run_id"], ["content_staging_verification_runs.run_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("run_id", "scope_id", name="uq_content_staging_verification_run_scope"),
    )
    op.create_index(
        "ix_content_staging_verification_scope_status",
        "content_staging_verification_scope_results",
        ["scope_id", "status"],
    )


def downgrade() -> None:
    op.drop_index("ix_content_staging_verification_scope_status", table_name="content_staging_verification_scope_results")
    op.drop_table("content_staging_verification_scope_results")
    op.drop_table("content_staging_verification_runs")
