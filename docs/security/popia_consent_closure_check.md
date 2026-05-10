# POPIA Consent Closure Check

## Purpose

`make popia-consent-closure-check` is the single aggregate command for the
Cluster C POPIA consent/audit boundary.

## Included Checks

- consent-gate inventory generation
- POPIA consent-boundary matrix generation
- consent-gate allowlist drift check
- audit-event contract check
- consent/audit aggregate evidence check
- consent-boundary matrix check
- object-authorization-before-consent order check
- central consent-source check
- consent-rejection audit check

## Command

```bash
make popia-consent-closure-check
```

## Verification

```bash
pytest -c pytest.ini tests/unit/test_popia_consent_closure_check.py -q --no-cov
```
