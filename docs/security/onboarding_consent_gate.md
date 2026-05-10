# Onboarding Consent Gate

## Learner-Scoped Routes

```text
POST /api/v2/onboarding/submit
POST /api/v2/onboarding/archetype
```

Onboarding submission updates learner archetype data and must pass:

1. learner write authorization
2. active POPIA consent

## Non-Learner-Scoped Boundary

```text
GET /api/v2/onboarding/questions
```

The questions endpoint remains an authenticated catalog boundary. It has no
learner identifier and does not process a learner record.

## Verification

```bash
pytest -c pytest.ini tests/unit/test_onboarding_consent_gate_wiring.py -q --no-cov
```
