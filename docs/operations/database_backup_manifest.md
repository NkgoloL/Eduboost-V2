# Database Backup Manifest

Manifest ID: `2a72d2dfae2434b8`
Generated: `2026-05-19T23:07:25Z`
Branch: `codex/production_readiness`
Commit: `9e706b9e0b787b0e4fb7324c9beefeb3fe35d2a4`

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
