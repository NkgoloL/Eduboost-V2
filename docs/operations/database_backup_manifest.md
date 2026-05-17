# Database Backup Manifest

Manifest ID: `61de9b5a1abcd405`
Generated: `2026-05-17T14:32:46Z`
Branch: `fix/github-ci-cd-errors`
Commit: `b5eb28226e73bc462ade0ff52d80b97ecdaf0621`

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
