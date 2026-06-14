"""Allow validation reports to reference a task before an artifact exists.

Revision ID: 20260614_0900_phase1_validation_reports
Revises: 20260609_0800_practice_sessions
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260614_0900_phase1_validation_reports"
down_revision = "20260609_0800_practice_sessions"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "content_validation_reports",
        "artifact_id",
        existing_type=postgresql.UUID(as_uuid=True),
        nullable=True,
    )
    op.add_column(
        "content_validation_reports",
        sa.Column("task_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_content_validation_reports_task_id",
        "content_validation_reports",
        "content_generation_tasks",
        ["task_id"],
        ["task_id"],
        ondelete="CASCADE",
    )
    op.create_check_constraint(
        "ck_content_validation_reports_subject_present",
        "content_validation_reports",
        "artifact_id IS NOT NULL OR task_id IS NOT NULL",
    )
    op.create_index(
        "ix_content_validation_reports_task",
        "content_validation_reports",
        ["task_id", "created_at"],
    )


def downgrade() -> None:
    # A downgrade is only safe when all task-only reports have been removed or
    # associated with an artifact. Fail explicitly rather than deleting evidence.
    op.execute(
        """
        DO $$
        BEGIN
          IF EXISTS (
            SELECT 1 FROM content_validation_reports
            WHERE artifact_id IS NULL
          ) THEN
            RAISE EXCEPTION 'Cannot downgrade: task-only validation reports exist';
          END IF;
        END $$;
        """
    )
    op.drop_index("ix_content_validation_reports_task", table_name="content_validation_reports")
    op.drop_constraint(
        "ck_content_validation_reports_subject_present",
        "content_validation_reports",
        type_="check",
    )
    op.drop_constraint(
        "fk_content_validation_reports_task_id",
        "content_validation_reports",
        type_="foreignkey",
    )
    op.drop_column("content_validation_reports", "task_id")
    op.alter_column(
        "content_validation_reports",
        "artifact_id",
        existing_type=postgresql.UUID(as_uuid=True),
        nullable=False,
    )
