---
title: RR-004 Workspace Hygiene Policy
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

# RR-004 Workspace Hygiene Policy

## Authority

RR-004 exists to make workspace hygiene reproducible and auditable before further roadmap work proceeds.

## Safe cleanup target

The safe cleanup target is a **dry-run** target. It identifies ignored build/cache artifacts without deleting them:

```bash
make rr004-ignored-artifact-clean-dry-run
```

This delegates to:

```bash
python3 scripts/workspace_hygiene/safe_cleanup_ignored_artifacts.py --dry-run --json
```

Actual deletion is intentionally not part of the evidence capture path and requires an explicit confirmation flag outside this closure evidence.

## Tracked-file-only audit inventory

The canonical tracked-file inventory command is:

```bash
git ls-files
```

The scanner records tracked-file counts, top-level counts, extension counts, docs/scripts/tests counts, and ignored artifact candidates.

## Boundary

This policy does not authorise production release, deployment, release tagging, public beta, runtime KG implementation, or destructive cleanup.
