---
title: Interface Control Document (ICD)
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

# Interface Control Document (ICD)

| Field | Value |
|---|---|
| Document ID | EDB-ICD-009 |
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

## Interface inventory

| Interface | Producer | Consumer | Contract |
|---|---|---|---|
| Web UI to API | Next.js frontend | FastAPI backend | HTTP JSON over `/api/v2`; bearer/session auth where required. |
| Backend to PostgreSQL | Services/repositories | PostgreSQL | SQLAlchemy models and Alembic migrations. |
| Backend to Redis | Auth/jobs/cache | Redis | Token revocation, cache and ARQ queue. |
| Backend to LLM providers | AI services | Google/Groq/Anthropic/local inference where configured | Timeout, retry, quota and safety wrappers. |
| Content registry to services | `data/content_factory/*.json` | Content Factory services | Scope and coverage target JSON. |
| Observability | App/runtime | Prometheus/Grafana/Alertmanager | `/metrics`, health endpoints, logs and alerts. |
| CI/CD | GitHub Actions | repo checks | Workflow YAML, Make targets and scripts. |

## API route summary from static scan

| Area | Route count | Representative paths |
|---|---:|---|
|  | 1 | `/` |
| admin | 103 | `/admin/etl/status`, `/admin/etl/documents`, `/admin/etl/documents/{document_id}` |
| assessments | 2 | `/assessments`, `/assessments/{assessment_id}/attempt` |
| audit | 2 | `/audit`, `/audit/feed` |
| auth | 19 | `/auth/me`, `/auth/register`, `/auth/login` |
| billing | 3 | `/billing/checkout`, `/billing/create-checkout-session`, `/billing/webhook` |
| consent | 3 | `/consent/grant`, `/consent/revoke`, `/consent/status/{learner_id}` |
| content-review | 10 | `/content-review/artifacts/{artifact_id}/assignments`, `/content-review/assignments/{assignment_id}/accept`, `/content-review/assignments/{assignment_id}/reassign` |
| diagnostics | 9 | `/diagnostics/items/{learner_id}`, `/diagnostics/submit`, `/diagnostics/coverage` |
| gamification | 3 | `/gamification/profile/{learner_id}`, `/gamification/award-xp`, `/gamification/leaderboard` |
| health | 1 | `/health` |
| jobs | 1 | `/jobs/{job_id}` |
| learner | 5 | `/learner/content/scopes/{scope_id}/summary`, `/learner/content/scopes/{scope_id}/diagnostic-items`, `/learner/content/scopes/{scope_id}/lessons` |
| learners | 6 | `/learners/`, `/learners/{learner_id}`, `/learners/{learner_id}/mastery` |
| lessons | 6 | `/lessons/generate`, `/lessons/`, `/lessons/generate/stream` |
| onboarding | 3 | `/onboarding/questions`, `/onboarding/submit`, `/onboarding/archetype` |
| parents | 5 | `/parents/dashboard`, `/parents/{guardian_id}/dashboard`, `/parents/{guardian_id}/export` |
| popia | 9 | `/popia/consent/grant`, `/popia/consent/deny`, `/popia/consent/withdraw` |
| practice | 3 | `/practice/sessions`, `/practice/sessions/{session_id}/next-item`, `/practice/sessions/{session_id}/respond` |
| study-plans | 2 | `/study-plans/{learner_id}`, `/study-plans/generate/{learner_id}` |
| system | 4 | `/system/health`, `/system/pillars`, `/system/schema-status` |
| tutor | 5 | `/tutor/sessions`, `/tutor/sessions/{session_id}`, `/tutor/sessions/{session_id}/messages` |

## Canonical POPIA data-rights routes

| Action | Backend route |
|---|---|
| Consent grant/deny/withdraw/renew | `/popia/consent/grant`, `/popia/consent/deny`, `/popia/consent/withdraw`, `/popia/consent/renew` |
| Export request | `/popia/exports` |
| Erasure request | `/popia/erasure` |
| Erasure cancellation | `/popia/erasure/{learner_id}/cancel` |
| Correction request | `/popia/correction` |
| Restriction request | `/popia/restriction` |

## Removed/stale interfaces

API gateway `/ask`, `/feedback`, graph-database, external ML pipeline and DBE policy-query interfaces are not supported by the supplied codebase.

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
