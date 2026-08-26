# Test Taxonomy and Fast-Suite Manifest

## 1. Test Taxonomy Classification
All tests in EduBoost V2 are classified into five strict categories:

1. **`product_unit`** (`tests/unit/`): Fast, memory-only unit tests with isolated mocks. Zero network or real database I/O. Expected runtime: < 100ms per test.
2. **`product_integration`** (`tests/integration/`): Real database (PostgreSQL 16 + pgvector) and Redis service integration testing actual repositories and services.
3. **`runtime_stack`** (`tests/runtime/`): Health, readiness (`/ready`), Alembic migrations, worker pools, and connection-resilience tests.
4. **`governance_contract`** (`tests/governance/`, `scripts/production_readiness/`): Machine-readable register schema validation, doc freshness, release boundaries, and API envelope contracts.
5. **`release_evidence`** (`scripts/true_state_remediation/`): Release gate execution and cryptographic evidence compilation.

## 2. Deterministic Fast-Suite Manifest (PR Gate)
The deterministic PR fast-suite executes in `pr-core.yml` and locally via `pytest tests/unit/test_etl_mcp_server_startup.py tests/unit/test_subscription_service.py tests/unit/test_password_policy.py tests/unit/test_popia_consent_versioning.py`:
- `tests/unit/test_etl_mcp_server_startup.py`
- `tests/unit/test_subscription_service.py`
- `tests/unit/test_password_policy.py`
- `tests/unit/test_popia_consent_versioning.py`

Total expected duration: **< 5 seconds**.
