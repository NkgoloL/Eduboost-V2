---
title: Database Backup Integrity Check
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

# Database Backup Integrity Check

## Purpose

This check validates that the generated backup manifest records the minimum
integrity evidence needed for release review.

## Required Evidence

- backup artifact ID
- retention period
- encrypted status
- restore drill linkage
- backup dry-run command reference

## Command

```bash
make database-backup-integrity-check
```

## Verification

```bash
pytest -c pytest.ini tests/unit/test_database_backup_integrity.py -q --no-cov
```
