---
title: "API Contract & Route Documentation"
status: active
owner: backend
reviewers: [frontend, architecture, qa]
audience: developer
source_of_truth: true
supersedes: []
superseded_by: null
last_reviewed: '2026-09-23'
review_interval_days: 90
evidence_command: "make openapi-check && make route-inventory-check"
code_anchors:
  - app/api_v2.py
  - docs/openapi.json
  - docs/route_inventory.md
---

# API Contract & Route Documentation

The generated OpenAPI specification ([`docs/openapi.json`](../openapi.json)) and route inventory ([`docs/route_inventory.md`](../route_inventory.md)) form the API contract source of truth for EduBoost V2. Human-authored documentation must not contradict these generated artifacts.

## Runtime Specification

- **Canonical Application**: `app.api_v2:app` (FastAPI)
- **Application Title**: `EduBoost SA V2`
- **Application Version**: `1.0.0-rc1`

## Prefix Architecture & Routing Topology

EduBoost V2 registers routers under the canonical `/api/v2` prefix:
1. **Canonical Prefix (`/api/v2`)**: The standard contract used by web clients, mobile apps, and integrations. The deprecated `/v2` alias has been completely retired.
2. **Router Registry**: Exactly 234 registered FastAPI route entry points (225 domain routes across 13 router modules + 9 direct root operational routes).

## Required Operational Routes

The following operational endpoints are mounted directly on the application:
- `/` — Service identification and discovery metadata
- `/health` — Shallow liveness probe
- `/ready` — Deep readiness probe (checks PostgreSQL pool, Redis connection, and worker health)
- `/metrics` — Prometheus exposition endpoint
- `/api/v2/health/deep` — Deep health diagnostics
- `/docs` / `/redoc` — Interactive API documentation (Swagger UI & Redoc)
- `/openapi.json` — Machine-readable OpenAPI 3.1.0 specification

## Verification Commands

To verify that active code has not drifted from documentation contracts:

```bash
# Verify route inventory is aligned
.venv/bin/python scripts/generate_route_inventory.py --check

# Verify OpenAPI schema is aligned
.venv/bin/python scripts/generate_openapi.py --check
```

Both checks are enforced in CI via `make openapi-check` and `make route-inventory-check`.
