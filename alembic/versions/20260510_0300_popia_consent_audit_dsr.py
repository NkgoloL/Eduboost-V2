"""
alembic/versions/0010_popia_consent_audit_dsr.py
Creates all POPIA-related tables (§4.1 §4.3 §4.5).
Sets up row-level trigger to prevent UPDATE/DELETE on audit_events.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "20260510_0300"
down_revision = "20260510_0200"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ================================================================
    # NOTE: The audit_events table and its append-only rules are 
    # ALREADY CREATED in migration 0006_v2_audit_events.py.
    # This migration only adds POPIA consent and data-subject-rights tables.
    # ================================================================

    # Row-level trigger: prevent UPDATE/DELETE on audit_events (§4.5)
    # This ensures the table remains append-only at the database level.
    op.execute("""
        CREATE OR REPLACE FUNCTION audit_events_immutable()
        RETURNS TRIGGER LANGUAGE plpgsql AS $$
        BEGIN
            RAISE EXCEPTION 'audit_events is append-only – modifications are forbidden';
        END;
        $$;
    """)
    op.execute("""
        CREATE TRIGGER trg_audit_events_immutable
        BEFORE UPDATE OR DELETE ON audit_events
        FOR EACH ROW EXECUTE FUNCTION audit_events_immutable();
    """)

    # ================================================================
    # §4.1 – consent records
    # ================================================================
    op.create_table(
        "consent_records",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("learner_id", UUID(as_uuid=True), nullable=False),
        sa.Column("guardian_id", UUID(as_uuid=True), nullable=False),
        sa.Column("privacy_notice_version", sa.String(32), nullable=False),
        sa.Column("state", sa.String(32), nullable=False, server_default="pending"),
        sa.Column("granted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("withdrawn_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("denial_reason", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_consent_records_learner_id", "consent_records", ["learner_id"])

    # ----------------------------------------------------------------
    # §4.3 – Data Subject Rights tables
    # ----------------------------------------------------------------
    op.create_table(
        "data_export_requests",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("learner_id", UUID(as_uuid=True), nullable=False),
        sa.Column("requested_by", UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="pending"),
        sa.Column("format", sa.String(8), nullable=False, server_default="json"),
        sa.Column("download_url", sa.Text, nullable=True),
        sa.Column("artifact_path", sa.Text, nullable=True),
        sa.Column("sla_deadline", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_export_requests_learner_id", "data_export_requests", ["learner_id"])

    op.create_table(
        "erasure_requests",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("learner_id", UUID(as_uuid=True), nullable=False),
        sa.Column("requested_by", UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="pending"),
        sa.Column("review_notes", sa.Text, nullable=True),
        sa.Column("legal_hold", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("sla_deadline", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("executed_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "correction_requests",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("learner_id", UUID(as_uuid=True), nullable=False),
        sa.Column("requested_by", UUID(as_uuid=True), nullable=False),
        sa.Column("field_name", sa.String(128), nullable=False),
        sa.Column("old_value", sa.Text, nullable=True),
        sa.Column("new_value", sa.Text, nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "restriction_requests",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("learner_id", UUID(as_uuid=True), nullable=False),
        sa.Column("requested_by", UUID(as_uuid=True), nullable=False),
        sa.Column("reason", sa.Text, nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("lifted_at", sa.DateTime(timezone=True), nullable=True),
    )

    # ----------------------------------------------------------------
    # §4.5 – revoke UPDATE/DELETE from app role on audit_events
    # (run as superuser during migration)
    # ----------------------------------------------------------------
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'eduboost_app') THEN
                REVOKE UPDATE, DELETE ON audit_events FROM eduboost_app;
            END IF;
        END $$;
    """)


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_audit_events_immutable ON audit_events;")
    op.execute("DROP FUNCTION IF EXISTS audit_events_immutable;")
    for table in [
        "restriction_requests", "correction_requests",
        "erasure_requests", "data_export_requests",
        "consent_records",
    ]:
        op.drop_table(table)
