# Consent Rejection Audit

## Purpose

When active consent is missing or expired, learner-data processing must be
rejected and auditable.

## Contract

`ConsentService.require_active_consent` must preserve evidence for:

- `consent.access_rejected`
- `ConsentRequiredError`
- `ConsentExpiredError`
- audit append fallback
- Fourth Estate rejected-outcome semantics

## Command

```bash
make popia-consent-rejection-audit-check
```

## Verification

```bash
pytest -c pytest.ini tests/unit/test_consent_rejection_audit_check.py -q --no-cov
```
