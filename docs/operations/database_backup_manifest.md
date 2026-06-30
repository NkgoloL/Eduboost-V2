# Database Backup Manifest

Manifest ID: `fdf3cdc7dc71ac55`
Generated: `2026-06-12T17:40:07Z`
Branch: `phase-11/technical-debt-burn-down`
Commit: `a70b57616bb29572fcb57961b91a3f68f0c66329`

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
