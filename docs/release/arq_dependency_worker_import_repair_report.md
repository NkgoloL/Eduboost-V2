---
title: "Release — ARQ Dependency and Worker Import Repair Report"
status: "active"
owner: "release"
reviewers: ['release', 'engineering']
audience: "internal"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-09-13"
review_interval_days: 90
evidence_command: "make docs-housekeeping-check"
code_anchors: "[]"
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
