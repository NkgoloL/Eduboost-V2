# Stakeholder Requirements Definition (StRS)

| Field | Value |
|---|---|
| Document ID | EDB-STRS-004 |
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

## Stakeholder register

| ID | Stakeholder | Need | Priority |
|---|---|---|---|
| SH-01 | Learners | Age-appropriate CAPS-aligned lessons, diagnostics, practice, tutor help and motivation. | High |
| SH-02 | Parents/guardians | Safe consent management, progress visibility, reports and data-rights controls. | High |
| SH-03 | Educator/content reviewers | Curriculum alignment, review queues, provenance and answer-key verification. | High |
| SH-04 | Platform administrators | Content Factory, readiness, audit, operations and release evidence. | High |
| SH-05 | Engineers | Clear architecture, reproducible tests, migration integrity and clean CI. | High |
| SH-06 | Compliance/legal | POPIA, child data protection, audit trails, consent history and erasure governance. | High |
| SH-07 | Product/programme owner | A scoped launch path, claim discipline, risk register and beta readiness. | High |
| SH-08 | Security operators | Secrets management, token revocation, security headers, dependency scanning and incident response. | Medium |

## Stakeholder requirements

| Req ID | Stakeholder | Requirement | Validation |
|---|---|---|---|
| SR-01 | Learner | The UI must support diagnostic-to-lesson flow without exposing admin controls. | Frontend route tests and E2E. |
| SR-02 | Guardian | Guardian can see learner progress and initiate POPIA workflows. | Parent portal tests and route-contract tests. |
| SR-03 | Compliance | Consent and data-rights actions are persisted and auditable. | POPIA tests and audit repository evidence. |
| SR-04 | Content reviewer | Artifact review requires provenance and quality checks. | Content Factory service tests. |
| SR-05 | Operator | Health, readiness and metrics endpoints exist and are scrapeable under controlled conditions. | Runtime entrypoint and Compose validation. |
| SR-06 | Engineer | New code respects import-boundary contracts and source-of-truth docs. | Import-linter and current-state checks. |

## Stakeholder exclusions corrected from stale docs

The project does not target DBE policy analysts asking natural-language policy questions over a graph-search architecture. References to policy analysts, gateway policy controls, graph-database and external ML platform policy-retraining stakeholders have been removed from this aligned baseline.

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
