# Diagnostic Items Authorization Wiring

## Endpoint

This slice enforces learner read authorization on:

```text
GET /api/v2/diagnostics/items/{learner_id}
```

## Policy Function

```python
require_learner_read_for_current_user(current_user, learner)
```

The route already loads the learner object before fetching diagnostic items, so
it can reuse the loaded-object policy adapter.

## Coverage

| Scenario | Expected |
| --- | --- |
| Admin reads diagnostic items | 200 |
| Assigned guardian reads diagnostic items | 200 |
| Learner reads own diagnostic items | 200 |
| Unrelated guardian | 403 |
| Missing auth | 401 |
| Missing learner | 404 |

## Verification

```bash
pytest -c pytest.ini \
  tests/unit/test_diagnostic_items_authorization_wiring.py \
  tests/integration/test_diagnostic_items_authorization.py \
  -q --no-cov
```
