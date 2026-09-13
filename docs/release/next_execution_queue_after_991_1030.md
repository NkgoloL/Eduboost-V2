---
title: "Release — Next Execution Queue After code_991_1030"
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
