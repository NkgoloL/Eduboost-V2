# Lesson Generation Authorization Wiring

## Endpoint

This slice enforces learner write authorization on:

```text
POST /api/v2/lessons/generate
POST /api/v2/lessons/
```

## Policy Function

```python
require_learner_write_for_current_user(current_user, str(body.learner_id))
```

The check runs before `enqueue_job(...)`, so unauthorized actors cannot enqueue
lesson-generation work for another learner.

## Coverage

| Scenario | Expected |
| --- | --- |
| Admin generates lesson | 202 |
| Guardian with learner claim generates lesson | 202 |
| `/lessons/` alias | 202 |
| Learner self generates lesson | 202 |
| Unrelated guardian | 403 |
| Missing auth | 401 |

## Verification

```bash
pytest -c pytest.ini   tests/unit/test_lesson_generation_authorization_wiring.py   tests/integration/test_lesson_generation_authorization.py   -q --no-cov
```
