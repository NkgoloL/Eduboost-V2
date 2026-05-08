# EduBoost V2 Route Inventory

## Status

This document records the PR-002R route inventory baseline.

The canonical production runtime is:

```text
app.api_v2:app
```

## Operational Routes

| Route | Purpose |
| --- | --- |
| `/` | Root runtime response. |
| `/health` | Basic health check. |
| `/ready` | Readiness check. |
| `/metrics` | Prometheus metrics endpoint. |
| `/v2/health/deep` | Deeper V2 health check. |
| `/docs` | Swagger UI. |
| `/redoc` | ReDoc UI. |
| `/openapi.json` | Runtime OpenAPI schema. |

## Production V2 Router Prefixes

Each production router should be available under both:

```text
/api/v2
/v2
```

Required router fragments include:

```text
/auth
/learners
/lessons
/study-plans
/diagnostics
/gamification
/onboarding
/parents
/billing
/consent
/popia
/jobs
/system
```

## Legacy Exclusion Rules

The canonical runtime must not expose V1 routes.

Known archived compatibility route:

```text
/api/v1/lessons/generate
```

This route may return HTTP 410 Gone only when `app.legacy.api.main:app` is explicitly imported. It must not be part of the canonical `app.api_v2:app` route table or V2 OpenAPI schema.

## Regeneration Command

```bash
python3 - <<'PY'
from fastapi.routing import APIRoute
from app.api_v2 import app

for route in sorted(app.routes, key=lambda r: getattr(r, "path", "")):
    if isinstance(route, APIRoute):
        methods = ",".join(sorted(route.methods or []))
        print(f"{methods:16} {route.path}")
PY
```

## Evidence

- Runtime route tests: `tests/test_entrypoints.py`
- Legacy route exclusion tests: `tests/test_legacy_route_exclusion.py`
- OpenAPI artifact: `docs/openapi.json`
