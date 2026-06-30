# PR-CF-004 Registry-Backed Coverage

Status: implemented and locally tested on branch `pr-cf-004-registry-backed-coverage`; CI and staging evidence are not yet captured.

## Scope

This batch adds read-only, registry-backed coverage calculations for the Content Factory launch scope. It does not add generation, review mutation, seeding, staging, promotion, worker orchestration, or dashboard live wiring.

## Implemented

- Added `ContentCoverageService` to calculate scope-level and CAPS-ref-level coverage from `data/content_factory/coverage_targets.json`.
- Counted live-backed `diagnostic_items` coverage through the item bank repository contract.
- Counted live-backed `lessons` coverage through the lesson repository contract.
- Kept future layers visible as configured zero-count placeholders when explicitly requested.
- Replaced diagnostic item coverage readiness with registry-backed target lookup while keeping the default `grade4_mathematics_en` launch wrapper.
- Replaced lesson coverage thresholding with registry-backed lesson targets.
- Added read-only admin endpoints:
  - `GET /api/v2/admin/content-factory/scopes/{scope_id}/coverage`
  - `GET /api/v2/admin/content-factory/scopes/{scope_id}/coverage/{caps_ref}`

## Safety

- Admin API remains read-only for coverage.
- Unknown scopes and out-of-scope CAPS refs fail closed with `404`.
- No learner-facing routes were added or changed for generated content exposure.
- No generation, seed, review, or promotion endpoint was added.

## Local Verification

```bash
python3 -m py_compile \
  app/services/content_coverage_service.py \
  app/services/content_scope_registry.py \
  app/api_v2_routers/content_factory.py \
  app/modules/diagnostics/item_bank_service.py \
  app/modules/lessons/lesson_coverage_router.py
```

```bash
python3 -m pytest \
  tests/unit/test_content_scope_registry.py \
  tests/unit/test_content_coverage_service.py \
  tests/unit/test_content_factory_services.py \
  tests/api/test_content_factory_admin_routes.py \
  tests/api/test_content_factory_scope_routes.py \
  tests/api/test_content_factory_coverage_routes.py \
  tests/unit/test_api_v2_router_contract.py \
  tests/unit/modules/diagnostics/test_item_bank_service.py \
  -q --no-cov
```

Result: `55 passed`.

```bash
python3 scripts/generate_openapi.py && make openapi-check
cd app/frontend && npm run type-check
```

Both passed locally.

## Remaining Proof

- CI run for the PR branch.
- Runtime migration evidence on disposable PostgreSQL.
- Staging smoke evidence.
- Educator/content review evidence before generated content is treated as externally approved.
