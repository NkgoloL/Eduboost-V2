# Concept of Operations (ConOps)

| Field | Value |
|---|---|
| Document ID | EDB-CONOPS-003 |
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

## Operational concept

EduBoost provides adaptive learning for South African primary learners. Guardians manage learner access and consent. Learners complete diagnostics, receive lessons, use tutor support, earn progress signals and follow study plans. Administrators govern curriculum content and operational evidence.

## Operational personas

| Persona | Primary goals | Typical entry points |
|---|---|---|
| Learner | Complete diagnostics, lessons, practice and tutor-supported learning. | Frontend learner dashboard, `/lessons`, `/diagnostics`, `/tutor`, `/practice`. |
| Guardian/parent | Manage consent, view progress, request exports/erasure and support learning. | Parent portal, `/parents`, `/popia`, `/consent`. |
| Admin/content operator | Review and promote curriculum artifacts. | `/admin/content-factory`, `/content-review`, `/admin/etl`. |
| Engineer/operator | Verify health, run migrations, operate queues, monitor alerts and collect release evidence. | `/health`, `/ready`, `/metrics`, Makefile, GitHub Actions. |
| Future educator reviewer | Validate curriculum alignment and content quality before publication. | Content Factory review assignment/decision flows. |

## Core scenarios

### Scenario 1: New learner onboarding
1. Guardian registers or logs in.
2. Guardian creates learner profile.
3. Guardian grants required POPIA consent.
4. Learner completes onboarding and diagnostic assessment.
5. System stores mastery state and recommends next learning actions.

### Scenario 2: Adaptive diagnostic session
1. Learner starts a diagnostic session.
2. Item selection uses scope, coverage, exposure and ability signals.
3. Responses are stored transactionally.
4. Mastery snapshots and knowledge gaps update.
5. Study plan and lesson recommendations are generated.

### Scenario 3: Content governance
1. Admin creates or imports content artifacts.
2. Validation, answer-key verification, provenance and review controls run.
3. Approved artifacts are staged and read-verified.
4. Production-promotion gates verify coverage and quality.
5. Learner content endpoints expose only approved production-ready material.

### Scenario 4: POPIA data subject request
1. Guardian or authorised actor submits export, erasure, correction or restriction request.
2. System checks authorisation, consent and learner relationship.
3. Request is persisted and audited.
4. Approved action is executed according to retention and legal constraints.

## Operating constraints

- New V2 work must keep the modular monolith boundary; do not reintroduce microservice sprawl or Celery/RabbitMQ for new workloads.
- Content and release claims must be scope-bounded and evidence-backed.
- Live deployment is not considered production-ready without current green gates.

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
