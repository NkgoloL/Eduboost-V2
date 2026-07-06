---
title: Next Execution Queue After code_951_990
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

# Next Execution Queue After code_951_990

## Recommended next batch

`code_991_1030`: Auth HTTP success-path tests and refresh-token authorization scope proof.

## Scope candidates

1. Register success path with in-memory or transactional test DB.
2. Login success/failure path.
3. Refresh success path preserving guardian learner scope.
4. Duplicate registration and wrong password failure tests.
5. Remove any residual auth extraction compatibility code no longer needed.
