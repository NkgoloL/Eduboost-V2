# Database Backup Manifest

Manifest ID: `20473b902a47040a`
Generated: `2026-08-03T14:18:09Z`
Branch: `fix/tsr-b01-gate-remediation`
Commit: `a55336c4112d0b994acb6a75e1db57e20e4fe381`

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
