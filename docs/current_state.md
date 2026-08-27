---
title: EduBoost Current State
status: active
owner: release-management
reviewers: [engineering, product, privacy, security, operations]
audience: developer
source_of_truth: true
supersedes: []
superseded_by: null
last_reviewed: 2026-08-27
review_interval_days: 45
evidence_command: PYTHONPATH=. python3 scripts/true_state_remediation/execute_bundle.py --bundle B03 --phase verify --json
code_anchors: [app/api_v2.py, app/frontend/package.json, docs/roadmap/production_readiness/true_state_remediation_register.json]
---

# EduBoost Current State

This file is the canonical current-state summary for EduBoost V2 generated deterministically from single-source register state on 2026-08-27.

It is intentionally conservative. It records what is true now and what remains unauthorised before production, deployment, public beta, billing, live learner traffic, or further production-readiness implementation work can proceed.

## Product identity

EduBoost V2 is a South African Grade 4 Mathematics learning platform. Its active launch product scope is:

- **Launch-Active Scope**: South African Grade 4 Mathematics (CAPS-aligned).
- **Planned / Inactive Scope**: Grades R–3 and Grades 5–7, and subjects other than Mathematics remain in planning and are not active for launch.
- Diagnostic assessment and adaptive learner support.
- Knowledge-graph-grounded learning-state modelling.
- AI-assisted tutoring through controlled and grounded service boundaries.
- Parent/guardian visibility into progress, consent history, and reports.
- Personalised study plans based on curriculum coverage and mastery gaps.
- Gamification through achievements, points, and badges.
- POPIA-aware privacy, consent, audit, and data-rights workflows.

## Technical identity

The active technical direction is:

- FastAPI V2 backend.
- Next.js frontend under `app/frontend`.
- PostgreSQL 16 persistence with pgvector and Alembic migrations.
- Redis 7 backend for sessions, cache, and ARQ background workers.
- Content Factory and curriculum tooling for controlled source ingestion.
- Generated canonical OpenAPI contract under `docs/openapi.json` and `docs/openapi.yaml`.
- Deterministic Route Inventory under `docs/route_inventory.md`.
- True-State Remediation automation under `scripts/true_state_remediation/`.

## Canonical remediation state

```text
Remediation program: EduBoost V2 True-State Remediation
Active implementation bundle: B03 (CI Authority & Test-System Taxonomy Consolidation)
Bundle B01 (Release Gate Recovery): verified and closed
Bundle B02 (Canonical Truth and Toolchain): in_progress
Feature freeze: active
Controlled beta operational hold: active
```

## Controlled beta semantics

Controlled-beta fields are distinct and independently enforced:

- **Governance Authorization**: Authorized under controlled remediation scope.
- **Operational Safety**: Internal / staging verification only.
- **Activation Hold**: `active` (live external traffic prohibited).
- **Cohort Limits**: Staging cohort only (<50 test accounts).
- **Kill-Switch State**: Enabled (`FEATURE_FLAG_MAINTENANCE_MODE=true` fails closed).

## Release authority boundaries (fail-closed)

These remain strictly unauthorized:

```text
production_release_authorised: false
deployment_authorised: false
release_tag_authorised: false
public_beta_authorised: false
public_beta_live_traffic_authorised: false
live_learner_traffic_authorised: false
billing_launch_authorised: false
live_payment_processing_authorised: false
```

**Generation timestamp: 2026-08-27T12:12:33.786710+00:00**
