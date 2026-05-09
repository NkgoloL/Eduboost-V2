# Dev Session Environment Gate

## Endpoint

```text
POST /api/v2/auth/dev-session
```

## Policy

The dev-session endpoint is a local/non-production bootstrap route. It must not
be visible in production.

The route enforces:

```python
if settings.is_production():
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
```

Returning `404` instead of `403` avoids disclosing the existence of the local
bootstrap endpoint in production.

## Verification

```bash
pytest -c pytest.ini tests/unit/test_dev_session_environment_gate.py -q --no-cov
```
