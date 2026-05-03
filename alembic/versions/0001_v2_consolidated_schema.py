"""
Initial V2 Consolidated Schema Migration

Revision ID: 0001_v2_consolidated
Revises: (base)
Create Date: 2026-05-03

This is the authoritative initial migration for EduBoost V2. It captures all
domain tables required by the modular monolith architecture:

1. guardians — Parent/teacher accounts with subscription tier
2. learner_profiles — Pseudonymized learner profiles with IRT theta
3. parental_consents — POPIA consent records with expiry/revocation
4. irt_items — Question bank with IRT 2PL parameters (a, b)
5. diagnostic_sessions — Assessment attempts with IRT theta tracking
6. knowledge_gaps — Identified learning needs per learner
7. lessons — Generated/adaptive lesson content per learner
8. audit_logs — Append-only audit trail (immutable)
9. stripe_webhook_events — Idempotency log for Stripe webhooks

This migration is generated from app/models/__init__.py and is the
single source of truth for schema going forward.
"""
from __future__ import annotations

from datetime import UTC, datetime, timedelta
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# Revision identifiers
revision = "0001_v2_consolidated"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create all V2 core tables."""

    # ──────────────────────────────────────────────────────────────────────────
    # 1. Guardians (Parent/Teacher accounts)
    # ──────────────────────────────────────────────────────────────────────────
    op.create_table(
        "guardians",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("email_hash", sa.String(64), nullable=False, unique=True, index=True),
        sa.Column("email_encrypted", sa.Text, nullable=False),
        sa.Column("display_name", sa.String(120), nullable=False),
        sa.Column("role", sa.Enum("student", "parent", "teacher", "admin", name="userrole"), nullable=False, server_default="parent"),
        sa.Column("password_hash", sa.Text, nullable=False),
        sa.Column("subscription_tier", sa.Enum("free", "premium", name="subscriptiontier"), nullable=False, server_default="free"),
        sa.Column("stripe_customer_id", sa.String(64), nullable=True),
        sa.Column("stripe_subscription_id", sa.String(64), nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_guardians_email_hash", "guardians", ["email_hash"])

    # ──────────────────────────────────────────────────────────────────────────
    # 2. Learner Profiles
    # ──────────────────────────────────────────────────────────────────────────
    op.create_table(
        "learner_profiles",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("pseudonym_id", sa.String(36), nullable=False, unique=True, index=True),
        sa.Column("guardian_id", sa.String(36), nullable=False),
        sa.Column("display_name", sa.String(80), nullable=False),
        sa.Column("grade", sa.Integer, nullable=False),  # 0=GradeR, 1-7
        sa.Column("language", sa.Enum("en", "zu", "af", "xh", name="language"), nullable=False, server_default="en"),
        sa.Column("archetype", sa.Enum(
            "Keter", "Chokmah", "Binah", "Chesed", "Gevurah", "Tiferet",
            "Netzach", "Hod", "Yesod", "Malkuth", name="archetypelabel"
        ), nullable=True),
        sa.Column("theta", sa.Float, nullable=False, server_default="0.0"),  # IRT ability
        sa.Column("xp", sa.Integer, nullable=False, server_default="0"),
        sa.Column("streak_days", sa.Integer, nullable=False, server_default="0"),
        sa.Column("last_active", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_deleted", sa.Boolean, nullable=False, server_default="false"),  # POPIA soft-delete
        sa.Column("deletion_requested_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["guardian_id"], ["guardians.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_learner_guardian_grade", "learner_profiles", ["guardian_id", "grade"])
    op.create_index("ix_learner_profiles_pseudonym_id", "learner_profiles", ["pseudonym_id"])

    # ──────────────────────────────────────────────────────────────────────────
    # 3. Parental Consents (POPIA enforcement)
    # ──────────────────────────────────────────────────────────────────────────
    op.create_table(
        "parental_consents",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("guardian_id", sa.String(36), nullable=False),
        sa.Column("learner_id", sa.String(36), nullable=False),
        sa.Column("policy_version", sa.String(20), nullable=False, server_default="1.0"),
        sa.Column("granted_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ip_address_hash", sa.String(64), nullable=True),
        sa.ForeignKeyConstraint(["guardian_id"], ["guardians.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["learner_id"], ["learner_profiles.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("guardian_id", "learner_id", name="uq_consent_guardian_learner"),
    )
    op.create_index("ix_parental_consent_guardian", "parental_consents", ["guardian_id"])
    op.create_index("ix_parental_consent_learner", "parental_consents", ["learner_id"])

    # ──────────────────────────────────────────────────────────────────────────
    # 4. IRT Items (Question Bank)
    # ──────────────────────────────────────────────────────────────────────────
    op.create_table(
        "irt_items",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("grade", sa.Integer, nullable=False),
        sa.Column("subject", sa.String(60), nullable=False),
        sa.Column("topic", sa.String(120), nullable=False),
        sa.Column("language", sa.Enum("en", "zu", "af", "xh", name="language"), nullable=False, server_default="en"),
        sa.Column("question_text", sa.Text, nullable=False),
        sa.Column("options", postgresql.JSONB, nullable=False),  # {A: ..., B: ..., C: ..., D: ...}
        sa.Column("correct_option", sa.String(1), nullable=False),
        sa.Column("a_param", sa.Float, nullable=False, server_default="1.0"),  # discrimination
        sa.Column("b_param", sa.Float, nullable=False, server_default="0.0"),  # difficulty
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_irt_grade_subject", "irt_items", ["grade", "subject"])

    # ──────────────────────────────────────────────────────────────────────────
    # 5. Diagnostic Sessions
    # ──────────────────────────────────────────────────────────────────────────
    op.create_table(
        "diagnostic_sessions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("learner_id", sa.String(36), nullable=False),
        sa.Column("responses", postgresql.JSONB, nullable=False, server_default="'{}'"),  # {item_id: bool}
        sa.Column("theta_before", sa.Float, nullable=False, server_default="0.0"),
        sa.Column("theta_after", sa.Float, nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["learner_id"], ["learner_profiles.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_diagnostic_learner", "diagnostic_sessions", ["learner_id"])

    # ──────────────────────────────────────────────────────────────────────────
    # 6. Knowledge Gaps
    # ──────────────────────────────────────────────────────────────────────────
    op.create_table(
        "knowledge_gaps",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("learner_id", sa.String(36), nullable=False),
        sa.Column("grade", sa.Integer, nullable=False),
        sa.Column("subject", sa.String(60), nullable=False),
        sa.Column("topic", sa.String(120), nullable=False),
        sa.Column("severity", sa.Float, nullable=False, server_default="1.0"),  # 0=mild … 1=critical
        sa.Column("resolved", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["learner_id"], ["learner_profiles.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_knowledge_gap_learner", "knowledge_gaps", ["learner_id"])

    # ──────────────────────────────────────────────────────────────────────────
    # 7. Lessons (Adaptive content)
    # ──────────────────────────────────────────────────────────────────────────
    op.create_table(
        "lessons",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("learner_id", sa.String(36), nullable=False),
        sa.Column("knowledge_gap_id", sa.String(36), nullable=True),
        sa.Column("grade", sa.Integer, nullable=False),
        sa.Column("subject", sa.String(60), nullable=False),
        sa.Column("topic", sa.String(120), nullable=False),
        sa.Column("language", sa.Enum("en", "zu", "af", "xh", name="language"), nullable=False, server_default="en"),
        sa.Column("archetype", sa.Enum(
            "Keter", "Chokmah", "Binah", "Chesed", "Gevurah", "Tiferet",
            "Netzach", "Hod", "Yesod", "Malkuth", name="archetypelabel"
        ), nullable=True),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("llm_provider", sa.String(30), nullable=False, server_default="groq"),
        sa.Column("served_from_cache", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("feedback_score", sa.Integer, nullable=True),  # 1-5
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["learner_id"], ["learner_profiles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["knowledge_gap_id"], ["knowledge_gaps.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_lesson_learner", "lessons", ["learner_id"])

    # ──────────────────────────────────────────────────────────────────────────
    # 8. Audit Logs (Append-only, replaces RabbitMQ)
    # ──────────────────────────────────────────────────────────────────────────
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("event_type", sa.String(80), nullable=False, index=True),
        sa.Column("actor_id", sa.String(36), nullable=True),
        sa.Column("learner_pseudonym", sa.String(36), nullable=True),
        sa.Column("payload", postgresql.JSONB, nullable=False, server_default="'{}'"),
        sa.Column("constitutional_outcome", sa.String(20), nullable=True),  # APPROVED/REJECTED
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_audit_event_created", "audit_logs", ["event_type", "created_at"])

    # Append-only trigger on audit_logs (prevent UPDATE/DELETE)
    op.execute("""
        CREATE OR REPLACE FUNCTION audit_logs_immutable()
        RETURNS TRIGGER LANGUAGE plpgsql AS $$
        BEGIN
            RAISE EXCEPTION 'audit_logs is append-only. UPDATE and DELETE are prohibited.';
        END;
        $$;
    """)
    op.execute("""
        CREATE TRIGGER trg_audit_logs_no_update
        BEFORE UPDATE ON audit_logs
        FOR EACH ROW EXECUTE FUNCTION audit_logs_immutable();
    """)
    op.execute("""
        CREATE TRIGGER trg_audit_logs_no_delete
        BEFORE DELETE ON audit_logs
        FOR EACH ROW EXECUTE FUNCTION audit_logs_immutable();
    """)

    # ──────────────────────────────────────────────────────────────────────────
    # 9. Stripe Webhook Events (Idempotency log)
    # ──────────────────────────────────────────────────────────────────────────
    op.create_table(
        "stripe_webhook_events",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("stripe_event_id", sa.String(64), nullable=False, unique=True),
        sa.Column("event_type", sa.String(80), nullable=False),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("payload", postgresql.JSONB, nullable=False, server_default="'{}'"),
    )
    op.create_index("ix_stripe_event_id", "stripe_webhook_events", ["stripe_event_id"])


def downgrade() -> None:
    """Drop all V2 core tables (reverse order)."""
    
    # Drop audit_logs triggers first
    op.execute("DROP TRIGGER IF EXISTS trg_audit_logs_no_delete ON audit_logs;")
    op.execute("DROP TRIGGER IF EXISTS trg_audit_logs_no_update ON audit_logs;")
    op.execute("DROP FUNCTION IF EXISTS audit_logs_immutable();")
    
    # Drop tables
    op.drop_table("stripe_webhook_events")
    op.drop_table("audit_logs")
    op.drop_table("lessons")
    op.drop_table("knowledge_gaps")
    op.drop_table("diagnostic_sessions")
    op.drop_table("irt_items")
    op.drop_table("parental_consents")
    op.drop_table("learner_profiles")
    op.drop_table("guardians")
    
    # Drop enums
    op.execute("DROP TYPE IF EXISTS archetypelabel CASCADE;")
    op.execute("DROP TYPE IF EXISTS language CASCADE;")
    op.execute("DROP TYPE IF EXISTS subscriptiontier CASCADE;")
    op.execute("DROP TYPE IF EXISTS userrole CASCADE;")
