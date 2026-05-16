# Database Restore Evidence

Generated: `2026-05-16T17:01:12Z`
Branch: `codex/production_readiness`
Commit: `c7a02d63c7ae117a8e1b9a25f94853e37c6ed2a0`

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
