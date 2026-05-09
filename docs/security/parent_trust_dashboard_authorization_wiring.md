# Parent Trust Dashboard Authorization Wiring

## Endpoint

This slice adds per-learner read authorization inside:

```text
GET /api/v2/parents/{guardian_id}/dashboard
```

## Policy Function

```python
require_learner_read_for_current_user(current_user, learner)
```

The route already checks dashboard ownership at guardian level. This adds a
second learner-object check before consent validation and learner data inclusion.

## Verification

```bash
pytest -c pytest.ini tests/unit/test_parent_trust_dashboard_authorization_wiring.py -q --no-cov
```
