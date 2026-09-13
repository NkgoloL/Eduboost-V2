---
title: "PRD-2.0-2.3 — Runtime KG Persistence Foundation"
status: "active"
owner: "product"
reviewers: ['product', 'engineering']
audience: "internal"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-09-13"
review_interval_days: 90
evidence_command: "make docs-housekeeping-check"
code_anchors: "[]"
---
# PRD-2.0-2.3 — Runtime KG Persistence Foundation

## Scope

This bundle combines the PRD-2 stream start with the first runtime KG
implementation layer:

- PRD-2.0 — Runtime KG stream authority and register.
- PRD-2.1 — Alembic migration and ORM persistence model.
- PRD-2.2 — Idempotent graph loader and repository boundary.
- PRD-2.3 — Runtime read/projection hooks behind feature flag.

## Non-goals

- No production release authorisation.
- No live learner traffic authorisation.
- No public beta authorisation.
- No PRD-3 implementation.
- No default runtime switch-on.

## Acceptance

- PRD-1 closure verifier remains green.
- Runtime KG scripts compile.
- Runtime KG unit tests pass.
- Verifier reports `valid: true` after capture.
- Register advances to `PRD-2.4-2.6`.
