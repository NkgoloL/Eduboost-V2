# PR-002R Release Evidence Index

## Status

This is the release-evidence index for the PR-002R backend runtime and API contract baseline.

PR-002R is a baseline implementation, not a full production-readiness release.

## Canonical Runtime

```text
app.api_v2:app
```

## Branch Policy

```text
master
release/**
```

## Evidence Files

| Evidence | Path |
| --- | --- |
| Runtime/API evidence document | `docs/pr/PR-002R_BACKEND_RUNTIME_API_CONTRACT.md` |
| Project status update | `docs/project_status.md` |
| PR integration summary | `PR_INTEGRATION_SUMMARY.md` |
| Error contract | `docs/error_contract.md` |
| API versioning policy | `docs/api_versioning_policy.md` |
| Route inventory | `docs/route_inventory.md` |
| OpenAPI schema | `docs/openapi.json` |
| OpenAPI generator | `scripts/generate_openapi.py` |
| Route inventory generator | `scripts/generate_route_inventory.py` |
| Runtime entrypoint checker | `scripts/check_runtime_entrypoints.py` |
| OpenAPI drift workflow | `.github/workflows/openapi-drift.yml` |
| Runtime contract workflow | `.github/workflows/runtime-contract.yml` |
| PR template | `.github/pull_request_template.md` |
| Pytest import-path policy | `docs/testing/pytest_import_path.md` |

## Verification Commands

Run from the repository root:

```bash
python3 -c "from app.api_v2 import app; print(app.title)"
make runtime-check
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
  tests/unit/test_generate_route_inventory.py \
  tests/unit/test_check_runtime_entrypoints.py \
  tests/unit/test_pr002r_governance_contract.py \
  tests/unit/test_pytest_import_path.py \
  -q --no-cov
```

## Completion Criteria

PR-002R evidence is complete when runtime check, OpenAPI drift check, route inventory drift check, focused tests, and CI pass.

## Explicit Non-Scope

This evidence does not approve production or public beta use. The remaining release blockers include security and object-level authorization, POPIA consent enforcement, audit-chain integrity, backup/restore proof, AI/CAPS validation, frontend production journeys, staging acceptance, incident response, and final go/no-go review.
