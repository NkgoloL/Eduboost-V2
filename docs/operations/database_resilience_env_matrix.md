---
title: Database Resilience Environment Matrix
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

# Database Resilience Environment Matrix

## Purpose

This matrix records the environment variables required for backup and restore
evidence workflows.

## Backup Variables

| Variable | Required | Purpose |
| --- | --- | --- |
| `DATABASE_URL` | yes | source database connection |
| `BACKUP_ENCRYPTION_KEY` | yes | backup encryption key |
| `AZURE_STORAGE_CONNECTION_STRING` | yes | backup storage connection |
| `AZURE_STORAGE_CONTAINER` | yes | backup storage container |

## Restore Variables

| Variable | Required | Purpose |
| --- | --- | --- |
| `DATABASE_URL` | yes | restore target database connection |
| `BACKUP_ENCRYPTION_KEY` | yes | backup decryption key |

## Safety Rules

- production restore requires explicit approval
- CI must use dry-run backup and restore commands
- secrets must not be committed
- restore evidence must record learner, consent, and audit count status
