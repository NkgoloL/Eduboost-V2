# Database Backup Manifest

Manifest ID: `1d983ecafc4d6676`
Generated: `2026-05-13T22:03:28Z`
Branch: `codex/production_readiness`
Commit: `ab75ab181e3328954bf1c0544237166ab5bcc8fb`

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
