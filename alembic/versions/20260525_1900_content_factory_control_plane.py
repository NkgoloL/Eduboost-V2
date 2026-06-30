"""Content Factory control plane expansion.

Revision ID: 20260525_1900
Revises: 20260525_1531
Create Date: 2026-05-25 19:00:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260525_1900"
down_revision = "20260525_1531"
branch_labels = None
depends_on = None


def upgrade() -> None:
    for column in (
        sa.Column("attempt_number", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("max_attempts", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("idempotency_key", sa.String(length=160), nullable=True),
        sa.Column("depends_on_task_ids", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("input_artifact_ids", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("output_artifact_ids", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("provider", sa.String(length=80), nullable=True),
        sa.Column("model", sa.String(length=120), nullable=True),
        sa.Column("prompt_version", sa.String(length=80), nullable=True),
        sa.Column("token_usage", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("cost_metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("validation_failures", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("artifact_paths", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("locked_by", sa.String(length=120), nullable=True),
        sa.Column("lock_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("admin_actor_id", sa.String(length=80), nullable=True),
    ):
        op.add_column("content_generation_tasks", column)
    op.create_unique_constraint("uq_content_generation_tasks_idempotency_key", "content_generation_tasks", ["idempotency_key"])
    op.alter_column("content_generation_tasks", "status", server_default="queued")

    for column in (
        sa.Column("source_title", sa.String(length=240), nullable=True),
        sa.Column("source_type", sa.String(length=80), nullable=True),
        sa.Column("source_uri", sa.String(length=500), nullable=True),
        sa.Column("citation_text", sa.Text(), nullable=True),
        sa.Column("caps_ref", sa.String(length=80), nullable=True),
        sa.Column("grade", sa.Integer(), nullable=True),
        sa.Column("subject_code", sa.String(length=20), nullable=True),
        sa.Column("language", sa.String(length=8), nullable=True),
        sa.Column("license_status", sa.String(length=80), nullable=True),
        sa.Column("source_quality_score", sa.Numeric(precision=5, scale=4), nullable=True),
        sa.Column("etl_version", sa.String(length=80), nullable=True),
        sa.Column("document_version_id", sa.String(length=120), nullable=True),
        sa.Column("chunk_hash", sa.String(length=120), nullable=True),
    ):
        op.add_column("content_artifact_sources", column)

    _add_blueprint_template_columns("assessment_blueprints")
    _add_blueprint_template_columns("study_plan_templates")


def downgrade() -> None:
    _drop_blueprint_template_columns("study_plan_templates")
    _drop_blueprint_template_columns("assessment_blueprints")
    for column_name in (
        "chunk_hash", "document_version_id", "etl_version", "source_quality_score", "license_status", "language",
        "subject_code", "grade", "caps_ref", "citation_text", "source_uri", "source_type", "source_title",
    ):
        op.drop_column("content_artifact_sources", column_name)
    op.drop_constraint("uq_content_generation_tasks_idempotency_key", "content_generation_tasks", type_="unique")
    for column_name in (
        "admin_actor_id", "finished_at", "started_at", "lock_expires_at", "locked_by", "artifact_paths",
        "validation_failures", "cost_metadata", "token_usage", "prompt_version", "model", "provider",
        "output_artifact_ids", "input_artifact_ids", "depends_on_task_ids", "idempotency_key", "max_attempts", "attempt_number",
    ):
        op.drop_column("content_generation_tasks", column_name)
    op.alter_column("content_generation_tasks", "status", server_default="pending")


def _add_blueprint_template_columns(table_name: str) -> None:
    for column in (
        sa.Column("caps_ref", sa.String(length=80), nullable=True),
        sa.Column("grade", sa.Integer(), nullable=True),
        sa.Column("subject_code", sa.String(length=20), nullable=True),
        sa.Column("language", sa.String(length=8), nullable=False, server_default="en"),
        sa.Column("title", sa.String(length=240), nullable=True),
        sa.Column("referenced_artifact_ids", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("review_status", sa.String(length=40), nullable=False, server_default="draft"),
        sa.Column("validation_status", sa.String(length=40), nullable=False, server_default="pending"),
        sa.Column("created_by_run_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("content_generation_runs.run_id"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    ):
        op.add_column(table_name, column)


def _drop_blueprint_template_columns(table_name: str) -> None:
    for column_name in (
        "updated_at", "created_by_run_id", "validation_status", "review_status", "referenced_artifact_ids",
        "title", "language", "subject_code", "grade", "caps_ref",
    ):
        op.drop_column(table_name, column_name)
