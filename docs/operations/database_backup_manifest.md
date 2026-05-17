# Database Backup Manifest

Manifest ID: `4241ec3d20993c89`
Generated: `2026-05-17T22:11:39Z`
Branch: `codex/production_readiness`
Commit: `02f3babd855703460eefc1727f5fdc71f44d2a60`

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
