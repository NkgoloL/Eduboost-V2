# Database Backup Manifest

Manifest ID: `3bda55e39bde32fc`
Generated: `2026-05-15T19:49:14Z`
Branch: `codex/production_readiness`
Commit: `3722ce2e590e30578a0ffad4cfb5c81bd0555b0b`

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
