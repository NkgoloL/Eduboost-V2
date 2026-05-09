# Gamification Profile Authorization Wiring

## Endpoint

This slice enforces learner read authorization on:

```text
GET /api/v2/gamification/profile/{learner_id}
```

## Policy Function

```python
require_learner_read_for_current_user(current_user, learner)
```

The route loads the learner first, applies shared object authorization, then
checks consent and returns the gamification profile.

## Verification

```bash
pytest -c pytest.ini \
  tests/unit/test_gamification_profile_authorization_wiring.py \
  tests/integration/test_gamification_profile_authorization.py \
  -q --no-cov
```
