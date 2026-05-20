# Database Backup Manifest

Manifest ID: `433b010c828b13ce`
Generated: `2026-05-20T18:19:21Z`
Branch: `fix/master-ci-cd-repair`
Commit: `4c0297e85f4a77147e22af491f7bcbe281b99bfc`

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
