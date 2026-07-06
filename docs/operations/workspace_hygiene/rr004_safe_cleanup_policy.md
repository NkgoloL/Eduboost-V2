---
title: RR-004 Safe Cleanup Policy
status: active-policy
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

# RR-004 Safe Cleanup Policy

## Default behavior

Ignored-artifact cleanup is dry-run first and read-only by default:

```bash
git clean -ndX
```

The repository helper exposes this through:

```bash
python3 scripts/workspace_hygiene/safe_cleanup_ignored_artifacts.py --dry-run --json
```

## Actual deletion guard

Actual deletion is not used for RR-004 evidence capture. If an operator chooses to clean ignored artifacts outside the evidence path, the helper requires both:

```bash
--execute --confirm-delete-ignored-artifacts
```

This is a deliberate guardrail to prevent accidental deletion of local-only ignored files.

## Boundary

RR-004 records cleanup authority and reproducible counts only. It does not delete artifacts as part of the captured evidence.
