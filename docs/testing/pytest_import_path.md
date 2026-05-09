# Pytest Import Path Policy

## Purpose

EduBoost keeps the backend application package in the repository-local `app/`
directory. Tests must be importable from local shells, CI, and IDE runners
without requiring every test module to patch `sys.path`.

## Policy

`tests/conftest.py` is responsible for adding the repository root to
`sys.path` during pytest collection.

Individual test files should not add repository-root path patches unless they
intentionally run subprocesses or load standalone scripts by absolute path.

## Verification

Run:

```bash
pytest -c pytest.ini tests/unit/test_pytest_import_path.py -q --no-cov
```

For PR-002R, also run the focused runtime/API contract suite:

```bash
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

## Non-Goal

This policy does not require the full historical test suite to pass. Some
legacy, integration, POPIA, and smoke tests may still expose behavior-level
failures. This policy only guarantees repository-local imports are consistently
available during pytest collection.
