---
title: "Release — Health and Readiness Diagnostic Contract"
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
