# PR-005 — Database/migration integrity

## Scope

This patch hardens the database baseline, migration graph, and disaster-recovery documentation without introducing new user-facing product flows.

## Implemented

### Migration graph integrity

- Corrected `20260507_1200_popia_consent_audit_hardening.py` so `down_revision` references the real prior revision, `0009_add_subject_mastery`.
- Added `20260507_1330_database_integrity_constraints.py` as the new migration head.
- Retired `0002_add_missing_tables.py` into an explicit no-op because its original legacy table definitions conflicted with the canonical V2 schema.
- Fixed `0004_add_rlhf_pipeline.py` so `lesson_feedback.lesson_id` matches the canonical `lessons.id` string key.
- Added `scripts/verify_migration_graph.py` to catch broken revision links, duplicate heads, duplicate bases, and non-conforming new migration names.

### ORM/schema integrity

- Added timestamps to `parental_consents`, `subject_mastery`, and `stripe_webhook_events`.
- Added missing `DiagnosticSession.items_correct` ORM mapping for the existing `0003` migration.
- Added ORM mappings for `lesson_feedback` and `rlhf_exports` so the active migration history and metadata remain aligned.
- Aligned SQLAlchemy enum persistence with the enum values used by the database migrations.
- Added `scripts/validate_schema_integrity.py` to verify required tables, primary keys, timestamps, foreign keys, indexes, and constraints.

### Constraints and indexes

Added production indexes for:

- Stripe customer and subscription lookups.
- Active premium subscription lookup.
- Consent status and active consent lookup.
- Diagnostic session creation/incomplete lookup.
- Subject mastery update ordering.
- Stripe webhook processed-time lookup.

Added database-level constraints for:

- Learner grade, XP, and streak ranges.
- Consent expiry/revocation chronology.
- Audit event type and hash/HMAC shape.
- IRT item grade, answer option, and discrimination range.
- Knowledge-gap severity range.
- Lesson grade and feedback-score ranges.
- Subject mastery standard-error range.
- RLHF feedback/export count ranges.

### Migration discipline and DR docs

- Added `docs/database/migration_discipline.md`.
- Added `docs/database/schema_integrity.md`.
- Added `docs/disaster_recovery.md`.
- Added local-only synthetic seed data in `data/synthetic/`.
- Added `make migration-check`, `make schema-integrity`, and `make migration-smoke`.
- Added migration graph and ORM schema checks to the CI schema-drift job.

## TODO items completed

- TODO-048 — Primary keys, timestamps, and FKs confirmed for core production tables.
- TODO-049 — Production indexes added/verified.
- TODO-050 — Database constraints added for core invariants.
- TODO-057 — Destructive migration rollback strategy documented.
- TODO-058 — Migration naming convention documented/enforced for new migrations.
- TODO-059 — Backup/staging/validation/rollback evidence required for sensitive migrations.
- TODO-061 — Synthetic local seed data added.
- TODO-243 — Backup retention documented.
- TODO-246 — RPO/RTO documented.
- TODO-248 — Redis recoverability documented.
- TODO-249 — Disaster recovery document created.
- TODO-250 — Provider outage plans documented.

## Intentionally left partial/open

- TODO-051 — Active consent/subscription partial indexes are added; refresh-token sessions and background jobs are Redis-backed, so PostgreSQL partial indexes do not apply.
- TODO-052 — Transaction-boundary review needs a service-by-service implementation pass.
- TODO-053 — Slow-query logging requires staging/production database access.
- TODO-054 — Performance tests remain a later performance PR.
- TODO-060 — Migration smoke target exists, but production-like data-volume runs require a disposable database environment.
- TODO-245/TODO-247 — Restore drill and post-restore validation are documented but require cloud/staging execution.

## Validation

Passed locally in the repo snapshot:

```bash
PYTHONPATH=. python scripts/validate_schema_integrity.py
PYTHONPATH=. python scripts/verify_migration_graph.py
PYTHONPATH=. make migration-check
PYTHONPATH=. pytest tests/unit/test_migration_graph.py tests/unit/test_schema_integrity.py --no-cov -q
python -m py_compile app/models/__init__.py scripts/verify_migration_graph.py scripts/validate_schema_integrity.py alembic/versions/0002_add_missing_tables.py alembic/versions/0004_add_rlhf_pipeline.py alembic/versions/20260507_1200_popia_consent_audit_hardening.py alembic/versions/20260507_1330_database_integrity_constraints.py
```

Not run locally because no disposable PostgreSQL service is available in the sandbox:

```bash
DATABASE_URL=postgresql+asyncpg://... make migration-smoke
```
