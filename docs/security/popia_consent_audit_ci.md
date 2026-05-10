# POPIA Consent Audit CI

## Workflow

```text
.github/workflows/popia-consent-audit.yml
```

## Covered Checks

```bash
make audit-contract-check
make popia-consent-gate-check
pytest -c pytest.ini tests/unit/test_generate_consent_gate_inventory.py tests/unit/test_consent_gate_inventory_check.py tests/unit/test_audit_event_contracts.py tests/unit/test_popia_consent_audit_baseline_docs.py -q --no-cov
```

## Branch Policy

The workflow runs on pull requests and pushes targeting:

```text
master
release/**
```

## Verification

```bash
pytest -c pytest.ini tests/unit/test_popia_consent_audit_ci_contract.py -q --no-cov
```
