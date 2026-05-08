# EduBoost API Versioning Policy

## Current Version

The current production API version is:

```text
v2
```

The canonical runtime is:

```text
app.api_v2:app
```

## Supported Prefixes

During the current migration window, production V2 routers are exposed under both prefixes:

```text
/api/v2
/v2
```

## Versioning Rules

- New production API work must target V2.
- New V1 routes are forbidden.
- Archived V1 compatibility behavior must not be mounted in `app.api_v2:app`.
- Breaking API changes require an explicit PR label and OpenAPI diff review.
- `docs/openapi.json` must be regenerated when route, request, or response contracts change.
- `make openapi-check` must pass before merge.

## Compatibility Policy

`app.legacy.api.main:app` may remain as a compatibility import shim, but it is not the canonical production runtime.

Known legacy compatibility behavior:

- `/api/v1/lessons/generate` may return HTTP 410 Gone when the legacy shim is explicitly imported.
- That route must not appear in the canonical V2 OpenAPI schema.

## Evidence

- Runtime tests: `tests/test_entrypoints.py`
- Legacy exclusion tests: `tests/test_legacy_route_exclusion.py`
- OpenAPI generator: `scripts/generate_openapi.py`
- Drift check: `make openapi-check`
