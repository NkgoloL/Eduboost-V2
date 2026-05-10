# POPIA Consent Closure CI

## Purpose

The POPIA consent/audit CI workflow runs both component checks and the aggregate
closure command.

## Required CI Command

```bash
make popia-consent-closure-check
```

## Verification

```bash
pytest -c pytest.ini tests/unit/test_popia_consent_closure_ci_contract.py -q --no-cov
```
