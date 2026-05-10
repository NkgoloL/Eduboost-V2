# Study Plan Consent Gate

## Routes

```text
POST /api/v2/study-plans/{learner_id}
POST /api/v2/study-plans/generate/{learner_id}
```

## Policy

Study-plan generation processes learner data and must pass:

1. learner write authorization
2. active POPIA consent

The consent gate runs before the background job is enqueued.

## Verification

```bash
pytest -c pytest.ini tests/unit/test_study_plan_consent_gate_wiring.py -q --no-cov
```
