# Learner Read Authorization HTTP Tests

## Purpose

This slice adds HTTP-level contract tests for the first Phase 2 enforcement
endpoint:

```text
GET /api/v2/learners/{learner_id}
```

The tests exercise the real FastAPI route while replacing the database,
consent service, current-user dependency, and learner repository with
deterministic fakes.

## Coverage

| Scenario | Expected |
| --- | --- |
| Admin reads learner | 200 |
| Assigned guardian reads learner | 200 |
| Learner reads own record | 200 |
| Unrelated guardian reads learner | 403 |
| Missing auth | 401 |
| Missing learner | 404 |

## Test File

```text
tests/integration/test_learner_read_authorization.py
```

## Verification

```bash
pytest -c pytest.ini tests/integration/test_learner_read_authorization.py -q --no-cov
```

## Notes

These tests intentionally do not require a real database. They verify the HTTP
contract and route-level authorization wiring, not repository persistence.
