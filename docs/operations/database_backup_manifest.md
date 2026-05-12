# Database Backup Manifest

Manifest ID: `9d82404b96c82f21`
Generated: `2026-05-12T19:10:32Z`
Branch: `master`
Commit: `e8ac491be7bc3f61cd12ebd08d649f8e8cdcaa10`

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
