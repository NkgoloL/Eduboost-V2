---
title: "Release — Next Execution Queue After DIAG-001 / code_1231_1270"
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
# Next Execution Queue After DIAG-001 / code_1231_1270

## Next batch

`AUTH-REPO-001 / code_1271_1310` — production repository auth fixture proof.

## Scope candidates

1. Discover actual auth models and repositories at HEAD.
2. Build transactional test DB fixture.
3. Exercise real repository-backed register/login/refresh where feasible.
4. Prove refresh replay rejection against actual token store.
5. Prove guardian learner scope from real learner repository rows.
6. Keep no-false-closure status if repository shape blocks safe proof.
