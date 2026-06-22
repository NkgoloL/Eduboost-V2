# Test Summary Report (TSR)

| Field | Value |
|---|---|
| Document ID | EDB-TSR-020 |
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

## Summary template

| Gate | Result | Evidence |
|---|---|---|
| Runtime entrypoint | Pending fresh run | Attach command output. |
| OpenAPI drift | Pending fresh run | Attach `generate_openapi.py --check`. |
| Route inventory | Pending fresh run | Attach route inventory check. |
| Migration graph | Pending fresh run | Attach script output. |
| Schema integrity | Pending fresh run | Attach script output. |
| Backend unit | Pending fresh run | Attach `make test-fast`. |
| Frontend lint | Pending fresh run | Attach pnpm output. |
| Frontend type-check | Pending fresh run | Attach pnpm output. |
| Frontend unit | Pending fresh run | Attach Vitest output. |
| E2E browser | Pending release gate | Attach Playwright report. |
| POPIA/privacy | Pending release gate | Attach data-rights evidence. |

## Interpretation rules

- A red required gate blocks release-readiness claims.
- A skipped gate must have a named owner, reason and expiry date.
- Historical green evidence cannot substitute for fresh evidence after route, schema, security, POPIA or content changes.

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
