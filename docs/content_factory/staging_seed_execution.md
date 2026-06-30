# Content Factory Staging Seed Execution

PR-CF-010 adds a staging-only seed path for approved Content Factory artifacts. It records seed run evidence, per-artifact item evidence, staging payload rows, rollback metadata, and read verification results.

## Safety Boundary

Approved artifacts may enter staging when all artifact-level checks pass:

- artifact status is `approved`
- provenance validation passes
- the latest validation report is present and clean
- artifact status is not `pending_review`, `rejected`, `quarantined`, or `validation_failed`

Production promotion remains blocked in this PR. The production gate still evaluates coverage and staging verification, then raises a fail-closed error until PR-CF-011 implements the release gate.

## Persistence

Seed evidence is persisted in:

- `content_seed_runs` for run-level status and summary
- `content_staging_seed_items` for per-artifact seed, skip, failure, and rollback evidence
- `content_staging_artifacts` for staging payload records

`content_staging_seed_items.rollback_payload_json` preserves the staging target metadata needed to roll back a seed run. Rollback marks seed items as `rolled_back` and excludes rolled-back staging rows from active read verification.

## Admin API

All routes are admin-only under `/api/v2/admin/content-factory`:

- `POST /scopes/{scope_id}/dry-run-seed`
- `POST /scopes/{scope_id}/seed-staging`
- `GET /seed-runs`
- `GET /seed-runs/{seed_run_id}`
- `GET /seed-runs/{seed_run_id}/items`
- `POST /seed-runs/{seed_run_id}/verify`
- `POST /seed-runs/{seed_run_id}/rollback`
- `GET /scopes/{scope_id}/staging-read-verification`

No learner-facing seed route is added.

## Verification

Focused verification for this batch:

```bash
python3 -m py_compile \
  app/services/content_staging_seed_executor.py \
  app/services/content_staging_read_verification.py \
  app/services/content_seed_promotion.py \
  app/api_v2_routers/content_factory.py

python3 -m pytest \
  tests/unit/test_content_staging_seed_executor.py \
  tests/unit/test_content_staging_read_verification.py \
  tests/unit/test_content_seed_promotion.py \
  tests/api/test_content_factory_staging_seed_routes.py \
  tests/unit/test_api_v2_router_contract.py \
  -q --no-cov

python3 scripts/generate_openapi.py --check
make openapi-check

cd app/frontend
npm run type-check
```

Migration smoke requires a live content-factory test database and `DATABASE_URL`.
