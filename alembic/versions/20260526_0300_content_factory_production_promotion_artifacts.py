"""Add Content Factory production promotion artifacts.

Revision ID: 20260526_0300
Revises: 20260525_2300
Create Date: 2026-05-26 03:00:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260526_0300"
down_revision = "20260525_2300"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        "content_production_artifacts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("artifact_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("staging_artifact_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("scope_id", sa.String(length=80), nullable=False),
        sa.Column("caps_ref", sa.String(length=80), nullable=True),
        sa.Column("layer", sa.String(length=80), nullable=False),
        sa.Column("artifact_type", sa.String(length=80), nullable=False),
        sa.Column("payload_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("source_artifact_hash", sa.String(length=64), nullable=True),
        sa.Column("production_status", sa.String(length=40), nullable=False, server_default="active"),
        sa.Column("created_by_promotion_event_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["artifact_id"], ["content_generation_artifacts.artifact_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["staging_artifact_id"], ["content_staging_artifacts.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["created_by_promotion_event_id"], ["content_promotion_events.promotion_event_id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("created_by_promotion_event_id", "artifact_id", name="uq_content_production_promotion_artifact")
    )
    op.create_index("ix_content_production_artifacts_scope_caps_layer", "content_production_artifacts", ["scope_id", "caps_ref", "layer"])
    op.create_index("ix_content_production_artifacts_status", "content_production_artifacts", ["production_status"])
    op.create_index("ix_content_production_artifacts_promotion_event", "content_production_artifacts", ["created_by_promotion_event_id"])

def downgrade() -> None:
    op.drop_table("content_production_artifacts")
