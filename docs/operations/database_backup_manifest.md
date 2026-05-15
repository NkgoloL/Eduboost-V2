# Database Backup Manifest

Manifest ID: `12b6dd2aa4365ed7`
Generated: `2026-05-15T19:23:49Z`
Branch: `codex/production_readiness`
Commit: `617b3c330b8f9b7f7111c1d288bdedc915a195c0`

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
