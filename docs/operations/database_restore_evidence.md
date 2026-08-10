# Database Restore Evidence

Generated: `2026-08-03T14:18:09Z`
Branch: `fix/tsr-b01-gate-remediation`
Commit: `a55336c4112d0b994acb6a75e1db57e20e4fe381`

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
