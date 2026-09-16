"""Reconcile legacy unmapped consolidation tables (DEF-12).

Drops the 5 unmapped consolidation tables (restriction_requests,
correction_requests, erasure_requests, data_export_requests, consent_records)
that were superseded by canonical ORM models (parental_consents, erasure_request).
Provides full reversible downgrade recreating the tables if rolled back.
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision = "20260913_2300_reconcile_consolidation_tables"
down_revision = "20260711_1510_prd11_runtime_green_exec5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    for table in [
        "restriction_requests",
        "correction_requests",
        "erasure_requests",
        "data_export_requests",
        "consent_records",
    ]:
        op.drop_table(table)


def downgrade() -> None:
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

