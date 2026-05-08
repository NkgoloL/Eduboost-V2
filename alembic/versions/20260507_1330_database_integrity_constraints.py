"""database integrity constraints and production indexes.

Revision ID: 20260507_1330
Revises: 20260507_1200
Create Date: 2026-05-07

This migration is intentionally additive. It strengthens the production schema
without rewriting historical data or changing application runtime semantics.
Destructive changes remain forbidden unless a migration-specific backup,
staging dry-run, validation, and rollback plan is documented.
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260507_1330"
down_revision = "20260507_1200"
branch_labels = None
depends_on = None

HEX_64 = "^[0-9a-f]{64}$"


def upgrade() -> None:
    # ── Timestamp completeness ──────────────────────────────────────────────
    op.add_column(
        "parental_consents",
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.add_column(
        "parental_consents",
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.add_column(
        "subject_mastery",
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.add_column(
        "stripe_webhook_events",
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    # ── Lookup and operational indexes ──────────────────────────────────────
    op.create_index(
        "ix_guardians_stripe_customer_id",
        "guardians",
        ["stripe_customer_id"],
        unique=False,
        postgresql_where=sa.text("stripe_customer_id IS NOT NULL"),
    )
    op.create_index(
        "ix_guardians_stripe_subscription_id",
        "guardians",
        ["stripe_subscription_id"],
        unique=False,
        postgresql_where=sa.text("stripe_subscription_id IS NOT NULL"),
    )
    op.create_index(
        "ix_guardians_active_subscription",
        "guardians",
        ["subscription_tier", "stripe_subscription_id"],
        unique=False,
        postgresql_where=sa.text(
            "is_active IS TRUE AND stripe_subscription_id IS NOT NULL "
            "AND lower(subscription_tier::text) = 'premium'"
        ),
    )
    op.create_index(
        "ix_parental_consents_guardian_learner_status",
        "parental_consents",
        ["guardian_id", "learner_id", "status"],
    )
    op.create_index(
        "ix_parental_consents_active_status",
        "parental_consents",
        ["learner_id", "guardian_id"],
        unique=False,
        postgresql_where=sa.text(
            "revoked_at IS NULL AND expires_at > CURRENT_TIMESTAMP "
            "AND status::text IN ('granted', 'renewal_required')"
        ),
    )
    op.create_index("ix_diagnostic_sessions_created_at", "diagnostic_sessions", ["created_at"])
    op.create_index(
        "ix_diagnostic_sessions_incomplete",
        "diagnostic_sessions",
        ["learner_id", "created_at"],
        unique=False,
        postgresql_where=sa.text("completed_at IS NULL"),
    )
    op.create_index("ix_subject_mastery_last_updated", "subject_mastery", ["last_updated"])
    op.create_index("ix_stripe_webhook_processed_at", "stripe_webhook_events", ["processed_at"])

    # ── Database-level invariants ───────────────────────────────────────────
    op.create_check_constraint(
        "ck_learner_profiles_grade_range",
        "learner_profiles",
        "grade >= 0 AND grade <= 12",
    )
    op.create_check_constraint(
        "ck_learner_profiles_xp_non_negative",
        "learner_profiles",
        "xp >= 0",
    )
    op.create_check_constraint(
        "ck_learner_profiles_streak_non_negative",
        "learner_profiles",
        "streak_days >= 0",
    )
    op.create_check_constraint(
        "ck_parental_consents_expiry_after_grant",
        "parental_consents",
        "expires_at > granted_at",
    )
    op.create_check_constraint(
        "ck_parental_consents_revoked_after_grant",
        "parental_consents",
        "revoked_at IS NULL OR revoked_at >= granted_at",
    )
    op.create_check_constraint(
        "ck_audit_events_event_type_not_blank",
        "audit_events",
        "length(btrim(event_type)) > 0",
    )
    op.create_check_constraint(
        "ck_audit_events_hash_hex64_or_bootstrap",
        "audit_events",
        f"event_hash = '' OR event_hash ~ '{HEX_64}'",
    )
    op.create_check_constraint(
        "ck_audit_events_hmac_hex64_or_bootstrap",
        "audit_events",
        f"hmac_signature = '' OR hmac_signature ~ '{HEX_64}'",
    )
    op.create_check_constraint(
        "ck_audit_events_previous_hash_hex64",
        "audit_events",
        f"previous_event_hash IS NULL OR previous_event_hash ~ '{HEX_64}'",
    )
    op.create_check_constraint(
        "ck_irt_items_grade_range",
        "irt_items",
        "grade >= 0 AND grade <= 12",
    )
    op.create_check_constraint(
        "ck_irt_items_correct_option",
        "irt_items",
        "correct_option IN ('A', 'B', 'C', 'D')",
    )
    op.create_check_constraint(
        "ck_irt_items_a_param_positive",
        "irt_items",
        "a_param > 0",
    )
    op.create_check_constraint(
        "ck_knowledge_gaps_severity_range",
        "knowledge_gaps",
        "severity >= 0 AND severity <= 1",
    )
    op.create_check_constraint(
        "ck_lessons_grade_range",
        "lessons",
        "grade >= 0 AND grade <= 12",
    )
    op.create_check_constraint(
        "ck_lessons_feedback_score_range",
        "lessons",
        "feedback_score IS NULL OR (feedback_score >= 1 AND feedback_score <= 5)",
    )
    op.create_check_constraint(
        "ck_subject_mastery_standard_error_non_negative",
        "subject_mastery",
        "standard_error >= 0",
    )
    op.create_check_constraint(
        "ck_lesson_feedback_rating_range",
        "lesson_feedback",
        "rating >= 1 AND rating <= 5",
    )
    op.create_check_constraint(
        "ck_rlhf_exports_positive_count_non_negative",
        "rlhf_exports",
        "positive_count >= 0",
    )
    op.create_check_constraint(
        "ck_rlhf_exports_negative_count_non_negative",
        "rlhf_exports",
        "negative_count >= 0",
    )
    op.create_check_constraint(
        "ck_rlhf_exports_record_count_non_negative",
        "rlhf_exports",
        "record_count >= 0",
    )


def downgrade() -> None:
    # Reverse order keeps dependent objects clean. This downgrade is safe: it
    # removes only additive indexes and constraints introduced by this revision.
    op.drop_constraint("ck_rlhf_exports_record_count_non_negative", "rlhf_exports", type_="check")
    op.drop_constraint("ck_rlhf_exports_negative_count_non_negative", "rlhf_exports", type_="check")
    op.drop_constraint("ck_rlhf_exports_positive_count_non_negative", "rlhf_exports", type_="check")
    op.drop_constraint("ck_lesson_feedback_rating_range", "lesson_feedback", type_="check")
    op.drop_constraint("ck_subject_mastery_standard_error_non_negative", "subject_mastery", type_="check")
    op.drop_constraint("ck_lessons_feedback_score_range", "lessons", type_="check")
    op.drop_constraint("ck_lessons_grade_range", "lessons", type_="check")
    op.drop_constraint("ck_knowledge_gaps_severity_range", "knowledge_gaps", type_="check")
    op.drop_constraint("ck_irt_items_a_param_positive", "irt_items", type_="check")
    op.drop_constraint("ck_irt_items_correct_option", "irt_items", type_="check")
    op.drop_constraint("ck_irt_items_grade_range", "irt_items", type_="check")
    op.drop_constraint("ck_audit_events_previous_hash_hex64", "audit_events", type_="check")
    op.drop_constraint("ck_audit_events_hmac_hex64_or_bootstrap", "audit_events", type_="check")
    op.drop_constraint("ck_audit_events_hash_hex64_or_bootstrap", "audit_events", type_="check")
    op.drop_constraint("ck_audit_events_event_type_not_blank", "audit_events", type_="check")
    op.drop_constraint("ck_parental_consents_revoked_after_grant", "parental_consents", type_="check")
    op.drop_constraint("ck_parental_consents_expiry_after_grant", "parental_consents", type_="check")
    op.drop_constraint("ck_learner_profiles_streak_non_negative", "learner_profiles", type_="check")
    op.drop_constraint("ck_learner_profiles_xp_non_negative", "learner_profiles", type_="check")
    op.drop_constraint("ck_learner_profiles_grade_range", "learner_profiles", type_="check")

    op.drop_index("ix_stripe_webhook_processed_at", table_name="stripe_webhook_events")
    op.drop_index("ix_subject_mastery_last_updated", table_name="subject_mastery")
    op.drop_index("ix_diagnostic_sessions_incomplete", table_name="diagnostic_sessions")
    op.drop_index("ix_diagnostic_sessions_created_at", table_name="diagnostic_sessions")
    op.drop_index("ix_parental_consents_active_status", table_name="parental_consents")
    op.drop_index("ix_parental_consents_guardian_learner_status", table_name="parental_consents")
    op.drop_index("ix_guardians_active_subscription", table_name="guardians")
    op.drop_index("ix_guardians_stripe_subscription_id", table_name="guardians")
    op.drop_index("ix_guardians_stripe_customer_id", table_name="guardians")

    op.drop_column("stripe_webhook_events", "created_at")
    op.drop_column("subject_mastery", "created_at")
    op.drop_column("parental_consents", "updated_at")
    op.drop_column("parental_consents", "created_at")
