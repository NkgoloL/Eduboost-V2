"""Add AL LLM safety fields to lessons.

Revision ID: 20260510_0100
Revises: 20260509_02
Create Date: 2026-05-10
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260510_0100"
down_revision = "20260509_02"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("lessons", sa.Column("caps_ref", sa.String(length=80), nullable=True))
    op.add_column("lessons", sa.Column("term", sa.Integer(), nullable=True))
    op.add_column("lessons", sa.Column("subtopic", sa.String(length=160), nullable=True))
    op.add_column("lessons", sa.Column("learning_objectives", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"))
    op.add_column("lessons", sa.Column("explanation", sa.Text(), nullable=True))
    op.add_column("lessons", sa.Column("worked_examples", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"))
    op.add_column("lessons", sa.Column("practice_questions", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"))
    op.add_column("lessons", sa.Column("answer_key", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"))
    op.add_column("lessons", sa.Column("remediation_hints", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"))
    op.add_column("lessons", sa.Column("difficulty_level", sa.String(length=40), nullable=True))
    op.add_column("lessons", sa.Column("language_level", sa.String(length=40), nullable=True))
    op.add_column("lessons", sa.Column("safety_classification", sa.String(length=40), nullable=False, server_default="requires_review"))
    op.add_column("lessons", sa.Column("pii_check_passed", sa.Boolean(), nullable=False, server_default=sa.text("false")))
    op.add_column("lessons", sa.Column("answer_key_verified", sa.Boolean(), nullable=False, server_default=sa.text("false")))
    op.add_column("lessons", sa.Column("review_status", sa.String(length=40), nullable=False, server_default="ai_generated"))
    op.add_column("lessons", sa.Column("reviewer_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("lessons", sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("lessons", sa.Column("prompt_template_version", sa.String(length=80), nullable=True))
    op.add_column("lessons", sa.Column("provider", sa.String(length=40), nullable=True))
    op.add_column("lessons", sa.Column("model_version", sa.String(length=120), nullable=True))
    op.add_column("lessons", sa.Column("generation_latency_ms", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("lessons", sa.Column("token_usage", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"))
    op.add_column("lessons", sa.Column("variant_type", sa.String(length=40), nullable=False, server_default="standard"))

    op.create_index("ix_lessons_caps_ref", "lessons", ["caps_ref"])
    op.create_index("ix_lessons_review_status", "lessons", ["review_status"])
    op.create_index("ix_lessons_caps_ref_review_status", "lessons", ["caps_ref", "review_status"])
    op.create_check_constraint("ck_lessons_term_range", "lessons", "term IS NULL OR (term >= 1 AND term <= 4)")
    op.create_check_constraint("ck_lessons_generation_latency_non_negative", "lessons", "generation_latency_ms >= 0")


def downgrade() -> None:
    op.drop_constraint("ck_lessons_generation_latency_non_negative", "lessons", type_="check")
    op.drop_constraint("ck_lessons_term_range", "lessons", type_="check")
    op.drop_index("ix_lessons_caps_ref_review_status", table_name="lessons")
    op.drop_index("ix_lessons_review_status", table_name="lessons")
    op.drop_index("ix_lessons_caps_ref", table_name="lessons")
    for column in (
        "variant_type", "token_usage", "generation_latency_ms", "model_version",
        "provider", "prompt_template_version", "reviewed_at", "reviewer_id",
        "review_status", "answer_key_verified", "pii_check_passed",
        "safety_classification", "language_level", "difficulty_level",
        "remediation_hints", "answer_key", "practice_questions",
        "worked_examples", "explanation", "learning_objectives",
        "subtopic", "term", "caps_ref",
    ):
        op.drop_column("lessons", column)
