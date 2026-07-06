---
title: ARQ Dependency and Worker Import Repair Report
status: release-record
owner: release-management
reviewers: [release-management, evidence-custodian, documentation-governance]
audience: release-reviewer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-06
review_interval_days: 180
evidence_command: make docs-housekeeping-stage7-check
code_anchors: [docs/release, docs/documentation/stage_7_release_archive_backlog_codemaps_governance.md]
---

# ARQ Dependency and Worker Import Repair Report

Generated at: `2026-05-19T19:36:10Z`

**Status:** implemented

## Dependency files patched

- None

## Runtime import changes

- `app/modules/jobs.py` import compatibility patched: `False`
- `app/services/arq_import_compat.py` provides import-safe RedisSettings/cron fallback.

## Stale checks patched

- None

## Boundary

The import-safe fallback is for local/test import safety only. Production worker execution still requires `arq` from the pinned dependency files.
