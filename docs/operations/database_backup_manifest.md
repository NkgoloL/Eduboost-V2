# Database Backup Manifest

Manifest ID: `4acdf5359b5dfc9d`
Generated: `2026-05-18T08:38:26Z`
Branch: `fix/github-ci-cd-errors`
Commit: `996786f9faffec5ada9651e9637d40c3ce574e97`

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
