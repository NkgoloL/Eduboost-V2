---
title: Database Restore Command
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

# Database Restore Command

## Purpose

`python3 scripts/run_database_restore.py --dry-run --target-environment staging`
provides a non-destructive restore command contract for CI.

## Required Inputs

- `DATABASE_URL`
- `BACKUP_ENCRYPTION_KEY`

## Safety Behavior

- staging dry-run is allowed in CI
- production target is blocked unless `--allow-production-target` is passed
- restore plans must verify learner, consent, and audit event counts

## Command

```bash
make database-restore-dry-run
```

## Verification

```bash
pytest -c pytest.ini tests/unit/test_database_restore_command.py -q --no-cov
```
