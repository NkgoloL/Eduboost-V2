---
title: EduBoost Current State
status: active
owner: release-management
reviewers: [engineering, product, privacy, security, operations]
audience: developer
source_of_truth: true
supersedes: []
superseded_by: null
last_reviewed: 2026-09-13
review_interval_days: 45
evidence_command: PYTHONPATH=. python3 scripts/true_state_remediation/verify_final_program.py --json
code_anchors: [app/api_v2.py, app/frontend/package.json, docs/roadmap/production_readiness/true_state_remediation_register.json]
---

# EduBoost Current State

This file is the canonical current-state summary for EduBoost V2 generated deterministically from single-source register state on 2026-09-13.

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
Remediation program: EduBoost V2 True-State Remediation (Completed)
Active implementation bundle: completed (Bundles B01-B07 verified and closed)
Bundle B01 (Release Gate Recovery): verified and closed
Bundle B02 (Canonical Truth and Toolchain): verified and closed
Bundle B03 (CI Authority & Test-System Taxonomy Consolidation): verified and closed
Bundle B04 (Architecture & Schema Lifecycle): verified and closed
Bundle B05 (Security, Privacy & Educational Validity): verified and closed
Bundle B06 (API Rationalisation & Operations): verified and closed
Bundle B07 (Release Candidate Pilot & Stabilisation): verified and closed
Feature freeze: active
Controlled beta operational hold: active
Active production-readiness item: PRD-11.0R.RUNTIME-RESTORE.EXECUTION-8
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

## Test Suite & Coverage Baseline

- **Repository Statement Coverage**: ~95.7% across `app/` (Target: >90.9% achieved and exceeded; CI and Contract Floor strictly enforced at 90%).
- **Enforced CI & Contract Floor**: **90%** minimum line coverage enforced in `.github/workflows/pr-core.yml`, `Makefile`, and `coverage_contract.json`.
- **Package-Level Verified Coverage**:
  - `app/core`: **97.7%** statement coverage (2,534 statements)
  - `app/domain`: **96.2%** statement coverage (2,977 statements)
  - `app/security`: **100.0%** statement coverage (272 statements)
  - `app/repositories`: **98.5%** statement coverage (1,139 statements)
  - `app/models`: **97.8%** statement coverage (2,135 statements)
  - `app/api_v2_routers`: **97.2%** statement coverage (2,261 statements)
  - `app/api_v2_deps`: **99.4%** statement coverage (271 statements)
  - `app/modules`: **97.3%** statement coverage (8,043 statements)
  - `app/services`: **92.9%** statement coverage (16,106 statements)
  - `app/middleware, utils, jobs`: **100.0%** statement coverage (244 statements)
- **Deterministic Evidence**: Batches 412 through 428 passing with 1,500+ unit tests and 0 failures. Full report at [`docs/reports/coverage_target_90_completion_report.md`](reports/coverage_target_90_completion_report.md).

## Governance & Reconciled Registers

- Current-state refresh cadence recorded: true
- Reconciled register rule: All roadmap items follow the RR-### register structure in `docs/roadmap/reconciliation/outstanding_work_register.md`.
- Historical caveats: RR-003 fallback coverage baseline resolved (>90.9% target achieved at 95.7%); RR-006 evidence merged with non-required checks non-blocking; RR-010 beta outcome reporting outstanding; RR-016 operational drills outstanding.

**Generation timestamp: 2026-09-13T13:38:00.000000+00:00**
