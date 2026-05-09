# Lesson Stream Authorization Wiring

## Endpoint

```text
POST /api/v2/lessons/generate/stream
```

## Policy Function

```python
require_learner_write_for_current_user(current_user, str(body.learner_id))
```

The stream endpoint generates learner-scoped lesson content and is treated as a write-sensitive learner operation.

## Verification

```bash
pytest -c pytest.ini tests/unit/test_lesson_stream_authorization_wiring.py tests/integration/test_lesson_stream_authorization.py -q --no-cov
```
