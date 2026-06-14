"""Phase 3 educator consensus and content-governance controls.

Revision ID: 20260614_1500_p3_consensus
Revises: 20260614_1200_p2_retrieval
Create Date: 2026-06-14 15:00:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260614_1500_p3_consensus"
down_revision = "20260614_1200_p2_retrieval"
branch_labels = None
depends_on = None


def upgrade() -> None:
    for value in ("revision_required", "published", "superseded"):
        op.execute(
            f"ALTER TYPE content_artifact_status ADD VALUE IF NOT EXISTS '{value}'"
        )

    op.add_column("content_generation_artifacts", sa.Column("root_artifact_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("content_generation_artifacts", sa.Column("supersedes_artifact_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("content_generation_artifacts", sa.Column("superseded_by_artifact_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("content_generation_artifacts", sa.Column("version_number", sa.Integer(), nullable=False, server_default="1"))
    op.add_column("content_generation_artifacts", sa.Column("row_version", sa.Integer(), nullable=False, server_default="1"))
    op.add_column("content_generation_artifacts", sa.Column("created_by_actor_id", sa.String(length=80), nullable=True))
    op.add_column("content_generation_artifacts", sa.Column("approval_count", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("content_generation_artifacts", sa.Column("review_policy_version", sa.String(length=40), nullable=False, server_default="phase3-v1"))
    op.add_column("content_generation_artifacts", sa.Column("rubric_version", sa.String(length=40), nullable=False, server_default="1.0"))
    op.add_column("content_generation_artifacts", sa.Column("publication_eligible", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("content_generation_artifacts", sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("content_generation_artifacts", sa.Column("published_at", sa.DateTime(timezone=True), nullable=True))
    op.create_foreign_key("fk_content_artifacts_root", "content_generation_artifacts", "content_generation_artifacts", ["root_artifact_id"], ["artifact_id"], ondelete="RESTRICT")
    op.create_foreign_key("fk_content_artifacts_supersedes", "content_generation_artifacts", "content_generation_artifacts", ["supersedes_artifact_id"], ["artifact_id"], ondelete="RESTRICT")
    op.create_foreign_key("fk_content_artifacts_superseded_by", "content_generation_artifacts", "content_generation_artifacts", ["superseded_by_artifact_id"], ["artifact_id"], ondelete="RESTRICT")
    op.create_check_constraint("ck_content_artifacts_version_positive", "content_generation_artifacts", "version_number > 0")
    op.create_check_constraint("ck_content_artifacts_row_version_positive", "content_generation_artifacts", "row_version > 0")
    op.create_check_constraint("ck_content_artifacts_approval_count_non_negative", "content_generation_artifacts", "approval_count >= 0")
    op.create_index("ix_content_artifacts_root_version", "content_generation_artifacts", ["root_artifact_id", "version_number"])

    op.add_column("content_review_assignments", sa.Column("artifact_version", sa.Integer(), nullable=False, server_default="1"))
    op.add_column("content_review_assignments", sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("content_review_assignments", sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("content_review_assignments", sa.Column("reminder_count", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("content_review_assignments", sa.Column("last_reminded_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("content_review_assignments", sa.Column("escalated_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("content_review_assignments", sa.Column("reassigned_from_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key("fk_content_review_assignments_reassigned_from", "content_review_assignments", "content_review_assignments", ["reassigned_from_id"], ["id"], ondelete="RESTRICT")
    op.create_check_constraint("ck_content_review_assignments_reminders_non_negative", "content_review_assignments", "reminder_count >= 0")
    op.add_column("content_review_assignments", sa.Column("conflict_of_interest", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("content_review_assignments", sa.Column("reviewer_competencies", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")))
    op.add_column("content_review_assignments", sa.Column("policy_version", sa.String(length=40), nullable=False, server_default="phase3-v1"))
    op.add_column("content_review_assignments", sa.Column("idempotency_key", sa.String(length=160), nullable=True))
    op.create_unique_constraint("uq_content_review_assignment_artifact_version_reviewer", "content_review_assignments", ["artifact_id", "artifact_version", "assigned_to"])
    op.create_unique_constraint("uq_content_review_assignment_reviewer_idempotency", "content_review_assignments", ["assigned_to", "idempotency_key"])

    op.create_table(
        "content_review_decisions",
        sa.Column("decision_id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.func.gen_random_uuid()),
        sa.Column("artifact_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("content_generation_artifacts.artifact_id", ondelete="RESTRICT"), nullable=False),
        sa.Column("artifact_version", sa.Integer(), nullable=False),
        sa.Column("reviewer_id", sa.String(length=80), nullable=False),
        sa.Column("review_action", postgresql.ENUM(name="content_review_action", create_type=False), nullable=False),
        sa.Column("reason_code", sa.String(length=80), nullable=True),
        sa.Column("comments", sa.Text(), nullable=True),
        sa.Column("rubric_id", sa.String(length=80), nullable=False, server_default="educator-content-review"),
        sa.Column("rubric_version", sa.String(length=40), nullable=False, server_default="1.0"),
        sa.Column("rubric_results", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("policy_version", sa.String(length=40), nullable=False, server_default="phase3-v1"),
        sa.Column("idempotency_key", sa.String(length=160), nullable=False),
        sa.Column("conflict_of_interest", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("reviewer_competencies", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("correlation_id", sa.String(length=120), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("artifact_version > 0", name="ck_content_review_decisions_version_positive"),
        sa.UniqueConstraint("artifact_id", "artifact_version", "reviewer_id", name="uq_content_review_decision_artifact_version_reviewer"),
        sa.UniqueConstraint("reviewer_id", "idempotency_key", name="uq_content_review_decision_reviewer_idempotency"),
    )
    op.create_index("ix_content_review_decisions_artifact_created", "content_review_decisions", ["artifact_id", "created_at"])

    op.create_table(
        "content_state_transition_events",
        sa.Column("event_id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.func.gen_random_uuid()),
        sa.Column("artifact_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("content_generation_artifacts.artifact_id", ondelete="RESTRICT"), nullable=False),
        sa.Column("artifact_version", sa.Integer(), nullable=False),
        sa.Column("previous_status", sa.String(length=40), nullable=False),
        sa.Column("new_status", sa.String(length=40), nullable=False),
        sa.Column("actor_id", sa.String(length=80), nullable=False),
        sa.Column("reason_code", sa.String(length=80), nullable=True),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("triggering_decision_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("content_review_decisions.decision_id", ondelete="RESTRICT"), nullable=True),
        sa.Column("policy_version", sa.String(length=40), nullable=False, server_default="phase3-v1"),
        sa.Column("correlation_id", sa.String(length=120), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("artifact_version > 0", name="ck_content_state_events_version_positive"),
    )
    op.create_index("ix_content_state_events_artifact_created", "content_state_transition_events", ["artifact_id", "created_at"])

    op.execute(
        """
        CREATE OR REPLACE FUNCTION reject_phase3_audit_mutation()
        RETURNS trigger AS $$
        BEGIN
          RAISE EXCEPTION 'Phase 3 review decisions and transition events are append-only';
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    for table in ("content_review_decisions", "content_state_transition_events"):
        op.execute(
            f"""
            CREATE TRIGGER trg_{table}_append_only
            BEFORE UPDATE OR DELETE ON {table}
            FOR EACH ROW EXECUTE FUNCTION reject_phase3_audit_mutation();
            """
        )


def downgrade() -> None:
    for table in ("content_state_transition_events", "content_review_decisions"):
        op.execute(f"DROP TRIGGER IF EXISTS trg_{table}_append_only ON {table}")
    op.execute("DROP FUNCTION IF EXISTS reject_phase3_audit_mutation()")
    op.drop_table("content_state_transition_events")
    op.drop_table("content_review_decisions")

    op.drop_constraint("uq_content_review_assignment_reviewer_idempotency", "content_review_assignments", type_="unique")
    op.drop_constraint("uq_content_review_assignment_artifact_version_reviewer", "content_review_assignments", type_="unique")
    op.drop_constraint("ck_content_review_assignments_reminders_non_negative", "content_review_assignments", type_="check")
    op.drop_constraint("fk_content_review_assignments_reassigned_from", "content_review_assignments", type_="foreignkey")
    for column in ("idempotency_key", "policy_version", "reviewer_competencies", "conflict_of_interest", "reassigned_from_id", "escalated_at", "last_reminded_at", "reminder_count", "completed_at", "accepted_at", "artifact_version"):
        op.drop_column("content_review_assignments", column)

    op.drop_index("ix_content_artifacts_root_version", table_name="content_generation_artifacts")
    for constraint in (
        "ck_content_artifacts_approval_count_non_negative",
        "ck_content_artifacts_row_version_positive",
        "ck_content_artifacts_version_positive",
    ):
        op.drop_constraint(constraint, "content_generation_artifacts", type_="check")
    for constraint in ("fk_content_artifacts_superseded_by", "fk_content_artifacts_supersedes", "fk_content_artifacts_root"):
        op.drop_constraint(constraint, "content_generation_artifacts", type_="foreignkey")
    for column in (
        "published_at", "approved_at", "publication_eligible", "rubric_version",
        "review_policy_version", "approval_count", "created_by_actor_id", "row_version",
        "version_number", "superseded_by_artifact_id", "supersedes_artifact_id", "root_artifact_id",
    ):
        op.drop_column("content_generation_artifacts", column)
    # PostgreSQL enum values are intentionally retained; removing them is unsafe
    # when historical rows or external evidence may still reference them.
