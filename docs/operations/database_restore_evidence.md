# Database Restore Evidence

Generated: `2026-05-10T13:45:54Z`
Branch: `codex/cluster-c-popia-consent-audi`
Commit: `3ad3c38ef7db8e86fcae5c540228716f98ef5776`

## Restore Metadata

| Field | Value |
| --- | --- |
| Backup artifact ID | `pending-backup-artifact` |
| Target environment | `staging` |
| Integrity status | `pending` |
| Learner count status | `pending` |
| Consent count status | `pending` |
| Audit count status | `pending` |

## Required Verification Commands

```bash
make database-restore-dry-run
make runtime-check
make route-inventory-check
make popia-consent-closure-check
make cluster-d-closure-check
```

## Release Use

Production promotion is blocked until restore evidence records learner,
consent, and audit integrity status.
