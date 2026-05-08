# Backup and Restore Runbook

This runbook turns the disaster-recovery policy into executable operator steps. Cloud backup scheduling is externally configured, but the repository now contains validation gates, expected evidence, and local helper scripts.

## Backup requirements

| Requirement | Policy |
|---|---|
| Scope | PostgreSQL primary database and audit tables |
| Encryption | Required before backup leaves the database host/network |
| Failure domain | Backup destination must not share the same failure domain as the database |
| Retention | See `docs/disaster_recovery.md` |
| Alerting | `EduBoostBackupFailure` and `EduBoostBackupStale` |
| Evidence | checksum, object path, timestamp, size, encryption status, restore drill result |

## Manual backup drill

```bash
DATABASE_URL=postgresql://user:pass@host:5432/db \
BACKUP_ENCRYPTION_KEY=... \
./scripts/backup_postgres.sh
```

## Restore drill

```bash
DATABASE_URL=postgresql://user:pass@restore-host:5432/restore_db \
BACKUP_FILE=backups/eduboost_YYYYmmdd_HHMMSS.dump.gpg \
BACKUP_ENCRYPTION_KEY=... \
./scripts/restore_postgres.sh
```

After restore, run:

```bash
make migration-check
python scripts/validate_schema_integrity.py
```

Then verify:

- audit hash chain samples
- consent states
- learner records
- billing/subscription states
- diagnostic sessions
- lesson metadata

## Monthly restore drill

A production launch requires one clean restore into a disposable environment. After launch, run one restore drill monthly and attach the result to the operations evidence folder.
