# Gamification Award XP Authorization Wiring

## Endpoint

```text
POST /api/v2/gamification/award-xp
```

## Policy Function

```python
require_learner_write_for_current_user(current_user, body.learner_id)
```

Awarding XP mutates learner gamification state and may mark a lesson complete.

## Verification

```bash
pytest -c pytest.ini tests/unit/test_gamification_award_xp_authorization_wiring.py tests/integration/test_gamification_award_xp_authorization.py -q --no-cov
```
