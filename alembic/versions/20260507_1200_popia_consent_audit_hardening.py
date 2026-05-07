"""POPIA consent states and tamper-evident audit chain.

Revision ID: 20260507_1200
Revises: 20260505_1734
Create Date: 2026-05-07
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260507_1200"
down_revision = "20260505_1734"
branch_labels = None
depends_on = None

CONSENT_STATUS = sa.Enum(
    "PENDING",
    "GRANTED",
    "DENIED",
    "EXPIRED",
    "WITHDRAWN",
    "RENEWAL_REQUIRED",
    name="consentstate",
)


def upgrade() -> None:
    bind = op.get_bind()
    CONSENT_STATUS.create(bind, checkfirst=True)
    op.add_column(
        "parental_consents",
        sa.Column("status", CONSENT_STATUS, nullable=False, server_default="GRANTED"),
    )
    op.create_index("ix_parental_consents_status", "parental_consents", ["status"])

    op.add_column("audit_events", sa.Column("previous_event_hash", sa.String(length=64), nullable=True))
    op.add_column("audit_events", sa.Column("event_hash", sa.String(length=64), nullable=False, server_default=""))
    op.add_column("audit_events", sa.Column("hmac_signature", sa.String(length=64), nullable=False, server_default=""))
    op.create_index("idx_audit_events_hash", "audit_events", ["event_hash"])


def downgrade() -> None:
    op.drop_index("idx_audit_events_hash", table_name="audit_events")
    op.drop_column("audit_events", "hmac_signature")
    op.drop_column("audit_events", "event_hash")
    op.drop_column("audit_events", "previous_event_hash")
    op.drop_index("ix_parental_consents_status", table_name="parental_consents")
    op.drop_column("parental_consents", "status")
    CONSENT_STATUS.drop(op.get_bind(), checkfirst=True)
