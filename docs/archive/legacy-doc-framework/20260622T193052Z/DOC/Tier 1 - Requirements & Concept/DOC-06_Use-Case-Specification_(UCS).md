---
title: Use-Case Specification (UCS)
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

# Use-Case Specification (UCS)

| Field | Value |
|---|---|
| Document ID | EDB-UCS-006 |
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

## Use-case map

| Use case | Primary actor | Goal | Primary APIs |
|---|---|---|---|
| UC-01 Register/login guardian | Guardian | Establish authenticated session. | `/auth/register`, `/auth/login`, `/auth/refresh`, `/auth/logout` |
| UC-02 Create learner profile | Guardian | Add a learner under guardian control. | `/learners/` |
| UC-03 Grant/revoke consent | Guardian | Manage consent for child data processing. | `/consent/*`, `/popia/consent/*` |
| UC-04 Complete diagnostic | Learner | Start a diagnostic session and answer adaptive items. | `/diagnostics/sessions`, `/diagnostics/sessions/{id}/respond` |
| UC-05 Generate lesson | Learner | Receive a CAPS-aligned lesson for need/topic. | `/lessons/generate`, `/lessons/generate/stream` |
| UC-06 Ask tutor | Learner | Ask lesson-scoped tutor questions. | `/tutor/sessions`, `/tutor/sessions/{id}/messages` |
| UC-07 Generate study plan | Learner/guardian | Receive personalised study plan. | `/study-plans/{learner_id}` |
| UC-08 View parent dashboard | Guardian | Review progress and privacy controls. | `/parents/dashboard`, `/parents/learners/{learner_id}/progress` |
| UC-09 Exercise data rights | Guardian/data subject | Export, erase, correct or restrict processing. | `/popia/exports`, `/popia/erasure`, `/popia/correction`, `/popia/restriction` |
| UC-10 Govern content artifacts | Admin/reviewer | Validate, review, seed and promote content. | `/admin/content-factory/*`, `/content-review/*` |
| UC-11 Calibrate item quality | Admin | Run/inspect IRT calibration and overrides. | `/admin/irt-quality/*` |
| UC-12 Monitor operations | Operator | Check health, readiness and metrics. | `/health`, `/ready`, `/metrics`, `/system/*` |

## Example detailed use case: diagnostic to lesson

| Field | Description |
|---|---|
| Preconditions | Guardian/learner authorised; learner has active consent; content scope exists. |
| Main flow | Start diagnostic session, serve next item, submit response, update mastery, generate lesson/study plan. |
| Alternate flow | If item bank coverage is insufficient, return a controlled error and block unsupported scope claims. |
| Postconditions | Diagnostic response, score snapshot, mastery updates and audit-relevant events are persisted. |
| Tests | Diagnostic session tests, mastery tests, route-contract tests and E2E learner journey. |

## Use cases intentionally removed

Stale `/ask`, `/feedback`, graph-search seeding and external ML retraining use cases do not match this repository and are excluded.

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
