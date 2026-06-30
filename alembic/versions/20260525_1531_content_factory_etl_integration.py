"""Content Factory ETL provenance integration.

Revision ID: 20260525_1531
Revises: 20260524_1800
Create Date: 2026-05-25 15:31:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260525_1531"
down_revision = "20260524_1800"
branch_labels = None
depends_on = None


content_scope_status = postgresql.ENUM("draft", "active", "paused", "retired", name="content_scope_status", create_type=False)
content_layer = postgresql.ENUM("diagnostic_items", "lessons", "assessment_blueprints", "study_plan_templates", name="content_layer", create_type=False)
content_artifact_type = postgresql.ENUM("diagnostic_item", "lesson", "assessment_blueprint", "study_plan_template", "rubric", "remediation_path", name="content_artifact_type", create_type=False)
content_artifact_status = postgresql.ENUM(
    "draft",
    "generated",
    "validation_failed",
    "pending_review",
    "approved",
    "seeded_staging",
    "promoted_production",
    "retired",
    "rejected",
    "quarantined",
    "generation_failed",
    name="content_artifact_status",
    create_type=False,
)
content_review_action = postgresql.ENUM("approve", "reject", "quarantine", "request_changes", name="content_review_action", create_type=False)


def upgrade() -> None:
    bind = op.get_bind()
    for enum in (
        content_scope_status,
        content_layer,
        content_artifact_type,
        content_artifact_status,
        content_review_action,
    ):
        enum.create(bind, checkfirst=True)

    op.create_table(
        "content_scopes",
        sa.Column("scope_id", sa.String(length=80), primary_key=True),
        sa.Column("grade", sa.Integer(), nullable=False),
        sa.Column("subject_code", sa.String(length=20), nullable=False),
        sa.Column("subject_slug", sa.String(length=80), nullable=False),
        sa.Column("subject_display_name", sa.String(length=120), nullable=False),
        sa.Column("language", sa.String(length=8), nullable=False, server_default="en"),
        sa.Column("curriculum", sa.String(length=40), nullable=False, server_default="CAPS"),
        sa.Column("status", content_scope_status, nullable=False, server_default="active"),
        sa.Column("source_policy", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("targets", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("grade >= 0 AND grade <= 12", name="ck_content_scopes_grade_range"),
    )
    op.create_index("ix_content_scopes_grade_subject_language", "content_scopes", ["grade", "subject_code", "language"])

    op.create_table(
        "content_coverage_targets",
        sa.Column("target_id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("scope_id", sa.String(length=80), sa.ForeignKey("content_scopes.scope_id", ondelete="CASCADE"), nullable=False),
        sa.Column("caps_ref", sa.String(length=80), nullable=False),
        sa.Column("content_layer", content_layer, nullable=False),
        sa.Column("target_count", sa.Integer(), nullable=False),
        sa.Column("minimum_approved_sources", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("target_count >= 0", name="ck_content_coverage_targets_count_non_negative"),
        sa.UniqueConstraint("scope_id", "caps_ref", "content_layer", name="uq_content_coverage_target_scope_caps_layer"),
    )

    op.create_table(
        "content_generation_runs",
        sa.Column("run_id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("scope_id", sa.String(length=80), sa.ForeignKey("content_scopes.scope_id"), nullable=False),
        sa.Column("requested_by", sa.String(length=80), nullable=True),
        sa.Column("status", sa.String(length=40), nullable=False, server_default="draft"),
        sa.Column("provider", sa.String(length=80), nullable=True),
        sa.Column("model", sa.String(length=120), nullable=True),
        sa.Column("prompt_version", sa.String(length=80), nullable=True),
        sa.Column("run_metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "content_generation_tasks",
        sa.Column("task_id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("run_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("content_generation_runs.run_id", ondelete="CASCADE"), nullable=False),
        sa.Column("scope_id", sa.String(length=80), nullable=False),
        sa.Column("caps_ref", sa.String(length=80), nullable=True),
        sa.Column("content_layer", content_layer, nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False, server_default="pending"),
        sa.Column("task_metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_content_generation_tasks_run_status", "content_generation_tasks", ["run_id", "status"])

    op.create_table(
        "content_generation_artifacts",
        sa.Column("artifact_id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("run_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("content_generation_runs.run_id"), nullable=True),
        sa.Column("task_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("content_generation_tasks.task_id"), nullable=True),
        sa.Column("scope_id", sa.String(length=80), nullable=False),
        sa.Column("content_layer", content_layer, nullable=False),
        sa.Column("artifact_type", content_artifact_type, nullable=False),
        sa.Column("caps_ref", sa.String(length=80), nullable=True),
        sa.Column("grade", sa.Integer(), nullable=True),
        sa.Column("subject_code", sa.String(length=20), nullable=True),
        sa.Column("language", sa.String(length=8), nullable=True),
        sa.Column("status", content_artifact_status, nullable=False, server_default="generated"),
        sa.Column("artifact_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("artifact_hash", sa.String(length=80), nullable=False, unique=True),
        sa.Column("schema_version", sa.String(length=40), nullable=False, server_default="1.0"),
        sa.Column("source_snapshot_hash", sa.String(length=120), nullable=True),
        sa.Column("provider", sa.String(length=80), nullable=True),
        sa.Column("model", sa.String(length=120), nullable=True),
        sa.Column("prompt_version", sa.String(length=80), nullable=True),
        sa.Column("token_usage", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("cost_metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("quality_score", sa.Numeric(precision=5, scale=4), nullable=True),
        sa.Column("safety_status", sa.String(length=40), nullable=True),
        sa.Column("answer_key_verified", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("caps_alignment_score", sa.Numeric(precision=5, scale=4), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("grade IS NULL OR (grade >= 0 AND grade <= 12)", name="ck_content_artifacts_grade_range"),
        sa.CheckConstraint("quality_score IS NULL OR (quality_score >= 0 AND quality_score <= 1)", name="ck_content_artifacts_quality_range"),
        sa.CheckConstraint("caps_alignment_score IS NULL OR (caps_alignment_score >= 0 AND caps_alignment_score <= 1)", name="ck_content_artifacts_caps_alignment_range"),
    )
    op.create_index("ix_content_artifacts_scope_caps_layer", "content_generation_artifacts", ["scope_id", "caps_ref", "content_layer"])
    op.create_index("ix_content_generation_artifacts_status", "content_generation_artifacts", ["status"])

    op.create_table(
        "content_artifact_sources",
        sa.Column("source_id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("artifact_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("content_generation_artifacts.artifact_id", ondelete="CASCADE"), nullable=False),
        sa.Column("source_document_id", sa.String(length=120), nullable=False),
        sa.Column("source_chunk_id", sa.String(length=120), nullable=True),
        sa.Column("curriculum_mapping_id", sa.String(length=120), nullable=True),
        sa.Column("source_hash", sa.String(length=120), nullable=True),
        sa.Column("source_role", sa.String(length=40), nullable=False, server_default="primary_context"),
        sa.Column("source_metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_content_artifact_sources_document_chunk", "content_artifact_sources", ["source_document_id", "source_chunk_id"])

    op.create_table(
        "content_validation_reports",
        sa.Column("validation_report_id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("artifact_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("content_generation_artifacts.artifact_id", ondelete="CASCADE"), nullable=False),
        sa.Column("passed", sa.Boolean(), nullable=False),
        sa.Column("checks", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("errors", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_content_validation_reports_artifact", "content_validation_reports", ["artifact_id", "created_at"])

    op.create_table(
        "content_artifact_reviews",
        sa.Column("review_id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("artifact_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("content_generation_artifacts.artifact_id", ondelete="CASCADE"), nullable=False),
        sa.Column("reviewer_id", sa.String(length=80), nullable=True),
        sa.Column("review_action", content_review_action, nullable=False),
        sa.Column("review_reason", sa.Text(), nullable=True),
        sa.Column("quality_score", sa.Numeric(precision=5, scale=4), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "content_seed_runs",
        sa.Column("seed_run_id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("scope_id", sa.String(length=80), nullable=False),
        sa.Column("dry_run", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("status", sa.String(length=40), nullable=False, server_default="pending"),
        sa.Column("summary", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "content_promotion_events",
        sa.Column("promotion_event_id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("artifact_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("content_generation_artifacts.artifact_id"), nullable=False),
        sa.Column("promoted_table", sa.String(length=80), nullable=False),
        sa.Column("promoted_record_id", sa.String(length=120), nullable=False),
        sa.Column("promoted_by", sa.String(length=80), nullable=True),
        sa.Column("promoted_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("rollback_metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
    )

    op.create_table(
        "lesson_bank",
        sa.Column("lesson_id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("artifact_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("content_generation_artifacts.artifact_id"), nullable=False),
        sa.Column("scope_id", sa.String(length=80), nullable=False),
        sa.Column("caps_ref", sa.String(length=80), nullable=False),
        sa.Column("grade", sa.Integer(), nullable=False),
        sa.Column("subject_code", sa.String(length=20), nullable=False),
        sa.Column("language", sa.String(length=8), nullable=False),
        sa.Column("title", sa.String(length=240), nullable=False),
        sa.Column("lesson_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("content_hash", sa.String(length=80), nullable=False, unique=True),
        sa.Column("review_status", sa.String(length=40), nullable=False),
        sa.Column("safety_status", sa.String(length=40), nullable=False),
        sa.Column("quality_score", sa.Numeric(precision=5, scale=4), nullable=True),
        sa.Column("source_snapshot_hash", sa.String(length=120), nullable=True),
        sa.Column("promoted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("grade >= 0 AND grade <= 12", name="ck_lesson_bank_grade_range"),
    )
    op.create_index("ix_lesson_bank_scope_caps", "lesson_bank", ["scope_id", "caps_ref"])

    op.create_table(
        "assessment_blueprints",
        sa.Column("blueprint_id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("artifact_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("content_generation_artifacts.artifact_id"), nullable=False),
        sa.Column("scope_id", sa.String(length=80), nullable=False),
        sa.Column("blueprint_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False, server_default="approved"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "study_plan_templates",
        sa.Column("template_id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("artifact_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("content_generation_artifacts.artifact_id"), nullable=False),
        sa.Column("scope_id", sa.String(length=80), nullable=False),
        sa.Column("template_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False, server_default="approved"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("study_plan_templates")
    op.drop_table("assessment_blueprints")
    op.drop_index("ix_lesson_bank_scope_caps", table_name="lesson_bank")
    op.drop_table("lesson_bank")
    op.drop_table("content_promotion_events")
    op.drop_table("content_seed_runs")
    op.drop_table("content_artifact_reviews")
    op.drop_index("ix_content_validation_reports_artifact", table_name="content_validation_reports")
    op.drop_table("content_validation_reports")
    op.drop_index("ix_content_artifact_sources_document_chunk", table_name="content_artifact_sources")
    op.drop_table("content_artifact_sources")
    op.drop_index("ix_content_generation_artifacts_status", table_name="content_generation_artifacts")
    op.drop_index("ix_content_artifacts_scope_caps_layer", table_name="content_generation_artifacts")
    op.drop_table("content_generation_artifacts")
    op.drop_index("ix_content_generation_tasks_run_status", table_name="content_generation_tasks")
    op.drop_table("content_generation_tasks")
    op.drop_table("content_generation_runs")
    op.drop_table("content_coverage_targets")
    op.drop_index("ix_content_scopes_grade_subject_language", table_name="content_scopes")
    op.drop_table("content_scopes")

    bind = op.get_bind()
    for enum in (
        content_review_action,
        content_artifact_status,
        content_artifact_type,
        content_layer,
        content_scope_status,
    ):
        enum.drop(bind, checkfirst=True)
