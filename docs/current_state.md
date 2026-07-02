---
title: EduBoost Current State
status: active
owner: release-management
reviewers: [engineering, product, privacy, security, operations]
audience: developer
source_of_truth: true
supersedes: []
superseded_by: null
last_reviewed: 2026-07-02
review_interval_days: 14
evidence_command: make docs-housekeeping-check && make openapi-check && make runtime-check
code_anchors: [app/api_v2.py, app/frontend/package.json, docs/documentation/source_of_truth.yml]
---

# EduBoost Current State

This is the bounded current-state summary for EduBoost V2. It is intentionally conservative: it describes what the repository is intended to be and what must be re-verified before any readiness claim is made.

## Product identity

EduBoost V2 is a learning platform for South African Grade 4 Mathematics. Its core product direction is:

- CAPS-aligned curriculum coverage.
- Diagnostic assessment and adaptive learner support.
- AI-assisted tutoring through controlled and grounded service boundaries.
- Parent/guardian visibility into progress, consent history, and reports.
- Personalised study plans based on curriculum coverage and mastery gaps.
- Gamification through achievements, points, and badges.
- POPIA-aware privacy, consent, audit, and data-rights workflows.

## Technical identity

The active technical direction is:

- FastAPI V2 backend.
- Next.js frontend under `app/frontend`.
- PostgreSQL persistence with Alembic migrations.
- Redis-backed sessions, jobs, or runtime support where configured.
- Content Factory and curriculum tooling for controlled source ingestion and lesson material production.
- Generated OpenAPI contract under `docs/openapi.json`.
- Release and evidence automation under scripts, Makefile targets, and `docs/release*` areas.

## Known caution areas

The documentation corpus must not claim broad production or release readiness without fresh evidence. The June 2026 technical audit identified release-blocking concerns including missing Content Factory runtime registry artifacts, POPIA auth-shape drift, frontend/backend route drift, CI package-manager drift, stale OpenAPI output, frontend lint/env-check drift, and dependency scan enforcement gaps.

## Documentation truth boundary

This file is not a release approval. It is a navigation document. Release decisions must be made through the release source-of-truth documents and evidence commands listed in `docs/documentation/source_of_truth.yml`.

## Reconciled roadmap and governance state

RR-009 governance/process reconciliation records that current work selection is governed by `docs/roadmap/reconciliation/outstanding_work_register.md` and must cite an `RR-###` item.

Current closed reconciliation items include RR-001 through RR-008, with RR-006 completed earlier and retained as a valid out-of-order closure. New roadmap or product work remains blocked unless reconciled into the RR register.

Known residual caveats remain visible:

- RR-003 is valid, but its fallback coverage baseline recorded `0.0` because full test collection had pre-existing blockers.
- RR-006 is valid, but its evidence PR merged with only the required branch-protection check blocking; other non-required checks were red.
- RR-010 beta outcome reporting, RR-015 external approvals, RR-016 operational drills, and RR-017 release safety controls remain outstanding.

Production release, deployment, release tagging, public beta, and runtime KG implementation remain unauthorised.

**Current-state refresh cadence recorded: true**
