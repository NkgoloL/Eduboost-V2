# Database Backup Manifest

Manifest ID: `cc422dd8acd3466c`
Generated: `2026-08-29T09:37:19Z`
Branch: `feature/coverage-target-90`
Commit: `d81bc05b230256f6c4ab39540ccb03ed4b52bcfd`

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
