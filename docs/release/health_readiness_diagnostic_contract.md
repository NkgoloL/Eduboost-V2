---
title: Health and Readiness Diagnostic Contract
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

# Health and Readiness Diagnostic Contract

This contract captures the health/readiness dragons named during backend consolidation review.

## Dragon addressed

- ORM/schema drift may exist even when Alembic reports current.
- Health/readiness endpoints may return false positives if they check only narrow dependencies.
- Deep health must avoid unsafe public mutations.

## Health endpoint levels

| Level | Purpose | Allowed behavior |
|---|---|---|
| Lightweight health | Liveness/basic readiness | Cheap checks only; no schema introspection; no writes |
| Deep health | Internal/release diagnostics | Dependency checks, Alembic revision, required-table presence |
| Release evidence scripts | Offline/operator proof | Full ORM-vs-DB drift comparison, migration evidence, smoke checks |

## Required deep-health semantics

A future runtime deep-health implementation should be able to report:

- database connectivity
- Alembic current revision
- required core table presence
- audit persistence availability
- consent persistence availability
- Redis availability where required
- no unsafe public write operations

## Non-goals for this batch

- No runtime route behavior change.
- No database write from health checks.
- No automatic Alembic baseline/stamp operation.
- No schema repair before diagnostics prove the cause.
