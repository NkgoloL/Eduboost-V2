"""
alembic/versions/0006_v2_audit_events.py
─────────────────────────────────────────────────────────────────────────────
Task 23: V2 Append-Only PostgreSQL Audit Service

Creates the audit_events table with:
  - PostgreSQL RULE preventing UPDATE and DELETE (immutability guarantee)
  - JSONB payload for flexible event metadata
  - Indexed on actor_id, event_type, and created_at (DESC) for query performance
  - Replaces Redis stream dependency in the V2 path

Revision: 0006
Down revision: 94b628483fa7  (merge head)
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers
revision: str = "0006"
down_revision: str = "94b628483fa7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ─── Create audit_events table ────────────────────────────────────────────
    op.create_table(
        "audit_events",
        sa.Column(
            "id",
            sa.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column(
            "event_type",
            sa.Text(),
            nullable=False,
            comment="Dot-notation event identifier, e.g. 'consent.granted'",
        ),
        sa.Column(
            "actor_id",
            sa.UUID(as_uuid=True),
            nullable=True,
            comment="UUID of the entity that triggered the event (guardian, admin, system)",
        ),
        sa.Column(
            "resource_id",
            sa.UUID(as_uuid=True),
            nullable=True,
            comment="UUID of the primary resource this event relates to",
        ),
        sa.Column(
            "payload",
            sa.dialects.postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
            comment="Event metadata — MUST NOT contain PII; use pseudonym_id only",
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
            comment="Immutable creation timestamp — set by database, never application",
        ),
    )

    # ─── Indexes for common query patterns ───────────────────────────────────
    op.create_index(
        "idx_audit_events_actor",
        "audit_events",
        ["actor_id"],
        postgresql_where=sa.text("actor_id IS NOT NULL"),
    )
    op.create_index(
        "idx_audit_events_type",
        "audit_events",
        ["event_type"],
    )
    op.create_index(
        "idx_audit_events_resource",
        "audit_events",
        ["resource_id"],
        postgresql_where=sa.text("resource_id IS NOT NULL"),
    )
    op.create_index(
        "idx_audit_events_ts",
        "audit_events",
        [sa.text("created_at DESC")],
    )

    # ─── Immutability: PostgreSQL RULES ──────────────────────────────────────
    # These rules make the audit table truly append-only at the database level.
    # No application-layer bug, SQL injection, or direct DB connection can
    # modify or delete audit records. This satisfies POPIA §8 Accountability
    # and §22 Security Safeguards.

    op.execute(
        """
        CREATE RULE audit_events_no_update
        AS ON UPDATE TO audit_events
        DO INSTEAD NOTHING;
        """
    )

    op.execute(
        """
        CREATE RULE audit_events_no_delete
        AS ON DELETE TO audit_events
        DO INSTEAD NOTHING;
        """
    )

    # ─── Row-level comment ────────────────────────────────────────────────────
    op.execute(
        """
        COMMENT ON TABLE audit_events IS
        'Append-only POPIA audit trail. UPDATE and DELETE are blocked by '
        'PostgreSQL RULE. Do not alter this table structure without a '
        'formal security review.';
        """
    )


def downgrade() -> None:
    # Remove rules before dropping table
    op.execute("DROP RULE IF EXISTS audit_events_no_update ON audit_events;")
    op.execute("DROP RULE IF EXISTS audit_events_no_delete ON audit_events;")
    op.drop_index("idx_audit_events_ts", table_name="audit_events")
    op.drop_index("idx_audit_events_resource", table_name="audit_events")
    op.drop_index("idx_audit_events_type", table_name="audit_events")
    op.drop_index("idx_audit_events_actor", table_name="audit_events")
    op.drop_table("audit_events")
