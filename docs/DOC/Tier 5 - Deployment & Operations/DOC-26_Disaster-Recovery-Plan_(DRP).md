# Disaster Recovery Plan (DRP)

| Field | Value |
|---|---|
| Document ID | EDB-DRP-026 |
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

## Recovery objectives

| Asset | Target RPO | Target RTO | Evidence needed |
|---|---:|---:|---|
| PostgreSQL primary data | Defined by deployment tier | Defined by deployment tier | Backup/restore drill. |
| Redis cache/queue | Best effort for cache; job recovery policy for ARQ | Defined by operations | Worker retry/dead-letter evidence. |
| Content artifacts | Repository-backed and object storage backed where used | Restore from repo/artifacts | Checksum and promotion history. |
| Frontend/API containers | Rebuild from commit | Minutes to hours | Container build logs and deploy rollback proof. |
| Audit/POPIA evidence | Highest priority retention | As defined legally | Immutable backup and access controls. |

## DR scenarios

| Scenario | Response |
|---|---|
| Database corruption | Stop writes, snapshot evidence, restore last known-good backup, run migrations, validate integrity. |
| Redis loss | Restart Redis, rehydrate cache naturally, inspect ARQ job loss/retry impact. |
| Bad deployment | Roll back to previous container/image/commit; verify health and route contracts. |
| Content artifact defect | Quarantine artifact, remove from production promotion, notify reviewers and regenerate evidence. |
| Secret compromise | Rotate affected secrets, revoke sessions/tokens, audit access and redeploy. |
| POPIA evidence loss | Escalate as compliance incident and follow incident response plan. |

## DR validation

A release cannot claim DR readiness until backup, restore and rollback evidence is attached for the target environment.

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
