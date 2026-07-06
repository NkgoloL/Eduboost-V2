---
title: Auth DB Lifecycle Proof Report
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

# Auth DB Lifecycle Proof Report

Generated at: `2026-06-27T02:18:59Z`

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
