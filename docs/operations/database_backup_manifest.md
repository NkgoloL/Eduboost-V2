# Database Backup Manifest

Manifest ID: `42855f11d9fc6dc8`
Generated: `2026-05-12T11:14:44Z`
Branch: `codex/sync-frontend-lockfile-local`
Commit: `b7ef0eb83946b356402c33b69a8b905c8fbac2bd`

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
