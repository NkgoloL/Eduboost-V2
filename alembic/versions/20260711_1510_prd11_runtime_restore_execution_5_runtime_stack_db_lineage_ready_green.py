"""PRD-11 runtime restore execution 5 readiness schema bridge.

This migration closes the gap between the live runtime schema and the
PRD-11.0R execution-5 readiness contract by:

- adding the assessment/study-plan tables required by the runtime contract
- adding compatibility columns expected by the runtime schema verifier
- backfilling the compatibility columns from the existing model columns where
  possible so fresh disposable stacks start in a coherent state
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260711_1510_prd11_runtime_green_exec5"
down_revision = "20260708_2100_prd2_runtime_kg"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "assessments",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("subject_code", sa.String(length=20), nullable=False),
        sa.Column("grade_level", sa.Integer(), nullable=False),
        sa.Column("assessment_type", sa.String(length=50), nullable=False),
        sa.Column("total_marks", sa.Integer(), nullable=False),
        sa.Column("questions", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("passing_score", sa.Integer(), nullable=False, server_default="50"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_assessments_subject_code", "assessments", ["subject_code"])
    op.create_index("ix_assessments_grade_level", "assessments", ["grade_level"])

    op.create_table(
        "assessment_attempts",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("learner_id", sa.String(length=36), sa.ForeignKey("learner_profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("assessment_id", sa.String(length=36), sa.ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("marks_obtained", sa.Integer(), nullable=False),
        sa.Column("time_taken_seconds", sa.Integer(), nullable=False),
        sa.Column("responses", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_assessment_attempts_learner_id", "assessment_attempts", ["learner_id"])
    op.create_index("ix_assessment_attempts_assessment_id", "assessment_attempts", ["assessment_id"])

    op.create_table(
        "study_plans",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("learner_id", sa.String(length=36), sa.ForeignKey("learner_profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("week_start", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("schedule", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("gap_ratio", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("week_focus", sa.String(length=200), nullable=False),
        sa.Column("generated_by", sa.String(length=50), nullable=False, server_default="V2_ALGORITHM"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_study_plans_learner_id", "study_plans", ["learner_id"])

    op.add_column("diagnostic_items", sa.Column("irt_discrimination", sa.Float(), nullable=True))
    op.add_column("diagnostic_items", sa.Column("irt_difficulty", sa.Float(), nullable=True))
    op.add_column("diagnostic_items", sa.Column("irt_guessing", sa.Float(), nullable=True))

    op.execute(
        """
        UPDATE diagnostic_items
        SET
            irt_discrimination = discrimination_a,
            irt_difficulty = difficulty_b,
            irt_guessing = guessing_c
        WHERE irt_discrimination IS NULL
           OR irt_difficulty IS NULL
           OR irt_guessing IS NULL
        """
    )

    op.add_column("runtime_kg_edges", sa.Column("source_node_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("runtime_kg_edges", sa.Column("target_node_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.execute(
        """
        UPDATE runtime_kg_edges
        SET
            source_node_id = from_node_id,
            target_node_id = to_node_id
        WHERE source_node_id IS NULL
           OR target_node_id IS NULL
        """
    )
    op.create_foreign_key(
        "fk_runtime_kg_edges_source_node_id",
        "runtime_kg_edges",
        "runtime_kg_nodes",
        ["source_node_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "fk_runtime_kg_edges_target_node_id",
        "runtime_kg_edges",
        "runtime_kg_nodes",
        ["target_node_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_index("ix_runtime_kg_edges_source_node_id", "runtime_kg_edges", ["source_node_id"])
    op.create_index("ix_runtime_kg_edges_target_node_id", "runtime_kg_edges", ["target_node_id"])


def downgrade() -> None:
    op.drop_index("ix_runtime_kg_edges_target_node_id", table_name="runtime_kg_edges")
    op.drop_index("ix_runtime_kg_edges_source_node_id", table_name="runtime_kg_edges")
    op.drop_constraint("fk_runtime_kg_edges_target_node_id", "runtime_kg_edges", type_="foreignkey")
    op.drop_constraint("fk_runtime_kg_edges_source_node_id", "runtime_kg_edges", type_="foreignkey")
    op.drop_column("runtime_kg_edges", "target_node_id")
    op.drop_column("runtime_kg_edges", "source_node_id")

    op.drop_column("diagnostic_items", "irt_guessing")
    op.drop_column("diagnostic_items", "irt_difficulty")
    op.drop_column("diagnostic_items", "irt_discrimination")

    op.drop_index("ix_study_plans_learner_id", table_name="study_plans")
    op.drop_table("study_plans")

    op.drop_index("ix_assessment_attempts_assessment_id", table_name="assessment_attempts")
    op.drop_index("ix_assessment_attempts_learner_id", table_name="assessment_attempts")
    op.drop_table("assessment_attempts")

    op.drop_index("ix_assessments_grade_level", table_name="assessments")
    op.drop_index("ix_assessments_subject_code", table_name="assessments")
    op.drop_table("assessments")
