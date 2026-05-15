# Database Backup Manifest

Manifest ID: `ea3931f81d08ed0b`
Generated: `2026-05-15T20:10:20Z`
Branch: `codex/production_readiness`
Commit: `29a82791fcdd57406da52160d1431d6cf54299bf`

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
