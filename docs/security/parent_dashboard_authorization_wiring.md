# Parent Dashboard Authorization Wiring

## Endpoint

This slice adds per-learner read authorization inside:

```text
GET /api/v2/parents/dashboard
```

## Policy Function

```python
require_learner_read_for_current_user(current_user, learner)
```

The route already loads learners by guardian. This adds the shared Phase 2
learner-object policy before consent validation and data inclusion.

## Verification

```bash
pytest -c pytest.ini tests/unit/test_parent_dashboard_authorization_wiring.py -q --no-cov
```
