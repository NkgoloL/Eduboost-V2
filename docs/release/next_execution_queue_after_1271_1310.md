---
title: Next Execution Queue After AUTH-REPO-001 / code_1271_1310
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

# Next Execution Queue After AUTH-REPO-001 / code_1271_1310

## Recommended next batch

`AUTH-CLEAN-001 / code_1311_1350` — auth service cleanup and monkey-patch removal, or `LEGAL/SEC/CONTENT` external evidence kickoff if release track is the priority.

## Scope candidates

1. Move lifecycle methods directly into `AuthApplicationService` if any module-bottom assignment remains.
2. Preserve repository fixture tests as the regression guard.
3. Add live Postgres/staging auth smoke when deployment evidence is available.
4. Continue external legal/security/content approval tracking.
