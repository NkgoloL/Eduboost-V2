# Onboarding Authorization Wiring

## Endpoints

```text
POST /api/v2/onboarding/submit
POST /api/v2/onboarding/archetype
```

## Policy Function

```python
require_learner_write_for_current_user(current_user, body.learner_id)
```

Submitting onboarding updates learner archetype state and is treated as a
write-sensitive learner operation.

## Verification

```bash
pytest -c pytest.ini tests/unit/test_onboarding_authorization_wiring.py -q --no-cov
```
