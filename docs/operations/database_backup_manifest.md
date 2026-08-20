# Database Backup Manifest

Manifest ID: `31759b07eeef1dd5`
Generated: `2026-08-19T20:02:45Z`
Branch: `fix/tsr-b01-gate-remediation`
Commit: `d5ae429bdec24b4d0123ea3362323fa3e4f25e4b`

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
