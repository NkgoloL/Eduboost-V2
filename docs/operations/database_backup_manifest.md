# Database Backup Manifest

Manifest ID: `f8e949db7780a22c`
Generated: `2026-05-10T13:45:54Z`
Branch: `codex/cluster-c-popia-consent-audi`
Commit: `3ad3c38ef7db8e86fcae5c540228716f98ef5776`

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
