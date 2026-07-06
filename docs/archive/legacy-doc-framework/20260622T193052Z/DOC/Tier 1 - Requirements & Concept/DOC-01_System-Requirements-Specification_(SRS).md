---
title: System Requirements Specification (SRS)
status: archived-record
owner: documentation-governance
reviewers: [documentation-governance, evidence-custodian, release-management]
audience: evidence-reviewer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-06
review_interval_days: 180
evidence_command: make docs-housekeeping-stage7-check
code_anchors: [docs/archive, docs/documentation/stage_7_release_archive_backlog_codemaps_governance.md]
---

# System Requirements Specification (SRS)

| Field | Value |
|---|---|
| Document ID | EDB-SRS-001 |
| Product | EduBoost SA / EduBoost V2 |
| Version | 2.0 aligned baseline |
| Generated | 2026-06-22 |
| Status | Aligned baseline draft |
| Classification | Internal - controlled |
| Replacement note | Replaces stale DBE policy-advisory content previously found in `docs/DOC` |

## Authoritative project baseline

This document is aligned to the EduBoost V2 repository supplied on 2026-06-22. It replaces the prior `docs/DOC` material that described a different DBE policy-advisory system.

| Area | Current baseline |
|---|---|
| Product | EduBoost SA, a CAPS-aligned adaptive learning platform for South African primary learners |
| Active backend | `app/api_v2.py` FastAPI modular monolith, mounted under `/api/v2` and `/v2` |
| Frontend | `app/frontend`, package `eduboost-sa-frontend`, Next.js `16.2.7`, React `18.3.1`, TypeScript `5.4.5` |
| Package manager | pnpm `9.14.4` for frontend |
| Python runtime | Python `3.12.3` |
| Persistence | PostgreSQL via SQLAlchemy/Alembic; 44 Alembic revision files in the supplied archive |
| Queue/cache | Redis and ARQ worker path (`app.modules.jobs.WorkerSettings`); V2 should not introduce Celery/RabbitMQ for new work |
| Launch curriculum scope | `grade4_mathematics_en`: CAPS refs 4.M.1.1, 4.M.1.2, 4.M.1.3 |
| Content targets | 40 approved diagnostic items, 8 approved lessons, 1 assessment blueprint, and 1 study-plan template per launch CAPS ref |
| API surface | 205 route handlers discovered by static router scan, plus health/readiness/metrics root routes |
| Tests | 767 backend test files and approximately 44 frontend test/spec files in the archive |
| Workflows | 44 GitHub Actions workflow files |

### Claim discipline

Unless fresh CI, staging, backup/restore, security, POPIA and release evidence is attached, these documents describe the current implementation and target operating model. They must not be used to claim that the system is production-ready.

## Purpose

This SRS defines the required behaviour for EduBoost V2. The system is not a policy-query graph-search platform. It is a modular learning platform for South African learners, guardians, administrators and future educator reviewers.

## Functional requirements

| ID | Requirement | Priority | Implementation anchor |
|---|---|---|---|
| FR-01 | Register, authenticate, refresh, revoke, and inspect sessions for guardians and authorised users. | Must | `app/api_v2_routers/auth.py`, `app/services/auth_application_service.py` |
| FR-02 | Create and manage learner profiles with guardian ownership and object-level access control. | Must | `app/api_v2_routers/learners.py`, `app/repositories/` |
| FR-03 | Run diagnostic assessment sessions and persist responses, scores, mastery updates, and item exposure controls. | Must | `app/api_v2_routers/diagnostics.py`, `app/services/diagnostic*.py` |
| FR-04 | Support IRT calibration and item-quality governance for adaptive diagnostics. | Must | `app/api_v2_routers/irt_quality.py`, `app/domain/irt_quality_schemas.py` |
| FR-05 | Generate, retrieve, stream, complete, and sync CAPS-aligned lessons. | Must | `app/api_v2_routers/lessons.py`, `app/services/lesson_service_v2.py` |
| FR-06 | Provide lesson-scoped AI tutor sessions with safety constraints. | Should | `app/api_v2_routers/tutor.py`, `app/services/learner_tutor.py`, `app/services/tutor_safety.py` |
| FR-07 | Generate personalised study plans from mastery gaps and curriculum coverage. | Must | `app/api_v2_routers/study_plans.py`, `app/services/study_plan_service_v2.py` |
| FR-08 | Track gamification XP, badges, leaderboard profile and achievement progress. | Should | `app/api_v2_routers/gamification.py`, `app/services/gamification_service_v2.py` |
| FR-09 | Provide a parent/guardian dashboard with learner progress, access bundle exports, and erasure initiation. | Must | `app/api_v2_routers/parents.py` |
| FR-10 | Manage POPIA consent, data export, erasure, correction, restriction, renewal and audit evidence. | Must | `app/api_v2_routers/popia.py`, `app/api_v2_routers/consent.py` |
| FR-11 | Operate admin-only Content Factory, review, seed, staging and production-promotion controls. | Must | `app/api_v2_routers/content_factory.py`, `app/models/content_factory.py` |
| FR-12 | Expose health, readiness, metrics and operational status endpoints. | Must | `app/api_v2.py`, `app/api_v2_routers/system.py` |

## Non-functional requirements

| ID | Requirement | Baseline control |
|---|---|---|
| NFR-01 | Security by default for protected routes. | JWT tokens, role dependencies, object-level authorisation and security headers middleware. |
| NFR-02 | POPIA-aligned privacy controls. | Consent lifecycle, data-subject rights routes, audit events, retention/erasure workflow. |
| NFR-03 | Reproducible database state. | Alembic migrations and schema integrity scripts. |
| NFR-04 | Observable operations. | `/health`, `/ready`, `/metrics`, Prometheus, Alertmanager and structured logging. |
| NFR-05 | Deterministic curriculum evidence. | `data/content_factory/scopes.json`, `coverage_targets.json`, generated item/lesson artifacts and release evidence. |
| NFR-06 | Frontend build quality. | pnpm, TypeScript, Vitest, ESLint and environment validation. |
| NFR-07 | AI safety and cost control. | LLM provider timeout/retry settings, tutor safety filters, AI budget counters and reservation APIs. |
| NFR-08 | Claims backed by evidence. | Current-state docs, roadmap gates, release evidence, CI and verification scripts. |

## Launch-scope requirements

| ID | Requirement | Acceptance signal |
|---|---|---|
| LR-01 | Treat Grade 4 Mathematics English as the initial launch scope. | `data/content_factory/scopes.json` contains `grade4_mathematics_en`. |
| LR-02 | Maintain coverage for CAPS refs 4.M.1.1, 4.M.1.2, 4.M.1.3. | `coverage_targets.json` contains all three refs. |
| LR-03 | Keep launch evidence bounded. | Documents must state that green launch evidence covers the slice only, not all grades/subjects. |

## Out of scope for this project baseline

- DBE policy-advisory workflows, `/ask` policy answers, graph-database, external ML retraining pipelines and gateway-first identity are not part of the supplied EduBoost V2 runtime.
- Full Grade R-7 CAPS coverage is a roadmap target, not a completed launch claim.
- Production-readiness claims require fresh release evidence.

## Source-of-truth references

- Runtime entrypoint: `app/api_v2.py`
- Backend routers: `app/api_v2_routers/` and `app/modules/practice/router.py`
- Domain contracts: `app/domain/`
- Persistence models: `app/models/`, `app/repositories/`, `alembic/versions/`
- Content Factory: `app/services/content_factory*.py`, `app/api_v2_routers/content_factory.py`, `data/content_factory/`
- Diagnostics and IRT: `app/services/diagnostic*.py`, `app/api_v2_routers/diagnostics.py`, `app/api_v2_routers/irt_quality.py`
- Parent portal and POPIA: `app/api_v2_routers/parents.py`, `app/api_v2_routers/popia.py`, `app/services/popia_service.py`
- Frontend: `app/frontend/package.json`, `app/frontend/src/`
- Operations: `docker-compose.yml`, `docker-compose.prod.yml`, `.github/workflows/`, `docs/operations/`

## Standard verification gate

Run the closest applicable subset before accepting a document-controlled change:

```bash
python3 -m compileall -q app scripts
python3 -m ruff check app tests scripts --select E9,F63,F7,F82,F821
python3 scripts/verify_migration_graph.py
python3 scripts/validate_schema_integrity.py
python3 scripts/check_runtime_entrypoints.py
python3 scripts/generate_openapi.py --check
python3 scripts/generate_route_inventory.py --check
make test-fast
cd app/frontend && pnpm run env-check && pnpm run lint && pnpm run type-check && pnpm run test
```

For release claims add integration tests, Docker Compose validation, staging smoke tests, Playwright E2E, backup/restore proof, rollback proof, and security/POPIA evidence.
