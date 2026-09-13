---
title: "Release — Next Execution Queue After code_1031_1070"
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
# Next Execution Queue After code_1031_1070

## Recommended next batch

`code_1071_1110`: production repository auth fixture proof.

## Scope candidates

1. Build transactional test DB fixture using the project SQLAlchemy models.
2. Register success path through real repositories.
3. Duplicate registration through real unique constraints/repository checks.
4. Login through real password hashing.
5. Refresh token persistence/replay through real token store.
6. Guardian learner scope via real learner repository relationship.
