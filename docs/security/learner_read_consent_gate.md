# Learner Read Consent Gate

## Routes

```text
GET /api/v2/learners/{learner_id}
GET /api/v2/learners/{learner_id}/mastery
```

## Policy

Learner profile and mastery reads must pass:

1. learner read authorization
2. active POPIA consent

The routes now use the centralized `require_active_consent_for_current_user`
adapter so actor attribution is consistent with the rest of Cluster C.

## Verification

```bash
pytest -c pytest.ini tests/unit/test_learner_read_consent_gate_wiring.py -q --no-cov
```
