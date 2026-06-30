# Database Resilience Environment Matrix

## Purpose

This matrix records the environment variables required for backup and restore
evidence workflows.

## Backup Variables

| Variable | Required | Purpose |
| --- | --- | --- |
| `DATABASE_URL` | yes | source database connection |
| `BACKUP_ENCRYPTION_KEY` | yes | backup encryption key |
| `AZURE_STORAGE_CONNECTION_STRING` | yes | backup storage connection |
| `AZURE_STORAGE_CONTAINER` | yes | backup storage container |

## Restore Variables

| Variable | Required | Purpose |
| --- | --- | --- |
| `DATABASE_URL` | yes | restore target database connection |
| `BACKUP_ENCRYPTION_KEY` | yes | backup decryption key |

## Safety Rules

- production restore requires explicit approval
- CI must use dry-run backup and restore commands
- secrets must not be committed
- restore evidence must record learner, consent, and audit count status
