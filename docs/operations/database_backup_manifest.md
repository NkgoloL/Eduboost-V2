# Database Backup Manifest

Manifest ID: `dbcb92fb11bba3fa`
Generated: `2026-08-26T16:58:56Z`
Branch: `codex/tsr-b04-architecture-and-data-integrity`
Commit: `107d58c62d28a0d0a7a094f69894809af40f8db0`

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
