#!/usr/bin/env python3
"""Validate ORM-level production schema invariants.

This check is deliberately database-free. It verifies that the canonical ORM
metadata includes the baseline integrity features expected for learner data,
consent, auditability, and operational lookup paths. Database migrations still
need `alembic upgrade head` and `alembic check` in CI/staging.
"""
from __future__ import annotations

import sys
from collections.abc import Iterable

import sqlalchemy as sa

from app.core.database import Base
import app.models  # noqa: F401  # import side-effect populates Base.metadata

REQUIRED_TABLES = {
    "guardians",
    "learner_profiles",
    "parental_consents",
    "audit_events",
    "irt_items",
    "diagnostic_sessions",
    "knowledge_gaps",
    "subject_mastery",
    "lessons",
    "stripe_webhook_events",
}

REQUIRED_INDEXES = {
    "guardians": {
        "ix_guardians_email_hash",
        "ix_guardians_stripe_customer_id",
        "ix_guardians_stripe_subscription_id",
        "ix_guardians_active_subscription",
    },
    "learner_profiles": {"ix_learner_guardian_grade", "ix_learner_profiles_created_at"},
    "parental_consents": {
        "ix_parental_consents_status",
        "ix_parental_consents_guardian_learner_status",
        "ix_parental_consents_active_status",
    },
    "diagnostic_sessions": {"ix_diagnostic_sessions_created_at", "ix_diagnostic_sessions_incomplete"},
    "audit_events": {"idx_audit_events_ts", "idx_audit_events_actor", "idx_audit_events_hash"},
    "subject_mastery": {"ix_subject_mastery_learner_subject", "ix_subject_mastery_last_updated"},
    "stripe_webhook_events": {"ix_stripe_webhook_processed_at"},
}

REQUIRED_CONSTRAINTS = {
    "learner_profiles": {
        "ck_learner_profiles_grade_range",
        "ck_learner_profiles_xp_non_negative",
        "ck_learner_profiles_streak_non_negative",
    },
    "parental_consents": {
        "uq_consent_guardian_learner",
        "ck_parental_consents_expiry_after_grant",
        "ck_parental_consents_revoked_after_grant",
    },
    "audit_events": {
        "ck_audit_events_event_type_not_blank",
        "ck_audit_events_hash_hex64_or_bootstrap",
        "ck_audit_events_hmac_hex64_or_bootstrap",
        "ck_audit_events_previous_hash_hex64",
    },
    "irt_items": {"ck_irt_items_grade_range", "ck_irt_items_correct_option", "ck_irt_items_a_param_positive"},
    "knowledge_gaps": {"ck_knowledge_gaps_severity_range"},
    "lessons": {"ck_lessons_grade_range", "ck_lessons_feedback_score_range"},
    "subject_mastery": {"ck_subject_mastery_standard_error_non_negative"},
}


def names(objects: Iterable[object]) -> set[str]:
    return {str(getattr(obj, "name", "")) for obj in objects if getattr(obj, "name", None)}


def main() -> int:
    metadata = Base.metadata
    errors: list[str] = []

    missing_tables = REQUIRED_TABLES - set(metadata.tables)
    if missing_tables:
        errors.append(f"missing ORM tables: {sorted(missing_tables)}")

    for table_name in REQUIRED_TABLES & set(metadata.tables):
        table = metadata.tables[table_name]
        pk_columns = [column.name for column in table.primary_key.columns]
        if not pk_columns:
            errors.append(f"{table_name}: missing primary key")
        if table_name not in {"audit_events"} and "created_at" not in table.c:
            errors.append(f"{table_name}: missing created_at timestamp")

        fk_count = sum(1 for constraint in table.constraints if isinstance(constraint, sa.ForeignKeyConstraint))
        if table_name in {"learner_profiles", "parental_consents", "diagnostic_sessions", "knowledge_gaps", "lessons"} and fk_count == 0:
            errors.append(f"{table_name}: expected at least one foreign key")

    for table_name, required_indexes in REQUIRED_INDEXES.items():
        if table_name not in metadata.tables:
            continue
        actual_indexes = names(metadata.tables[table_name].indexes)
        missing = required_indexes - actual_indexes
        if missing:
            errors.append(f"{table_name}: missing indexes {sorted(missing)}")

    for table_name, required_constraints in REQUIRED_CONSTRAINTS.items():
        if table_name not in metadata.tables:
            continue
        actual_constraints = names(metadata.tables[table_name].constraints)
        missing = required_constraints - actual_constraints
        if missing:
            errors.append(f"{table_name}: missing constraints {sorted(missing)}")

    if errors:
        print("Schema integrity validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("Schema integrity OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
