# Database Backup Manifest

Manifest ID: `970ae70d52f9b504`
Generated: `2026-05-17T09:36:06Z`
Branch: `codex/production_readiness`
Commit: `7edd5965c75337cddf07bac3852e53bc4ff5f689`

## Backup Metadata

| Field | Value |
| --- | --- |
| Backup artifact ID | `pending-backup-artifact` |
| Target environment | `staging` |
| Retention days | `30` |
| Encrypted | `yes` |

## Required Verification

- backup artifact is encrypted
- backup artifact ID is recorded
- retention period is recorded
- restore drill evidence is linked before production promotion

## Related Commands

```bash
make database-backup-dry-run
make database-backup-contract-check
make database-restore-drill-docs-check
```
