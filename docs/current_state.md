---
title: EduBoost Current State
status: active
owner: release-management
reviewers: [engineering, product, privacy, security, operations]
audience: developer
source_of_truth: true
supersedes: []
superseded_by: null
last_reviewed: '2026-09-22'
review_interval_days: 14
evidence_command: "make runtime-check && make openapi-check && make route-inventory-check"
code_anchors:
  - app/api_v2.py
  - app/core/arq_worker.py
  - app/frontend/package.json
  - docs/roadmap/production_readiness/coverage_contract.json
  - docs/roadmap/production_readiness/prd_4a_longitudinal_educational_validation_register.json
  - docs/roadmap/production_readiness/prd11_production_release_register.json
---

# EduBoost Current State

This file is the canonical current-state summary for EduBoost V2, reconciled against active code, database migrations, CI contracts, and governance registers on 2026-09-22.

It is intentionally conservative. It records empirical repository truth and enforces strict, fails-closed release boundaries: production deployment, public beta, billing, live learner traffic, and unverified mastery claims remain blocked until their authoritative prerequisites are satisfied.

## Product Identity

EduBoost V2 is a South African Grade 4 Mathematics learning platform aligned with the Curriculum and Assessment Policy Statement (CAPS). Its active launch product scope is:

- **Launch-Active Scope**: South African Grade 4 Mathematics (`grade4_mathematics_en`, CAPS-aligned).
- **Planned / Inactive Scope**: Grades R–3 and Grades 5–7, and subjects other than Mathematics remain in planning and are strictly inactive for launch.
- Diagnostic assessment and adaptive learner support.
- Knowledge-graph-grounded learning-state modelling.
- AI-assisted tutoring through controlled, prompt-bounded service layers.
- Parent/guardian visibility into progress, consent history, and reports.
- Personalised study plans based on curriculum coverage and mastery gaps.
- Gamification through achievements, points, and badges.
- POPIA-compliant privacy, consent, audit, and data-rights workflows.

## Technical Identity & Architecture

- **Backend Modular Monolith**: FastAPI (`app.api_v2:app`) with typed service boundaries and strict repository isolation.
- **Background Worker Engine**: Redis 7 + ARQ (`app/core/arq_worker.py`) exclusively. Celery is fully decommissioned.
- **Frontend Application**: Next.js 16.3.3 (`@next/swc`, React 18/19, pnpm@9.14.4) under `app/frontend`, with PWA offline caching.
- **Persistence & Migrations**: PostgreSQL 16 with pgvector and consolidated Alembic schema (DEF-12 immutable audit triggers).
- **API Contracts**: Generated OpenAPI 3.1.0 specification at `docs/openapi.json` and 915-entry route topology at `docs/route_inventory.md`.
- **Knowledge Graph**: Core KG roadmap closed through KG-8; runtime authority switch executed.

## Longitudinal Educational Validation (LEV / PRD-4A)

Educational validity is fundamentally distinct from technical execution: a test passing without errors does not prove that an algorithm improves learning.

All pedagogical and mastery models are governed under the **PRD-4A Longitudinal Educational Validation (LEV)** framework:
- **Authoritative Register**: [`docs/roadmap/production_readiness/prd_4a_longitudinal_educational_validation_register.json`](roadmap/production_readiness/prd_4a_longitudinal_educational_validation_register.json) (222 tasks across 15 workstreams).
- **Task Implementation**: Managed under [`docs/roadmap/production_readiness/lev/`](roadmap/production_readiness/lev/).
- **Mathematical Confidence Bounds**: Mastery algorithms enforce `MAX_CONFIDENCE_THRESHOLD`. Unvalidated mastery states remain programmatically tagged as *tentative* or *inferred* until field-validated through longitudinal empirical research.
- **Verification Script**: `.venv/bin/python scripts/educational_validation/verify_lev_task_register.py --repo-root .` (asserts 222 tasks, valid evidence records, acyclic DAG).

## Test Suite & Coverage Contract

- **CI & Contract Floor**: **90%** minimum line coverage enforced in `coverage_contract.json` and `.github/workflows/pr-core.yml`.
- **Coverage Contract Enforcement**: Validated across all 4 required classes (`product`, `runtime`, `governance`, `advisory`) via `.venv/bin/python -m pytest tests/unit/coverage_suites/test_coverage_contract.py -q --no-cov`.
- **Historical Milestone Statement**: ~95.7% statement coverage was achieved and documented on the `feature/coverage-target-90` branch across 17 test batches (`docs/reports/coverage_target_90_completion_report.md`). Continuous CI actively guards the 90% floor fails-closed.

## Release Authority Boundaries (Fail-Closed)

Live learner access, external traffic, and payment processing are fail-closed and strictly unauthorized (`docs/roadmap/production_readiness/prd11_production_release_register.json`):

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

## Governance & Reconciled Registers

- Reconciled register rule: All roadmap items trace to the RR-### register in `docs/roadmap/reconciliation/outstanding_work_register.md`.
- Anti-theatre documentation standard: Review dates are updated strictly upon active content verification; stale documents are tracked in [`docs/documentation/stale_documentation_review_register.md`](documentation/stale_documentation_review_register.md).

