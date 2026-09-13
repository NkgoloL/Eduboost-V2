---
title: "Release — Auth DB Lifecycle Proof Report"
status: "active"
owner: "release"
reviewers: ['release', 'engineering']
audience: "developer"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-09-13"
review_interval_days: 90
evidence_command: "make docs-housekeeping-check"
code_anchors: "[]"
---
# Auth DB Lifecycle Proof Report

Generated at: `2026-09-10T00:47:48Z`

**Status:** transactional_sqlite_auth_lifecycle_proof

| Check | Value |
|---|---|
| Registered guardian learner IDs | ['learner-1'] |
| Login guardian learner IDs | ['learner-1'] |
| Refresh guardian learner IDs | ['learner-1'] |
| Duplicate registration rejected | True |
| Refresh replay rejected | True |

## Proofs

- register persists user, guardian and learner rows
- duplicate registration is rejected by DB-backed lookup
- login verifies stored password hash
- wrong password is rejected
- refresh token is persisted and consumed
- refresh replay is rejected
- guardian_learner_ids are loaded from DB learner rows

## Boundary

This proof uses an isolated SQLite fixture. It does not mutate production data and does not prove production repository conformance.
