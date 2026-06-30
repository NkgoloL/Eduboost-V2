# Health & Readiness Contract

**Owner:** Platform / Operations
**Last updated:** 2026-05-27 (Phase 0 T010)
**Authoritative source:** `app/api_v2.py`

This document is the single source of truth for the EduBoost V2 health probe
contract. App code, smoke tests, Docker Compose, Dockerfiles, and Render
configuration must agree with this document. Drift between any of these is a
release-blocking issue.

---

## Endpoints

The V2 application exposes four health-related HTTP routes. They split cleanly
into two semantic categories: **liveness** and **readiness**.

### `/health` — liveness

- **Purpose:** Lightweight liveness probe. Confirms the process is alive and
  the FastAPI app is serving requests. Does *not* check downstream dependencies.
- **Method:** `GET`
- **Status codes:** `200 OK` always (process is up).
- **Body:**
  ```json
  {"status": "ok", "version": "<APP_VERSION>", ...}
  ```
- **Used by:** Lightweight reverse-proxy liveness checks, uptime monitors,
  developer ad-hoc curl.
- **Implementation:** `@app.get("/health")` in `app/api_v2.py`.

### `/ready` — deep readiness (canonical)

- **Purpose:** Deep readiness probe. Confirms the app *and* its critical
  downstream dependencies (database, Redis, etc.) are healthy enough to serve
  real traffic. This is the **canonical** readiness endpoint.
- **Method:** `GET`
- **Status codes:**
  - `200 OK` — status is `ok` or `degraded` (degraded means some non-critical
    dependency is unhealthy; the app can still serve core traffic).
  - `503 Service Unavailable` — status is `error` (at least one critical
    dependency is unhealthy; the instance should be removed from the load
    balancer).
- **Body:** Result of `app.core.health.gather_deep_health()`.
- **Used by:**
  - Docker Compose healthcheck (`docker-compose*.yml`, `staging/pr_008/docker-compose*.yml`).
  - Dockerfile HEALTHCHECK directive (`docker/Dockerfile.v2`, `staging/pr_008/docker/Dockerfile.v2`).
  - Render `healthCheckPath` (`render.yaml`).
  - Kubernetes `readinessProbe` (if/when k8s manifests are reintroduced).
- **Implementation:** `@app.get("/ready")` in `app/api_v2.py`, sharing a handler
  with the two API-namespaced aliases below.

### `/v2/health/deep` — alias of `/ready`

- **Purpose:** Same handler as `/ready`, exposed under the `/v2/` namespace for
  callers that expect a versioned operational API.
- **Status & body:** Identical to `/ready`.
- **Implementation:** Decorator alias on the `ready()` handler in
  `app/api_v2.py`.

### `/api/v2/health/deep` — alias of `/ready`

- **Purpose:** Same handler as `/ready`, exposed under `/api/v2/` for callers
  that route all application traffic through `/api/v2/`.
- **Status & body:** Identical to `/ready`.
- **Implementation:** Decorator alias on the `ready()` handler in
  `app/api_v2.py`.

---

## Configuration alignment

| Surface | Path | Notes |
|---|---|---|
| `app/api_v2.py` | `/health`, `/ready`, `/v2/health/deep`, `/api/v2/health/deep` | Authoritative. |
| `docker-compose.yml` (app healthcheck) | `/ready` | Deep readiness. |
| `docker-compose.prod.yml` | (db/redis only) | App not directly health-probed; relies on orchestrator. |
| `staging/pr_008/docker-compose.yml` | `/ready` | Deep readiness. |
| `staging/pr_008/docker-compose.prod.yml` | `/ready` | Deep readiness. |
| `docker/Dockerfile.v2` HEALTHCHECK | `/ready` | Deep readiness. |
| `staging/pr_008/docker/Dockerfile.v2` HEALTHCHECK | `/ready` | Deep readiness. |
| `render.yaml` `healthCheckPath` | `/ready` | Updated 2026-05-27 (T010). |
| `docker/Dockerfile.inference` HEALTHCHECK | `/health` | **Different service** (inference server). Out of scope for the API health contract. |

---

## Test expectations

Smoke tests must use only the routes listed above. As of 2026-05-27:

- `tests/smoke/test_v2_smoke.py` — exercises `/health` (liveness) and `/ready`
  (readiness) per the contract.
- `tests/smoke/test_app_import.py` — exercises the legacy v1 app's `/health`
  route; not part of the V2 contract.
- `tests/smoke/test_content_factory_*.py` — imports `app.api_v2:app`, not the
  removed `app.main` shim.

**Forbidden patterns** (any reintroduction is a release-blocking drift):

- `/health/ready` — does not exist.
- `from app.main import app` — the `app.main` module was removed; use
  `from app.api_v2 import app`.

---

## Changing the contract

Any change to the health contract must:

1. Update `app/api_v2.py` and the corresponding test file in `tests/smoke/`.
2. Update every healthcheck / probe configuration listed in the table above
   in the same PR.
3. Update this document in the same PR.
4. Be reviewed by Platform / Operations before merge.

A PR that changes a probe path in one surface but not the others is invalid
and must be rejected.
