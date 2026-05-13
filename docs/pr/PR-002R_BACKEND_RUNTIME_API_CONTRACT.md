# PR-002R Backend Runtime and API Contract Evidence

## Purpose

PR-002R is the replacement implementation for the backend runtime and API contract baseline.

It exists because the production-readiness backlog requires a verified, canonical V2 runtime before later work on security, POPIA enforcement, deployment, frontend integration, and release evidence can be trusted.

## Scope

PR-002R establishes:

- Canonical runtime: `app.api_v2:app`.
- Canonical branch: `master`.
- Runtime import tests.
- V2 router registration under `/api/v2` and `/v2`.
- Legacy route exclusion tests.
- Canonical API envelope models and helpers.
- Canonical error envelope handling.
- Deterministic OpenAPI generation.
- Committed OpenAPI schema at `docs/openapi.json`.
- OpenAPI drift verification through `make openapi-check`.
- Deterministic route inventory at `docs/route_inventory.md`.
- CI branch policy using `master` and `release/**`.

## Repository Freshness Marker

This PR sequence was started from the repository state identified by:

```text
Merge pull request #52 from NkgoloL/chore/slow-query-logging
```

Freshness must not be judged by raw commit count. Use head SHA, merge marker, branch name, release tag where applicable, and local/CI verification evidence.

## Runtime Contract

The only production runtime for new work is:

```text
app.api_v2:app
```

The archived compatibility shim must not be treated as a separate production runtime.

## Implemented Evidence

| Area | Evidence |
| --- | --- |
| Runtime import | `tests/test_entrypoints.py` |
| Runtime entrypoint check | `scripts/check_runtime_entrypoints.py`, `tests/unit/test_check_runtime_entrypoints.py` |
| Router registration | `app/api_v2.py`, `tests/test_entrypoints.py` |
| Legacy route exclusion | `tests/test_legacy_route_exclusion.py` |
| API envelope helpers | `app/domain/api_v2_models.py`, `tests/unit/test_api_v2_envelope.py` |
| Error envelope handlers | `app/core/exceptions.py`, `tests/unit/test_exception_envelopes.py` |
| OpenAPI generator | `scripts/generate_openapi.py`, `tests/unit/test_generate_openapi.py` |
| OpenAPI drift guard | `Makefile`, `.github/workflows/openapi-drift.yml`, `tests/unit/test_openapi_ci_contract.py` |
| OpenAPI schema artifact | `docs/openapi.json` |
| Route inventory artifact | `docs/route_inventory.md`, `scripts/generate_route_inventory.py`, `tests/unit/test_generate_route_inventory.py` |
| PR acceptance checklist | `.github/pull_request_template.md`, `tests/unit/test_pr002r_governance_contract.py` |
| Pytest import-path policy | `tests/conftest.py`, `tests/unit/test_pytest_import_path.py`, `docs/testing/pytest_import_path.md` |
| Release evidence index | `docs/release/PR-002R_EVIDENCE.md` |

## Verification Commands

```bash
python3 -c "from app.api_v2 import app; print(app.title)"
python3 scripts/generate_openapi.py
make openapi-check
make route-inventory-check
pytest -c pytest.ini \
  tests/test_entrypoints.py \
  tests/test_legacy_route_exclusion.py \
  tests/unit/test_api_v2_envelope.py \
  tests/unit/test_exception_envelopes.py \
  tests/unit/test_generate_openapi.py \
  tests/unit/test_openapi_ci_contract.py \
  tests/unit/test_pr002r_docs_contract.py \
  -q --no-cov
```

## Acceptance Criteria

PR-002R is complete when all verification commands pass locally, CI passes on the PR, `docs/openapi.json` is committed and current, the OpenAPI drift job passes, and this evidence document is committed.

## Explicit Non-Scope

PR-002R does not complete object-level authorization, POPIA workflows, audit-chain integrity, backup/restore, AI/CAPS validation, frontend production journeys, staging acceptance, or release approval.

---

## Replacement Baseline Addendum

# PR-002R — Backend Runtime and API Contract Baseline

**Status:** Replacement implementation (not a placeholder)
**Replaces:** PR-002 (original, not merged / lost)
**Priority:** P0
**Owner:** Backend team

---

## Why PR-002R Exists

PR-002 was the original pull request intended to establish the V2 FastAPI
runtime (`app.api_v2:app`) as the canonical production entrypoint and to lock
in the API response-envelope contract used by all V2 routers. That PR was
either abandoned, never opened, or was superseded by incremental commits that
landed the implementation without the accompanying governance artefacts
(recovery document, issue linkage, acceptance evidence).

PR-002R is the **replacement** that backfills everything PR-002 should have
produced. All commits on `master` that relate to the V2 runtime entrypoint,
router registration, API envelope models, and error contract are retroactively
treated as part of PR-002R's scope.

---

## Original PR-002 Expected Deliverables (reconstructed)

| # | Deliverable | Status in PR-002R |
|---|---|---|
| 1 | Canonical runtime entrypoint `app.api_v2:app` confirmed | ✅ Verified (`tests/test_entrypoints.py`) |
| 2 | Legacy shim `app.api.main` and `app.legacy.api.main` declared | ✅ Verified |
| 3 | `app/domain/api_v2_models.py` — `ApiEnvelope[T]`, helpers | ✅ Verified |
| 4 | `app/core/exceptions.py` — canonical error codes | ✅ Verified |
| 5 | `docs/api_envelope_contract.md` | ✅ Verified |
| 6 | `docs/error_contract.md` | ✅ Verified |
| 7 | `docs/route_inventory.md` snapshot | ✅ Verified |
| 8 | Envelope applied to all production routers | 🔧 In progress (PR-002R) |
| 9 | `scripts/generate_openapi.py` + `docs/openapi.json` | 🔧 In progress (PR-002R) |
| 10 | Dockerfile / docker-compose entrypoint locked to V2 | 🔧 In progress (PR-002R) |
| 11 | CI: openapi-contract + legacy-route-guard jobs | 🔧 In progress (PR-002R) |

---

## PR-002R Scope

### 1. Canonical runtime (§1.2)

- Dockerfile `CMD` references `app.api_v2:app`.
- `docker-compose.yml` `command` references `app.api_v2:app`.
- CI smoke test imports `app.api_v2`.
- `scripts/check_runtime_entrypoints.py` verifies all entrypoints.

### 2. Router registration hygiene (§1.3)

Already verified. No duplicate blocks; `system.router` is in the registration
loop; unreachable code removed.

### 3. Legacy route exclusion (§1.4)

- V2 production routes defined in `docs/legacy_compatibility.md`.
- Legacy routes excluded from `app.api_v2:app` (verified by tests).
- CI job `legacy-route-guard` enforces this going forward.

### 4. API response envelope (§1.5)

`ApiEnvelope[T]` (from `app/domain/api_v2_models.py`) applied to every
production router endpoint. All responses flow through `ok()`, `fail()`, or
`paginated()` helpers.

### 5. API error contract (§1.6)

Already verified. All error codes, field errors, remediation hints, and
request-ID propagation confirmed in `app/core/exceptions.py`.

### 6. OpenAPI generation (§1.7)

- `scripts/generate_openapi.py` generates `docs/openapi.json`.
- `make openapi` / `make openapi-check` targets added.
- CI job `openapi-contract` fails on schema drift.

---

## Acceptance Criteria

- [ ] All `tests/test_entrypoints.py` pass.
- [ ] All `tests/unit/test_api_v2_router_contract.py` pass.
- [ ] All `tests/unit/test_api_v2_envelope.py` pass.
- [ ] All `tests/unit/test_exception_envelopes.py` pass.
- [ ] `make runtime-check` exits 0.
- [ ] `make openapi-check` exits 0.
- [ ] CI `openapi-contract` job is green.
- [ ] CI `legacy-route-guard` job is green.
- [ ] `docs/openapi.json` committed and hash recorded in release evidence.
- [ ] Completion note added to `docs/project_status.md` and
  `PR_INTEGRATION_SUMMARY.md`.

---

## Related Artefacts

- `docs/api_envelope_contract.md`
- `docs/error_contract.md`
- `docs/route_inventory.md`
- `docs/legacy_compatibility.md`
- `docs/api_v2.md`
- `docs/api_versioning_policy.md`
- `scripts/check_runtime_entrypoints.py`
- `scripts/generate_openapi.py`
- `tests/test_entrypoints.py`
- `tests/unit/test_api_v2_router_contract.py`
- `tests/unit/test_api_v2_envelope.py`
- `tests/unit/test_exception_envelopes.py`
