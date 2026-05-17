# Database Backup Manifest

Manifest ID: `2d12b9ff03640d03`
Generated: `2026-05-17T08:28:59Z`
Branch: `codex/production_readiness`
Commit: `03c9056ffa30e080627b73933baaef11698da853`

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
