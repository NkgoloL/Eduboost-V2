"""
P1-03 — Alembic migration 0010: item_exposures table
=====================================================
Place this file at:
    alembic/versions/0010_add_item_exposures_table.py

Depends on: 0009 (diagnostic_items table — must already exist).

Purpose:
    Records every time a diagnostic item is served to a learner in a session.
    This enables:
      • Per-learner exposure de-duplication (same item not served twice per session)
      • Cross-session exposure cooling (configurable cooldown window)
      • Per-item exposure count (mirrors diagnostic_items.exposure_count for fast queries)
      • Audit trail for item usage

Rollback notes:
    Drop the table.  No existing data is modified.  Safe at any point before
    live diagnostic sessions have run.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "20260509_02"
down_revision = "20260509_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "item_exposures",

        # --- Identity --------------------------------------------------
        sa.Column(
            "id",
            sa.BigInteger,
            primary_key=True,
            autoincrement=True,
            comment="Surrogate key — use for pagination; never exposed to learners",
        ),

        # --- Foreign keys ---------------------------------------------
        sa.Column(
            "item_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            comment="FK → diagnostic_items.item_id",
        ),
        sa.Column(
            "learner_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            comment="FK → learner_profiles.id (pseudonym_id used in LLM calls; real UUID stored here)",
        ),
        sa.Column(
            "session_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
            comment="FK → diagnostic_sessions.id; NULL for practice/non-diagnostic exposure",
        ),

        # --- Event data -----------------------------------------------
        sa.Column(
            "served_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
            comment="When the item was sent to the frontend",
        ),
        sa.Column(
            "answered_at",
            sa.DateTime(timezone=True),
            nullable=True,
            comment="When the learner submitted their answer; NULL if session abandoned",
        ),
        sa.Column(
            "learner_response",
            sa.String(500),
            nullable=True,
            comment="The answer the learner gave; NULL if unanswered",
        ),
        sa.Column(
            "is_correct",
            sa.Boolean,
            nullable=True,
            comment="NULL = unanswered; True/False = graded",
        ),
        sa.Column(
            "response_time_ms",
            sa.Integer,
            nullable=True,
            comment="Time from item display to answer submission in milliseconds",
        ),

        # --- FK constraints (declarative; enforced by PostgreSQL) ------
        sa.ForeignKeyConstraint(
            ["item_id"],
            ["diagnostic_items.item_id"],
            name="fk_item_exposures_item_id",
            ondelete="RESTRICT",  # never silently delete a served item
        ),
    )

    # ------------------------------------------------------------------
    # Constraints
    # ------------------------------------------------------------------
    op.create_check_constraint(
        "ck_item_exposures_response_time_positive",
        "item_exposures",
        "response_time_ms IS NULL OR response_time_ms >= 0",
    )
    op.create_check_constraint(
        "ck_item_exposures_answered_after_served",
        "item_exposures",
        "answered_at IS NULL OR answered_at >= served_at",
    )

    # ------------------------------------------------------------------
    # Indexes
    # ------------------------------------------------------------------
    # Core lookup: which items has this learner seen?
    op.create_index(
        "ix_item_exposures_learner_item",
        "item_exposures",
        ["learner_id", "item_id"],
    )
    # Exposure cooling: recent exposures for a learner in the last N days
    op.create_index(
        "ix_item_exposures_learner_served_at",
        "item_exposures",
        ["learner_id", "served_at"],
    )
    # Per-item usage stats (used when updating diagnostic_items.exposure_count)
    op.create_index(
        "ix_item_exposures_item_id",
        "item_exposures",
        ["item_id"],
    )
    # Session replay: all items in a given diagnostic session
    op.create_index(
        "ix_item_exposures_session_id",
        "item_exposures",
        ["session_id"],
        postgresql_where=sa.text("session_id IS NOT NULL"),
    )
    # De-duplication: ensure a learner cannot see the same item twice in one session
    op.create_index(
        "uq_item_exposures_learner_item_session",
        "item_exposures",
        ["learner_id", "item_id", "session_id"],
        unique=True,
        postgresql_where=sa.text("session_id IS NOT NULL"),
    )


def downgrade() -> None:
    for idx in (
        "uq_item_exposures_learner_item_session",
        "ix_item_exposures_session_id",
        "ix_item_exposures_item_id",
        "ix_item_exposures_learner_served_at",
        "ix_item_exposures_learner_item",
    ):
        op.drop_index(idx, table_name="item_exposures")

    for ck in (
        "ck_item_exposures_answered_after_served",
        "ck_item_exposures_response_time_positive",
    ):
        op.drop_constraint(ck, "item_exposures")

    op.drop_table("item_exposures")
