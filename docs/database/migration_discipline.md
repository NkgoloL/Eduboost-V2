# Database migration discipline

EduBoost treats database migrations as production change-control artifacts, not incidental code changes.

## Naming convention

All new migration files must use:

```text
YYYYMMDD_HHMM_<short_description>.py
```

Examples:

```text
20260507_1330_database_integrity_constraints.py
20260601_0900_add_billing_webhook_indexes.py
```

Legacy migrations with older names are allowed only because they already exist in the historical chain. New migrations that do not follow the timestamped convention should fail review.

## Required migration evidence

Every migration touching learner, guardian, consent, audit, subscription, or billing data must include the following in the PR description:

| Evidence | Required content |
|---|---|
| Backup plan | Snapshot or logical backup command and storage destination |
| Staging dry-run | `alembic upgrade head` result against staging-like data |
| Validation | SQL or script proving row counts, constraints, and key workflows remain intact |
| Rollback plan | Whether rollback is `alembic downgrade -1`, forward-fix, or restore-from-backup |
| Data-risk classification | Additive, backfill, destructive, or irreversible |

## Destructive migration rule

Destructive migrations include dropping columns/tables, rewriting identifiers, changing encryption format, bulk deleting data, or making nullable columns non-null after backfill.

A destructive migration must not be merged unless:

1. A backup has been taken and restore-tested.
2. A staging dry-run has been completed with representative data volume.
3. A validation script exists.
4. A rollback or forward-fix plan is documented.
5. POPIA impact has been reviewed.

## Local checks

Run these before opening a migration PR:

```bash
PYTHONPATH=. make migration-check
DATABASE_URL=postgresql+asyncpg://... make migration-smoke
```

`migration-check` is database-free and verifies static revision graph/schema invariants. `migration-smoke` requires a disposable database and performs upgrade/downgrade/upgrade.

## Current migration graph correction

The POPIA hardening migration now depends on `0009_add_subject_mastery`, which is the active revision after the production index and subject mastery chain. This corrects a broken pointer to a filename-like identifier instead of a real Alembic revision ID.

`0002_add_missing_tables` is retained as a no-op graph node because the original contents represented legacy tables that conflicted with the canonical V2 schema. This preserves migration history without recreating duplicate or obsolete tables on fresh bootstrap.
