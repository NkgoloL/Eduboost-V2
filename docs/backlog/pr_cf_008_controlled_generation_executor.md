# PR-CF-008 — Controlled generation executor integration

## Status

Implemented locally and verified with focused backend tests, OpenAPI checks, frontend type-check, and safety greps.

## Delivered

- Added generation provider abstraction with deterministic, disabled, and LLM placeholder modes.
- Added missing-content planner driven by readiness/coverage gaps.
- Added grounded source-context and prompt payload construction.
- Added diagnostic item and lesson validation services.
- Added controlled executor that writes artifacts, provenance, and validation results.
- Added admin planning/execution/report endpoints under `/api/v2/admin/content-factory`.
- Added minimal frontend generation controls.

## Safety

`CONTENT_FACTORY_GENERATION_ENABLED=false` remains the default. Execute endpoints fail closed while disabled. Generated artifacts are never auto-approved and never promoted to production.

## Verification

- `python3 -m py_compile app/services/content_generation/provider_factory.py app/services/content_generation_planner.py app/services/content_generation/source_context.py app/services/content_generation/prompt_payloads.py app/services/content_generation/diagnostic_generator.py app/services/content_generation/lesson_generator.py app/services/content_generation_executor.py app/api_v2_routers/content_factory.py`
- `python3 -m pytest tests/unit/test_content_generation_provider_factory.py tests/unit/test_content_generation_planner.py tests/unit/test_content_generation_source_context.py tests/unit/test_diagnostic_generator.py tests/unit/test_lesson_generator.py tests/unit/test_content_generation_executor.py tests/api/test_content_factory_generation_routes.py tests/unit/test_api_v2_router_contract.py -q --no-cov`
- `python3 scripts/generate_openapi.py --check`
- `make openapi-check`
- `cd app/frontend && npm run type-check`
- safety greps for public routes, FastMCP imports, and generation flags
