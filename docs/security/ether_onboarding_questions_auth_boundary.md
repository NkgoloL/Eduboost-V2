# Ether Onboarding Questions Authentication Boundary

## Endpoint

```text
GET /api/v2/ether/onboarding/questions
```

## Policy

The route now requires an authenticated user:

```python
user: dict = Depends(get_current_user)
```

The route does not carry a `learner_id`, so it is guarded by authentication
rather than learner-object authorization.

## Verification

```bash
pytest -c pytest.ini tests/unit/test_ether_onboarding_questions_auth_boundary.py -q --no-cov
make learner-authz-check
```
