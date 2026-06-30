# PR-CF-007 — All-scope staging seed verification and readiness reports

## Status

Implemented locally and verified with focused backend tests, OpenAPI drift checks, frontend type-check, and disposable Postgres migration smoke.

## Delivered

- Added `ContentStagingReadinessService` for configured all-scope and per-scope readiness reports.
- Added status and blocker vocabulary for staging readiness.
- Persisted aggregate verification runs and per-scope results.
- Added admin API routes for all-scope verification, run history, run details, scope verification, and scope readiness.
- Refined seed staging semantics so partial staging can proceed when approved content exists, while production promotion remains fail-closed.
- Added minimal admin staging readiness panel.
- Updated OpenAPI contract and Content Factory schema contract.

## Verification

- `python3 -m py_compile app/services/content_staging_readiness.py app/services/content_seed_promotion.py app/api_v2_routers/content_factory.py`
- `python3 -m pytest tests/unit/test_content_staging_readiness.py tests/unit/test_content_seed_promotion.py tests/api/test_content_factory_staging_verification_routes.py tests/unit/test_api_v2_router_contract.py -q --no-cov`
- `python3 scripts/generate_openapi.py --check`
- `make openapi-check`
- `cd app/frontend && npm run type-check`
- Disposable Postgres `check_content_factory_migrations.sh` and `make migration-smoke`

## Remaining Gates

This is not a production promotion or learner-visible release. Human review, staging evidence, and green release readiness remain required before promotion.
