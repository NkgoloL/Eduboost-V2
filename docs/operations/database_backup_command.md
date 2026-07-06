---
title: Database Backup Command
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

# Database Backup Command

## Purpose

`python3 scripts/run_database_backup.py --dry-run` provides a non-destructive
backup command contract for CI.

## Required Inputs

- `DATABASE_URL`
- `BACKUP_ENCRYPTION_KEY`
- `AZURE_STORAGE_CONNECTION_STRING`
- `AZURE_STORAGE_CONTAINER`

## CI Behavior

CI uses dry-run mode only. The command validates required inputs and renders a
backup plan without dumping data.

## Command

```bash
make database-backup-dry-run
```

## Verification

```bash
pytest -c pytest.ini tests/unit/test_database_backup_command.py -q --no-cov
```
