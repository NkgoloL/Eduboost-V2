# Dev-Only Endpoint Exposure Guard

## Purpose

Development-only bootstrap endpoints must not expose operational details or
create sessions in production.

## Guarded Endpoint

```text
POST /api/v2/auth/dev-session
```

## Required Production Behavior

The route must check `settings.is_production()` and return `HTTP_404_NOT_FOUND`
with a generic `Not found` response in production.

## Command

```bash
make dev-only-endpoint-check
```

## Verification

```bash
pytest -c pytest.ini tests/unit/test_dev_only_endpoint_exposure.py -q --no-cov
```
