# Database Backup Manifest

Manifest ID: `4dcae80c4edf854d`
Generated: `2026-09-03T09:24:01Z`
Branch: `fix/governance-verification-remediation`
Commit: `51487956b21470877d482128092c01595e92be39`

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
