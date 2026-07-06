---
title: Next Execution Queue After code_991_1030
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

# Next Execution Queue After code_991_1030

## Recommended next batch

`code_1031_1070`: transactional auth repository/DB proof.

## Scope candidates

1. Build isolated transactional test DB fixture for auth lifecycle.
2. Register success path persists account/guardian state.
3. Duplicate registration fails at repository/database boundary.
4. Login validates password hash and returns token response.
5. Refresh token success path uses stored token state and rejects replay/expired tokens.
6. Guardian learner scope is loaded from persisted learner relationships.
