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
| PR acceptance checklist | `.github/pull_request_template.md`, `tests/unit/test_pr002r_governance_contract.py` |
| Pytest import-path policy | `tests/conftest.py`, `tests/unit/test_pytest_import_path.py`, `docs/testing/pytest_import_path.md` |
| Release evidence index | `docs/release/PR-002R_EVIDENCE.md` |

## Verification Commands

```bash
python3 -c "from app.api_v2 import app; print(app.title)"
python3 scripts/generate_openapi.py
make openapi-check
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
