# Assessment Consent Gate

## Learner-Scoped Route

```text
POST /api/v2/assessments/{assessment_id}/attempt
```

Assessment attempt submission processes learner data and must pass:

1. learner write authorization
2. active POPIA consent

## Non-Learner-Scoped Boundary

```text
GET /api/v2/assessments
```

The assessment list endpoint remains an authenticated catalog boundary. It has
no learner identifier and does not process a learner record.

## Verification

```bash
pytest -c pytest.ini tests/unit/test_assessment_consent_gate_wiring.py -q --no-cov
```
