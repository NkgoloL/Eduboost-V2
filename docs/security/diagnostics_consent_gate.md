# Diagnostics Consent Gate

## Routes

```text
GET /api/v2/diagnostics/items/{learner_id}
POST /api/v2/diagnostics/submit
```

## Policy

Diagnostic item retrieval and submission process learner data and must pass:

1. learner object authorization
2. active POPIA consent

## Verification

```bash
pytest -c pytest.ini tests/unit/test_diagnostics_consent_gate_wiring.py -q --no-cov
```
