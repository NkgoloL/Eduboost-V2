# Database Backup Contract

## Purpose

EduBoost V2 must preserve recoverability for learner records, consent state,
audit evidence, and operational configuration.

## Required Data Domains

- learner profiles and mastery state
- assessments, diagnostic attempts, and study-plan state
- consent records and POPIA data-rights requests
- audit event records
- subscription and billing references
- operational configuration needed for restore

## Security Requirements

- backups must be encrypted
- backup encryption key must not be committed
- backup retention must be documented
- restore drills must verify integrity before production use
- restore evidence must be attached to the release record

## Configuration Evidence

The settings layer must expose:

- `BACKUP_ENCRYPTION_KEY`
- `BACKUP_RETENTION_DAYS`
- `AZURE_STORAGE_CONNECTION_STRING`
- `AZURE_STORAGE_CONTAINER`

## Baseline Command

```bash
make database-backup-contract-check
```
