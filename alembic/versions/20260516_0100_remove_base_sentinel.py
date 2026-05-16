"""
alembic/versions/20260516_0100_remove_base_sentinel.py

Fix split migration state: remove 'base' sentinel + ensure audit_events exists.
================================================================================
During initial deployment the database was stamped directly at
``20260510_0300`` without running the full migration chain from ``0001``.
Two problems resulted:

1. A ``'base'`` row was left in ``alembic_version``, causing the readiness
   probe to report revision ``"base"`` instead of the real head revision,
   which made the API container appear misconfigured.

2. Migration ``0006_v2_audit_events.py`` (which creates the ``audit_events``
   table) was never executed.  Migration ``20260510_0300`` assumed the table
   already existed and tried to create a trigger on it, which caused the
   ``audit_repository`` health check to fail with ``ProgrammingError``.

Both fixes are applied idempotently (``IF NOT EXISTS`` / conditional DELETE)
so this migration is safe to run against any state of the database.
"""
from alembic import op
import sqlalchemy as sa

revision = "20260516_0100"
down_revision = "20260510_0300"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── Fix 1: Remove the spurious 'base' sentinel row ────────────────────────
    # No-op when the row has already been deleted manually.
    op.execute("DELETE FROM alembic_version WHERE version_num = 'base'")

    # ── Fix 2: Ensure audit_events exists (migration 0006 may have been skipped) ─
    op.execute("""
        CREATE TABLE IF NOT EXISTS audit_events (
            id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
            event_type  TEXT        NOT NULL,
            actor_id    UUID,
            resource_id UUID,
            payload     JSONB       NOT NULL DEFAULT '{}'::jsonb,
            created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """)

    # Indexes (all use IF NOT EXISTS via raw SQL — op.create_index has no guard)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_audit_events_actor
            ON audit_events (actor_id)
            WHERE actor_id IS NOT NULL
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_audit_events_type
            ON audit_events (event_type)
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_audit_events_resource
            ON audit_events (resource_id)
            WHERE resource_id IS NOT NULL
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_audit_events_ts
            ON audit_events (created_at DESC)
    """)

    # Append-only rules (DROP + CREATE is idempotent)
    op.execute("DROP RULE IF EXISTS audit_events_no_update ON audit_events")
    op.execute("""
        CREATE RULE audit_events_no_update
        AS ON UPDATE TO audit_events DO INSTEAD NOTHING
    """)
    op.execute("DROP RULE IF EXISTS audit_events_no_delete ON audit_events")
    op.execute("""
        CREATE RULE audit_events_no_delete
        AS ON DELETE TO audit_events DO INSTEAD NOTHING
    """)

    # Row-level immutability trigger
    op.execute("""
        CREATE OR REPLACE FUNCTION audit_events_immutable()
        RETURNS TRIGGER LANGUAGE plpgsql AS $$
        BEGIN
            RAISE EXCEPTION 'audit_events is append-only – modifications are forbidden';
        END;
        $$
    """)
    op.execute("DROP TRIGGER IF EXISTS trg_audit_events_immutable ON audit_events")
    op.execute("""
        CREATE TRIGGER trg_audit_events_immutable
        BEFORE UPDATE OR DELETE ON audit_events
        FOR EACH ROW EXECUTE FUNCTION audit_events_immutable()
    """)

    op.execute("""
        COMMENT ON TABLE audit_events IS
        'Append-only POPIA audit trail. UPDATE and DELETE are blocked by '
        'PostgreSQL RULE. Do not alter this table structure without a '
        'formal security review.'
    """)


def downgrade() -> None:
    # This migration fixes a broken state; downgrading would re-introduce
    # the broken state and is intentionally not supported.
    pass

