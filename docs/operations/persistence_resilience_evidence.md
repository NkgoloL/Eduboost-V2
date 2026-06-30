# Persistence Resilience Evidence

This document is the review index for database persistence, migrations,
backup/restore, and recoverability. It records evidence wiring only; staging
and production readiness still require green environment-specific runs.

## Migration Discipline

- Migration graph checker: `scripts/verify_migration_graph.py`
- Migration smoke command: `make migration-smoke`
- Migration discipline doc: `docs/database/migration_discipline.md`
- Required local check: `make migration-check`

## Schema Integrity

- Schema validator: `scripts/validate_schema_integrity.py`
- Schema integrity doc: `docs/database/schema_integrity.md`
- Required local check: `make schema-integrity`

## Backup Dry Run

- Backup command: `scripts/run_database_backup.py`
- Backup command evidence: `docs/operations/database_backup_command.md`
- Backup manifest generator: `scripts/generate_database_backup_manifest.py`
- Required dry run: `make database-backup-dry-run`

## Restore Dry Run

- Restore command: `scripts/run_database_restore.py`
- Restore command evidence: `docs/operations/database_restore_command.md`
- Restore evidence generator: `scripts/generate_database_restore_evidence.py`
- Required dry run: `make database-restore-dry-run`

## Integrity And Approval

- Backup integrity check: `make database-backup-integrity-check`
- Restore integrity check: `make database-restore-integrity-check`
- Production restore approval guard: `make production-restore-approval-check`
- Environment matrix check: `make database-resilience-env-matrix-check`

## RPO/RTO

- Runbook: `docs/operations/backup_restore_runbook.md`
- Restore drill doc: `docs/operations/database_restore_drill.md`
- Data resilience evidence index: `docs/operations/data_resilience_evidence_index.md`

## Redis Recoverability

Redis is treated as an operational dependency whose recoverability model must be
explicit before release. Until a Redis outage test exists, Redis loss impact on
token revocation, cache, job status, and rate limiting remains a verification
gap.

## Aggregate Check

Run the aggregate check with:

```bash
make persistence-resilience-check
```

## Verification Gaps

- `alembic upgrade head` still needs a green disposable PostgreSQL run.
- Backup and restore dry runs still need environment-specific evidence outside
  local documentation checks.
- Redis outage behavior still requires executable tests.
- RPO/RTO values need release-owner approval before public beta.
