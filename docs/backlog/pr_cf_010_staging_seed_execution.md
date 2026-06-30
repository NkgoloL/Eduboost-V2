# PR-CF-010 Staging Seed Execution

## Status

Implemented locally. Staging seed execution, per-artifact evidence, staging payload persistence, rollback, admin API routes, frontend panel, and read verification are present.

## Scope

- Added `ContentStagingSeedExecutor`.
- Added `ContentStagingReadVerificationService`.
- Added `content_staging_seed_items` and `content_staging_artifacts`.
- Extended admin Content Factory routes for dry-run, seed, seed run history, seed items, verification, and rollback.
- Added the admin frontend staging seed panel.
- Kept production promotion fail-closed for PR-CF-010.

## Safety

Only approved, provenance-valid, validation-clean artifacts are staged. Pending review, rejected, quarantined, validation failed, and invalid-provenance artifacts are skipped with reasons.

Production promotion is not automated in this batch.

## Evidence

- `app/services/content_staging_seed_executor.py`
- `app/services/content_staging_read_verification.py`
- `app/services/content_seed_promotion.py`
- `app/api_v2_routers/content_factory.py`
- `app/frontend/src/components/admin/contentFactory/StagingSeedPanel.tsx`
- `alembic/versions/20260525_2300_content_factory_staging_seed_items.py`
- `docs/content_factory/staging_seed_execution.md`
- `docs/openapi.json`

## Local Verification

- `python3 -m py_compile ...` passed.
- Focused backend tests passed: `23 passed`.
- `python3 scripts/generate_openapi.py --check` passed.
- `make openapi-check` passed.
- `npm run type-check` passed in `app/frontend`.
- Schema contract script passed.
- Migration smoke was not run because `DATABASE_URL` was not set for a live test database.
