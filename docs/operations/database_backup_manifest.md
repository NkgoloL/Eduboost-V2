# Database Backup Manifest

Manifest ID: `be2bb15746c4e766`
Generated: `2026-05-10T12:05:32Z`
Branch: `codex/cluster-c-popia-consent-audi`
Commit: `7f04f57d79d4c31d3532bafd11a9f9c2754dd7d5`

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
