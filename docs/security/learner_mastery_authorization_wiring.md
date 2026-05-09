# Learner Mastery Authorization Wiring

## Endpoint

This slice extends the Phase 2 learner read policy to:

```text
GET /api/v2/learners/{learner_id}/mastery
```

## Policy Function

```python
require_learner_read_for_current_user(current_user, learner)
```

The mastery endpoint now uses the same authorization policy as:

```text
GET /api/v2/learners/{learner_id}
```

## HTTP Contract Coverage

| Scenario | Expected |
| --- | --- |
| Admin reads mastery | 200 |
| Assigned guardian reads mastery | 200 |
| Learner reads own mastery | 200 |
| Unrelated guardian reads mastery | 403 |
| Missing auth | 401 |
| Missing learner | 404 |

## Verification

```bash
pytest -c pytest.ini   tests/unit/test_learner_mastery_authorization_wiring.py   tests/integration/test_learner_mastery_authorization.py   -q --no-cov
```

## Follow-Up

The next Phase 2 slice should move from read endpoints to a write-sensitive
operation, preferably a learner-scoped POST with a request body that includes
`learner_id`.
