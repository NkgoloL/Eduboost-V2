# Database Backup Manifest

Manifest ID: `666ecbe9a5c078f9`
Generated: `2026-05-17T12:14:09Z`
Branch: `codex/production_readiness`
Commit: `859695dac8184e8d9696272ed9f74aecdd267ef0`

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
