# Backend

The active backend is the V2 FastAPI modular monolith rooted at `app/api_v2.py`.

## Runtime map

- Routers: `app/api_v2_routers/`
- Application services: `app/services/`
- Persistence: `app/repositories/`
- Shared runtime kernel: `app/core/`
- Domain contracts: `app/domain/`
- Bounded modules: `app/modules/`

## Current implementation notes

- New backend work should use V2 routers and service/repository boundaries.
- Legacy code under `app/legacy/` is compatibility-only and should not grow.
- Deterministic/mock providers are allowed for tests and local dry-runs only.
- Production-sensitive paths must fail closed when required secrets or providers are missing.

## Verification

- Fast unit gate: `make test-fast`
- Integration gate: `make test-integration`
- Coverage gate: `make test-coverage`
- Runtime entrypoint check: `make runtime-check`

Back to the main index: [docs/README.md](../README.md). Root overview: [README.md](../../README.md).
