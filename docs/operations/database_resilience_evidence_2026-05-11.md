# Database And Resilience Evidence

Date: 2026-05-11
Branch: `codex/pr19-database-resilience-evidence`
Base: `codex/pr18-frontend-verification`

## Purpose

This document records the local database, migration, backup, and restore
evidence available for the production-readiness PR series. It distinguishes
local contract evidence from environment-backed backup and restore proof.

## Local Green Checks

The following command passed:

```bash
make migration-check database-backup-contract-check database-restore-drill-docs-check database-resilience-env-matrix-check database-backup-integrity-check database-restore-integrity-check
```

Observed result:

- Schema integrity check passed.
- Migration graph check passed with 19 revisions and head `20260510_0200`.
- Database backup contract check passed.
- Database restore drill documentation check passed.
- Database resilience environment matrix check passed.
- Database backup integrity check passed.
- Database restore integrity check passed.

## Dry-Run Backup And Restore Preflight

The following dry-run commands completed without mutating data:

```bash
python3 scripts/run_database_backup.py --dry-run
python3 scripts/run_database_restore.py --dry-run --target-environment staging
```

Observed backup preflight result:

- `DATABASE_URL`: missing.
- `BACKUP_ENCRYPTION_KEY`: missing.
- `AZURE_STORAGE_CONNECTION_STRING`: missing.
- `AZURE_STORAGE_CONTAINER`: missing.
- A non-destructive backup plan was rendered.

Observed restore preflight result:

- `DATABASE_URL`: missing.
- `BACKUP_ENCRYPTION_KEY`: missing.
- `target_environment`: allowed for `staging`.
- A non-destructive restore plan was rendered.

## Release Blockers

- No disposable PostgreSQL migration run was executed in this PR.
- No encrypted backup artifact was produced.
- No restore drill was executed against a separate environment.
- Learner, consent, and audit count integrity were not verified against a
  restored database.
- Redis outage and recovery behavior still needs environment-backed evidence.

## Release Claim

This PR establishes local migration/schema and database-resilience contract
evidence. It does not claim production backup readiness, restore readiness,
Redis resilience, or live data integrity.
