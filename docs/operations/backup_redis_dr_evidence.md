---
title: Backup, Redis, And DR Evidence
status: active
owner: operations
reviewers: [operations, security, release-management]
audience: operator
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-06
review_interval_days: 90
evidence_command: make docs-housekeeping-stage7-check
code_anchors: [docs/operations, docs/documentation/stage_7_release_archive_backlog_codemaps_governance.md]
---

# Backup, Redis, And DR Evidence

This index links backup/restore dry-run, Redis recoverability, RPO/RTO, and DR
evidence.

- DR plan: `docs/disaster_recovery.md`
- Redis revocation ADR: `docs/adr/0008-redis-token-revocation.md`
- Backup/restore runbook: `docs/operations/backup_restore_runbook.md`
- Backup command: `scripts/run_database_backup.py`
- Restore command: `scripts/run_database_restore.py`
- Integrity checks: `make database-backup-integrity-check` and
  `make database-restore-integrity-check`

Run:

```bash
make backup-redis-dr-check
```

Verification gaps: scheduled staging restore, Redis outage exercise, and signed
RPO/RTO acceptance.
