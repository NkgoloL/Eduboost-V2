# 1. PR-002R replacement — backend runtime and API contract baseline

## 1.1 PR-002R governance

- [ ] `P0` Create recovery document `docs/pr/PR-002R_BACKEND_RUNTIME_API_CONTRACT.md`.
- [ ] `P0` Explain why PR-002R exists.
- [ ] `P0` List original PR-002 expected deliverables if known.
- [ ] `P0` Mark PR-002R as replacement implementation, not a placeholder.
- [ ] `P0` Add PR-002R to `PR_INTEGRATION_SUMMARY.md`.
- [ ] `P0` Add PR-002R to release evidence bundle.
- [ ] `P1` Create issue `PR-002R Backend Runtime/API Contract Baseline`.
- [ ] `P1` Link all PR-002R commits to the issue.
- [ ] `P1` Add acceptance checklist to the PR template for API contract changes.

## 1.2 Canonical runtime

- [verify] `P0` Confirm production runtime is `app.api_v2:app`. Evidence: `scripts/check_runtime_entrypoints.py`, `tests/test_entrypoints.py`.
- [verify] `P0` Update all docs to reference `app.api_v2:app`. Evidence: `docs/current_state.md`, `docs/pr/PR-002R_BACKEND_RUNTIME_API_CONTRACT.md`, `docs/route_inventory.md`.
- [ ] `P0` Update Dockerfile command to reference `app.api_v2:app`.
- [ ] `P0` Update docker-compose command to reference `app.api_v2:app` if command is explicit.
- [ ] `P0` Update CI smoke test to import `app.api_v2`.
- [ ] `P0` Update release checklist to require `app.api_v2:app`.
- [verify] `P0` Add runtime entrypoint tests. Evidence: `tests/test_entrypoints.py`, `tests/unit/test_check_runtime_entrypoints.py`.
- [verify] `P0` Add test importing `app.api_v2:app`. Evidence: `tests/test_entrypoints.py`.
- [ ] `P0` Add test importing `app.api.main:app`.
- [verify] `P0` Add test importing `app.legacy.api.main:app`, if legacy shim is retained. Evidence: `tests/test_entrypoints.py`.
- [verify] `P0` Ensure compatibility imports resolve to the V2 app or documented shim. Evidence: `tests/test_entrypoints.py`.
- [verify] `P0` Test that compatibility shim title/version matches V2 app. Evidence: `scripts/check_runtime_entrypoints.py`, `tests/unit/test_check_runtime_entrypoints.py`.
- [verify] `P0` Test that compatibility shim exposes the same `/health` behavior. Evidence: `tests/test_entrypoints.py`.
- [verify] `P0` Test that compatibility shim exposes the same `/ready` behavior. Evidence: `tests/test_entrypoints.py`.
- [ ] `P1` Add `scripts/check_runtime_entrypoints.py`.
- [x] `P1` Add `make runtime-check`. Evidence: `Makefile`,
  `scripts/check_runtime_entrypoints.py`.
- [ ] `P1` Add runtime check to CI.

## 1.3 Fix `app/api_v2.py` router registration

- [verify] `P0` Remove duplicate router import blocks from `app/api_v2.py`. Evidence: `app/api_v2.py`.
- [verify] `P0` Move `system.router` registration into the actual router-registration loop. Evidence: `app/api_v2.py`, `tests/unit/test_api_v2_router_contract.py`.
- [verify] `P0` Confirm `system.router` is registered under `/api/v2`. Evidence: `tests/unit/test_api_v2_router_contract.py`.
- [verify] `P0` Confirm `system.router` is registered under `/v2`. Evidence: `tests/unit/test_api_v2_router_contract.py`.
- [verify] `P0` Remove unreachable/dead router-registration code. Evidence: `app/api_v2.py`.
- [verify] `P0` Add regression test for system routes. Evidence: `tests/unit/test_api_v2_router_contract.py`.
- [verify] `P0` Add import smoke test:
  ```bash
  python -c "from app.api_v2 import app; print(app.title)"
  ```
- [verify] `P0` Add test ensuring all router modules import without side effects. Evidence: `tests/unit/test_api_v2_router_contract.py`.
- [verify] `P1` Add route inventory test that snapshots all registered routes. Evidence: `tests/unit/test_generate_route_inventory.py`.
- [verify] `P1` Commit route inventory artifact under `docs/route_inventory.md`. Evidence: `docs/route_inventory.md`.

## 1.4 Legacy route exclusion

- [ ] `P0` Define which routes are V2 production routes.
- [ ] `P0` Define which routes are legacy-only and forbidden in production.
- [verify] `P0` Add test proving legacy-only routes are not exposed by `app.api_v2:app`. Evidence: `tests/unit/test_api_v2_router_contract.py`, `tests/test_entrypoints.py`.
- [verify] `P0` Add test proving archived `app/legacy` code is not mounted. Evidence: `tests/test_entrypoints.py`.
- [verify] `P0` Add test proving V1 routers are not included accidentally. Evidence: `tests/unit/test_api_v2_router_contract.py`.
- [ ] `P1` Add CI job `legacy-route-guard`.
- [ ] `P1` Add `docs/legacy_compatibility.md`.
- [ ] `P2` Remove stale V1 docs or mark them archived.

## 1.5 API response envelope

- [verify] `P0` Create `app/domain/api_v2_models.py`. Evidence: `app/domain/api_v2_models.py`, `tests/unit/test_api_v2_envelope.py`.
- [verify] `P0` Define `ApiMeta` model. Evidence: `app/domain/api_v2_models.py`.
- [verify] `P0` Define `ApiError` model. Evidence: `app/domain/api_v2_models.py`.
- [verify] `P0` Define `ApiEnvelope[T]` model. Evidence: `app/domain/api_v2_models.py`.
- [verify] `P0` Define `PaginationMeta` model. Evidence: `app/domain/api_v2_models.py`.
- [verify] `P0` Define success envelope helper `ok`. Evidence: `app/domain/api_v2_models.py`, `tests/unit/test_api_v2_envelope.py`.
- [verify] `P0` Define error envelope helper `fail`. Evidence: `app/domain/api_v2_models.py`, `tests/unit/test_api_v2_envelope.py`.
- [verify] `P0` Define pagination envelope helper `paginated`. Evidence: `app/domain/api_v2_models.py`, `tests/unit/test_api_v2_envelope.py`.
- [verify] `P0` Include `request_id` in every envelope. Evidence: `app/domain/api_v2_models.py`, `tests/unit/test_api_v2_envelope.py`.
- [verify] `P0` Include `api_version` in every envelope. Evidence: `app/domain/api_v2_models.py`, `tests/unit/test_api_v2_envelope.py`.
- [verify] `P0` Ensure `error` is `null` on success. Evidence: `tests/unit/test_api_v2_envelope.py`.
- [verify] `P0` Ensure `data` is `null` on error. Evidence: `tests/unit/test_api_v2_envelope.py`, `tests/unit/test_exception_envelopes.py`.
- [verify] `P0` Add unit tests for `ok`. Evidence: `tests/unit/test_api_v2_envelope.py`.
- [verify] `P0` Add unit tests for `fail`. Evidence: `tests/unit/test_api_v2_envelope.py`.
- [verify] `P0` Add unit tests for `paginated`. Evidence: `tests/unit/test_api_v2_envelope.py`.
- [ ] `P0` Apply envelope to auth router.
- [ ] `P0` Apply envelope to learners router.
- [ ] `P0` Apply envelope to lessons router.
- [ ] `P0` Apply envelope to study plans router.
- [ ] `P0` Apply envelope to diagnostics router.
- [ ] `P0` Apply envelope to gamification router.
- [ ] `P0` Apply envelope to onboarding router.
- [ ] `P0` Apply envelope to parents router.
- [ ] `P0` Apply envelope to billing router.
- [ ] `P0` Apply envelope to consent router.
- [ ] `P0` Apply envelope to consent renewal router.
- [ ] `P0` Apply envelope to POPIA router.
- [ ] `P0` Apply envelope to jobs router.
- [ ] `P0` Apply envelope to system router.
- [ ] `P1` Add lint/test rule preventing raw dict responses from production routers unless explicitly exempted.
- [verify] `P1` Add docs examples for success envelope. Evidence: `docs/api_envelope_contract.md`.
- [verify] `P1` Add docs examples for error envelope. Evidence: `docs/api_envelope_contract.md`, `docs/error_contract.md`.
- [verify] `P1` Add docs examples for pagination envelope. Evidence: `docs/api_envelope_contract.md`.

## 1.6 API error contract

- [verify] `P0` Update `app/core/exceptions.py` to emit canonical error envelope. Evidence: `app/core/exceptions.py`, `tests/unit/test_exception_envelopes.py`.
- [verify] `P0` Include machine-readable error code. Evidence: `app/core/exceptions.py`, `docs/error_contract.md`.
- [verify] `P0` Include human-readable message. Evidence: `app/core/exceptions.py`, `tests/unit/test_exception_envelopes.py`.
- [verify] `P0` Include field errors when validation fails. Evidence: `app/core/exceptions.py`, `tests/unit/test_exception_envelopes.py`.
- [verify] `P0` Include remediation hint when useful. Evidence: `app/core/exceptions.py`, `docs/api_envelope_contract.md`.
- [verify] `P0` Include request ID. Evidence: `app/core/exceptions.py`, `tests/unit/test_exception_envelopes.py`.
- [verify] `P0` Prevent sensitive exception details from leaking. Evidence: `app/core/exceptions.py`, `tests/unit/test_exception_envelopes.py`.
- [verify] `P0` Implement error code `validation_error`. Evidence: `docs/error_contract.md`, `tests/unit/test_exception_envelopes.py`.
- [verify] `P0` Implement error code `unauthorized`. Evidence: `docs/error_contract.md`, `app/core/exceptions.py`.
- [verify] `P0` Implement error code `forbidden`. Evidence: `docs/error_contract.md`, `tests/unit/test_exception_envelopes.py`.
- [verify] `P0` Implement error code `not_found`. Evidence: `docs/error_contract.md`, `tests/unit/test_exception_envelopes.py`.
- [verify] `P0` Implement error code `conflict`. Evidence: `docs/error_contract.md`, `tests/unit/test_exception_envelopes.py`.
- [verify] `P0` Implement error code `rate_limited`. Evidence: `docs/error_contract.md`, `app/core/exceptions.py`.
- [verify] `P0` Implement error code `consent_required`. Evidence: `docs/error_contract.md`, `tests/unit/test_exception_envelopes.py`.
- [verify] `P0` Implement error code `consent_expired`. Evidence: `docs/error_contract.md`, `app/core/exceptions.py`.
- [verify] `P0` Implement error code `dependency_unavailable`. Evidence: `docs/error_contract.md`, `app/core/exceptions.py`.
- [verify] `P0` Implement error code `internal_error`. Evidence: `docs/error_contract.md`, `tests/unit/test_exception_envelopes.py`.
- [verify] `P0` Add tests for all error codes. Evidence: `tests/unit/test_api_envelope_error_contract.py`; verification gap: executable endpoint tests still cover a representative subset.
- [verify] `P0` Add tests for validation errors. Evidence: `tests/unit/test_exception_envelopes.py`.
- [verify] `P0` Add tests for auth errors. Evidence: `app/core/exceptions.py`, `docs/error_contract.md`; verification gap: endpoint-level auth error tests remain router-specific.
- [verify] `P0` Add tests for authorization errors. Evidence: `tests/unit/test_exception_envelopes.py`.
- [verify] `P0` Add tests for consent errors. Evidence: `tests/unit/test_exception_envelopes.py`.
- [verify] `P0` Add tests for rate-limit errors. Evidence: `app/core/exceptions.py`; verification gap: executable rate-limit handler test remains open.
- [verify] `P0` Add tests proving internal exceptions hide details in production. Evidence: `tests/unit/test_exception_envelopes.py`.
- [verify] `P1` Add `docs/error_contract.md`. Evidence: `docs/error_contract.md`.

## 1.7 OpenAPI generation and contract

- [ ] `P0` Add `scripts/generate_openapi.py`.
- [ ] `P0` Ensure script imports `app.api_v2:app`.
- [ ] `P0` Ensure script writes `docs/openapi.json`.
- [ ] `P0` Generate `docs/openapi.json`.
- [ ] `P0` Add `make openapi`.
- [ ] `P0` Add `make openapi-check`.
- [ ] `P0` Add CI job `openapi-contract`.
- [ ] `P0` CI must fail if generated schema differs from committed schema.
- [ ] `P0` Add OpenAPI tags for ops.
- [ ] `P0` Add OpenAPI tags for auth.
- [ ] `P0` Add OpenAPI tags for learners.
- [ ] `P0` Add OpenAPI tags for consent.
- [ ] `P0` Add OpenAPI tags for diagnostics.
- [ ] `P0` Add OpenAPI tags for lessons.
- [ ] `P0` Add OpenAPI tags for study plans.
- [ ] `P0` Add OpenAPI tags for gamification.
- [ ] `P0` Add OpenAPI tags for parents.
- [ ] `P0` Add OpenAPI tags for POPIA.
- [ ] `P0` Add OpenAPI tags for billing.
- [ ] `P0` Add OpenAPI tags for jobs.
- [ ] `P0` Add OpenAPI tags for system.
- [ ] `P0` Add summaries for all production endpoints.
- [ ] `P0` Add descriptions for all production endpoints.
- [ ] `P0` Add examples for major request models.
- [ ] `P0` Add examples for major response models.
- [ ] `P1` Add breaking-change detection for OpenAPI diffs.
- [ ] `P1` Add PR label requirement for breaking API changes.
- [ ] `P1` Add `docs/api_v2.md`.
- [ ] `P1` Add `docs/api_versioning_policy.md`.
- [ ] `P2` Publish generated API docs through MkDocs/Sphinx.

## 1.8 PR-002R acceptance evidence

- [ ] `P0` PR-002R tests pass locally.
- [ ] `P0` PR-002R tests pass in CI.
- [ ] `P0` Runtime import test is included in release evidence bundle.
- [ ] `P0` OpenAPI schema hash is included in release evidence bundle.
- [ ] `P0` Route inventory is included in release evidence bundle.
- [ ] `P0` Error-envelope test output is included in release evidence bundle.
- [ ] `P0` Add PR-002R completion note to `docs/project_status.md`.
- [ ] `P0` Add PR-002R completion note to `PR_INTEGRATION_SUMMARY.md`.

---

