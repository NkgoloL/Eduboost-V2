"""Add AI/CAPS diagnostics safety metadata.

Revision ID: 20260507_1500
Revises: 20260507_1330
Create Date: 2026-05-07
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "20260507_1500"
down_revision = "20260507_1330"
branch_labels = None
depends_on = None


def upgrade() -> None:
    item_review_status = postgresql.ENUM("draft", "ai_generated", "human_reviewed", "approved", "retired", name="itemreviewstatus")
    item_review_status.create(op.get_bind(), checkfirst=True)

    op.add_column("irt_items", sa.Column("skill", sa.String(length=120), nullable=False, server_default="general"))
    op.add_column("irt_items", sa.Column("caps_reference", sa.String(length=220), nullable=True))
    op.add_column("irt_items", sa.Column("explanation", sa.Text(), nullable=False, server_default="Review the worked solution and compare it with the selected option."))
    op.add_column("irt_items", sa.Column("misconception_tag", sa.String(length=120), nullable=True))
    op.add_column("irt_items", sa.Column("review_status", item_review_status, nullable=False, server_default="ai_generated"))
    op.create_check_constraint("ck_irt_items_skill_not_blank", "irt_items", "length(btrim(skill)) > 0")
    op.create_check_constraint("ck_irt_items_explanation_not_blank", "irt_items", "length(btrim(explanation)) > 0")
    # Existing schema already has ck_irt_items_a_param_positive; retain it and add upper bound.
    op.create_check_constraint("ck_irt_items_a_param_bounds", "irt_items", "a_param > 0 AND a_param <= 4")
    op.create_check_constraint("ck_irt_items_b_param_bounds", "irt_items", "b_param >= -4 AND b_param <= 4")
    op.create_index("ix_irt_items_caps_reference", "irt_items", ["caps_reference"])
    op.create_index("ix_irt_items_review_status", "irt_items", ["review_status"])

    op.add_column("lessons", sa.Column("caps_reference", sa.String(length=220), nullable=True))
    op.add_column("lessons", sa.Column("alignment_confidence", sa.Float(), nullable=False, server_default="0"))
    op.add_column("lessons", sa.Column("quality_score", sa.Float(), nullable=False, server_default="0"))
    op.add_column("lessons", sa.Column("trust_label", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"))
    op.create_check_constraint("ck_lessons_alignment_confidence_range", "lessons", "alignment_confidence >= 0 AND alignment_confidence <= 1")
    op.create_check_constraint("ck_lessons_quality_score_range", "lessons", "quality_score >= 0 AND quality_score <= 1")
    op.create_index("ix_lessons_caps_reference", "lessons", ["caps_reference"])


def downgrade() -> None:
    op.drop_index("ix_lessons_caps_reference", table_name="lessons")
    op.drop_constraint("ck_lessons_quality_score_range", "lessons", type_="check")
    op.drop_constraint("ck_lessons_alignment_confidence_range", "lessons", type_="check")
    op.drop_column("lessons", "trust_label")
    op.drop_column("lessons", "quality_score")
    op.drop_column("lessons", "alignment_confidence")
    op.drop_column("lessons", "caps_reference")

    op.drop_index("ix_irt_items_review_status", table_name="irt_items")
    op.drop_index("ix_irt_items_caps_reference", table_name="irt_items")
    op.drop_constraint("ck_irt_items_b_param_bounds", "irt_items", type_="check")
    op.drop_constraint("ck_irt_items_a_param_bounds", "irt_items", type_="check")
    op.drop_constraint("ck_irt_items_explanation_not_blank", "irt_items", type_="check")
    op.drop_constraint("ck_irt_items_skill_not_blank", "irt_items", type_="check")
    op.drop_column("irt_items", "review_status")
    op.drop_column("irt_items", "misconception_tag")
    op.drop_column("irt_items", "explanation")
    op.drop_column("irt_items", "caps_reference")
    op.drop_column("irt_items", "skill")
    postgresql.ENUM(name="itemreviewstatus").drop(op.get_bind(), checkfirst=True)
