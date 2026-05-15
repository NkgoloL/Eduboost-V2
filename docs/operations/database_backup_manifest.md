# Database Backup Manifest

Manifest ID: `1fd1b45b15e90aa2`
Generated: `2026-05-15T07:07:11Z`
Branch: `codex/production_readiness`
Commit: `434281675253dda2f0dd011a8598a56dfa775c4a`

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
