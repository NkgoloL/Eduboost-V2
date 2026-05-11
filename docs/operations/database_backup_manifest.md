# Database Backup Manifest

Manifest ID: `8f18edce062f0639`
Generated: `2026-05-10T13:54:21Z`
Branch: `codex/cluster-c-popia-consent-audi`
Commit: `95e4e60b5374c33f492aed2f683305cd5f0a169a`

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
