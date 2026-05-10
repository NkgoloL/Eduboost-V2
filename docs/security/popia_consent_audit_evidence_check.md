# POPIA Consent Audit Evidence Check

## Make Target

```bash
make popia-consent-audit-check
```

## Script

```text
scripts/check_popia_consent_audit_evidence.py
```

## Purpose

This check aggregates the Cluster C POPIA consent/audit baseline evidence into a
single pass/fail command.

## Verification

```bash
make popia-consent-audit-check
pytest -c pytest.ini tests/unit/test_popia_consent_audit_evidence.py -q --no-cov
```


## Parent and POPIA Data-Rights Consent Boundary Evidence

The aggregate checker includes:

- parent route consent-gate wiring
- POPIA data-export active-consent gate
- DSR route boundary documentation


## Assessment and Onboarding Consent Boundary Evidence

The aggregate checker includes:

- assessment attempt active-consent gate
- onboarding submit/archetype active-consent gate
- authenticated catalog boundary documentation for list/questions routes
