"""Phase 2.2 — Add durable practice_sessions table to replace in-memory _SESSIONS dict

Revision ID: 20260609_0800_practice_sessions
Revises: 20260605_0500_fix_migration_graph
Create Date: 2026-06-09 08:00:00

This migration:
1. Creates practice_sessions table with all required fields
2. Adds indexes for efficient querying (learner_id, expires_at)
3. Adds constraints for data integrity (cursor >= 0, expires_at > created_at)

The practice_sessions table is designed for durability across process restarts
and multi-worker consistency. Sessions auto-expire after 24 hours and can be
cleaned up via a background job.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260609_0800_practice_sessions"
down_revision = "f2faf5aa12fd"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "practice_sessions",
        sa.Column("id", sa.String(length=36), nullable=False, comment="Session UUID (string)"),
        sa.Column(
            "learner_id",
            sa.String(length=36),
            sa.ForeignKey("learner_profiles.id", ondelete="CASCADE"),
            nullable=False,
            comment="FK to learner_profiles; learner participating in practice",
        ),
        sa.Column(
            "owner_subject",
            sa.String(length=256),
            nullable=False,
            comment="User ID/subject who created this session (for authorization check)",
        ),
        sa.Column(
            "items",
            postgresql.JSONB(),
            nullable=False,
            server_default="[]",
            comment="List of item IDs (UUIDs as strings) in sequence",
        ),
        sa.Column(
            "cursor",
            sa.Integer(),
            nullable=False,
            server_default="0",
            comment="Current position in items list (0-indexed)",
        ),
        sa.Column(
            "responses",
            postgresql.JSONB(),
            nullable=False,
            server_default="[]",
            comment="List of response objects: [item_id, correct, response, ...]",
        ),
        sa.Column(
            "gap_topics",
            postgresql.JSONB(),
            nullable=False,
            server_default="[]",
            comment="List of CAPS references (gap_topics) for this practice session",
        ),
        sa.Column(
            "theta",
            sa.Float(),
            nullable=False,
            server_default="0.0",
            comment="IRT ability estimate at session creation",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
            comment="Timestamp when session was created",
        ),
        sa.Column(
            "expires_at",
            sa.DateTime(timezone=True),
            nullable=False,
            comment="Auto-expiry timestamp; cleanup job should delete after this time",
        ),
        sa.Column(
            "completed_at",
            sa.DateTime(timezone=True),
            nullable=True,
            comment="Timestamp when session was completed (if applicable)",
        ),
        sa.CheckConstraint("cursor >= 0", name="ck_practice_sessions_cursor_non_negative"),
        sa.CheckConstraint("expires_at > created_at", name="ck_practice_sessions_expiry_after_creation"),
        sa.PrimaryKeyConstraint("id", name="pk_practice_sessions"),
    )

    # Indexes for efficient querying and cleanup
    op.create_index(
        "ix_practice_sessions_learner",
        "practice_sessions",
        ["learner_id"],
        unique=False,
    )
    op.create_index(
        "ix_practice_sessions_expires_at",
        "practice_sessions",
        ["expires_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_practice_sessions_expires_at", table_name="practice_sessions")
    op.drop_index("ix_practice_sessions_learner", table_name="practice_sessions")
    op.drop_table("practice_sessions")
