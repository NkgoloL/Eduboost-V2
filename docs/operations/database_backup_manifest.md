# Database Backup Manifest

Manifest ID: `2cba8353e2ec8960`
Generated: `2026-05-16T17:01:11Z`
Branch: `codex/production_readiness`
Commit: `c7a02d63c7ae117a8e1b9a25f94853e37c6ed2a0`

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
