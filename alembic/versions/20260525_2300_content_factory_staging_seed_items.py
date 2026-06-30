"""Add Content Factory staging seed items and artifacts.

Revision ID: 20260525_2300
Revises: 20260525_2200
Create Date: 2026-05-25 23:00:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260525_2300"
down_revision = "20260525_2200"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        "content_staging_seed_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("seed_run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("artifact_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("scope_id", sa.String(length=80), nullable=False),
        sa.Column("caps_ref", sa.String(length=80), nullable=True),
        sa.Column("layer", sa.String(length=80), nullable=False),
        sa.Column("artifact_type", sa.String(length=80), nullable=False),
        sa.Column("target_table", sa.String(length=80), nullable=False),
        sa.Column("target_record_id", sa.String(length=80), nullable=True),
        sa.Column("status", sa.String(length=40), nullable=False, server_default="planned"),
        sa.Column("skip_reason", sa.String(length=255), nullable=True),
        sa.Column("rollback_payload_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("seed_payload_hash", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["artifact_id"], ["content_generation_artifacts.artifact_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["seed_run_id"], ["content_seed_runs.seed_run_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("seed_run_id", "artifact_id", name="uq_content_staging_seed_run_artifact")
    )
    op.create_index("ix_content_staging_seed_items_run", "content_staging_seed_items", ["seed_run_id"])
    op.create_index("ix_content_staging_seed_items_scope_caps_layer", "content_staging_seed_items", ["scope_id", "caps_ref", "layer"])
    op.create_index("ix_content_staging_seed_items_status", "content_staging_seed_items", ["status"])

    op.create_table(
        "content_staging_artifacts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("artifact_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("scope_id", sa.String(length=80), nullable=False),
        sa.Column("caps_ref", sa.String(length=80), nullable=True),
        sa.Column("layer", sa.String(length=80), nullable=False),
        sa.Column("artifact_type", sa.String(length=80), nullable=False),
        sa.Column("payload_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("source_artifact_hash", sa.String(length=64), nullable=True),
        sa.Column("staging_status", sa.String(length=40), nullable=False, server_default="active"),
        sa.Column("created_by_seed_run_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["artifact_id"], ["content_generation_artifacts.artifact_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by_seed_run_id"], ["content_seed_runs.seed_run_id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_index("ix_content_staging_artifacts_scope_caps_layer", "content_staging_artifacts", ["scope_id", "caps_ref", "layer"])
    op.create_index("ix_content_staging_artifacts_status", "content_staging_artifacts", ["staging_status"])

def downgrade() -> None:
    op.drop_table("content_staging_artifacts")
    op.drop_table("content_staging_seed_items")
