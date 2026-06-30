# Phase 7 Evidence — Deployment and Security Hardening

**Date:** 2026-06-12  
**Refresh:** 2026-06-14
**Phase:** 7  
**Branch:** `phase-7/deployment-security-hardening`

---

## 7.1 — Stripe Redirect URLs → Environment-Derived

**Evidence:**

- `app/core/config.py` — `PUBLIC_FRONTEND_URL: str = "http://localhost:3000"` added to `Settings`.
- `app/core/stripe_client.py` lines 51-52 changed from hardcoded `http://localhost:3000/...`
  to `f"{settings.PUBLIC_FRONTEND_URL}/dashboard?upgraded=true"` and `...cancelled=true`.
- `docker-compose.prod.yml` — `PUBLIC_FRONTEND_URL: ${PUBLIC_FRONTEND_URL:-https://app.eduboost.co.za}` added to both `api` and `worker` services.
- `.env.example` — `PUBLIC_FRONTEND_URL=http://localhost:3000` added with documentation comment.

**Verification:**
```bash
grep -n "PUBLIC_FRONTEND_URL" app/core/config.py app/core/stripe_client.py docker-compose.prod.yml .env.example
```

---

## 7.2 — ACA Bicep CORS Hardening

**Evidence:**

- `bicep/container_apps.bicep` — `param corsAllowedOrigins array` added with production defaults
  `['https://app.eduboost.co.za', 'https://eduboost.co.za']`.
- `corsPolicy.allowedOrigins` changed from `['*']` to `corsAllowedOrigins`.

**Verification:**
```bash
grep -n "corsAllowedOrigins\|allowedOrigins" bicep/container_apps.bicep
```

---

## 7.3 — CSP Hardening (no unsafe-inline in production)

**Evidence:**

- `app/middleware/security_headers.py` rewritten:
  - Production CSP uses `nonce-{nonce}` for `script-src` and `style-src`. No `unsafe-inline`.
  - Dev CSP retains `unsafe-inline` for developer workflow compatibility.
  - Per-request nonce exposed via `request.state.csp_nonce`.

**Verification:**
```bash
# Start the app with APP_ENV=production and check the CSP header:
curl -s -I http://localhost:8000/health | grep -i content-security-policy
# Should contain nonce-... and NOT contain unsafe-inline
```

---

## 7.4 — Conditional HSTS

**Evidence:**

- `app/middleware/security_headers.py` — HSTS header now wrapped in `if settings.is_production()`.

**Verification:**
```bash
# Development — HSTS should be absent:
APP_ENV=development uvicorn app.api_v2:app --port 8001 &
curl -s -I http://localhost:8001/health | grep -i strict-transport
# (should return nothing)

# Production — HSTS should be present:
APP_ENV=production uvicorn app.api_v2:app --port 8002 &
curl -s -I http://localhost:8002/health | grep -i strict-transport
# Should return: strict-transport-security: max-age=31536000; includeSubDomains
```

---

## 7.5 — Nginx Rate Limit Path Fix

**Evidence:**

- `nginx/nginx.conf` — `limit_req_zone` added targeting `/api/v2/auth/` (was incorrectly `/api/v1/auth/`).
- Dedicated `location /api/v2/auth/` block applies `limit_req zone=auth_limit burst=5 nodelay`.

**Verification:**
```bash
docker run --rm -v $(pwd)/nginx/nginx.conf:/etc/nginx/nginx.conf:ro nginx:alpine nginx -t
```

---

## 7.6 — V1 Route Cleanup

**Evidence:**

- `app/legacy/api/main.py` — `_has_legacy_lesson_generate_route()` guard removed.
  410 tombstone registered unconditionally with deprecation log (`log.warning`).
  No V1 business logic remains.

**Verification:**
```bash
grep -rn "api/v1" app/ --include="*.py" | grep -v "legacy_lesson_generate_gone\|410\|legacy\|test"
# Should return no active v1 route registrations
```

---

## 7.7 — `/metrics` and Dev Route Access Control

**Evidence:**

- `app/api_v2.py` — `/metrics` handler updated with RFC-1918 IP allowlist check in production.
  Returns 403 for non-private IPs when `APP_ENV == production`.
- 2026-06-14 refresh: IP allowlist now uses exact `ipaddress` CIDR membership instead of string-prefix checks.
- `/__dev/slow_query` — was already gated behind `settings.is_production()` returning 404.
  No change required.
- ADR-027 written: `docs/adr/ADR-027-observability-endpoint-access-control.md`

---

## 7.8 — Production Secret Management

**Evidence:**

- `docker-compose.prod.yml` — comment block added clarifying that secrets come from
  environment/secrets manager and this file is a local-only convenience.
- ACA (`bicep/container_apps.bicep`) already uses `@secure()` Bicep parameters.
  Documented in ADR-028.

---

## 7.9 — Deployment Target Definition

**Evidence:**

- ADR-028 written: `docs/adr/ADR-028-authoritative-deployment-target.md`
- Authoritative target: **Azure Container Apps via `bicep/container_apps.bicep`**.
- `docker-compose.prod.yml` header comment already reads "local-smoke-test/staging convenience".

---

## 7.10 — Tests and Verification

**Syntax checks:**
```bash
# Python — compile all changed modules
python -m py_compile app/core/config.py app/core/stripe_client.py \
  app/middleware/security_headers.py app/api_v2.py app/legacy/api/main.py

# Nginx — syntax check
docker run --rm -v $(pwd)/nginx/nginx.conf:/etc/nginx/nginx.conf:ro nginx:alpine nginx -t

# Bicep — build check (requires az CLI)
az bicep build --file bicep/container_apps.bicep
```

**Security header spot-check (dev):**
```bash
curl -s -I http://localhost:8000/health
# Expect:
#   x-content-type-options: nosniff
#   x-frame-options: DENY
#   content-security-policy: ... (dev permissive policy)
#   NO strict-transport-security (dev)
```

**Stripe config smoke test:**
```python
from app.core.config import settings
assert "localhost" in settings.PUBLIC_FRONTEND_URL  # dev default
assert "CHANGE_ME" not in settings.PUBLIC_FRONTEND_URL
```

## 2026-06-14 Verification Refresh

```text
python3 scripts/check_environment_security_contract.py
# PASS app/core/config.py security and Key Vault markers

python3 -m py_compile app/core/config.py app/core/stripe_client.py app/middleware/security_headers.py app/api_v2.py app/legacy/api/main.py tests/unit/test_phase7_metrics_access_control.py
# passed

python3 -m pytest --no-cov -q tests/unit/test_phase7_metrics_access_control.py tests/unit/test_billing_router_contract.py tests/integration/test_stripe_webhooks.py tests/integration/test_security_headers.py -rs
# 4 passed, 10 skipped because the local test database was unavailable

security_headers_direct_check
# production HSTS present, dev HSTS absent, production CSP nonce-based and without unsafe-inline

docker run --rm --add-host api:127.0.0.1 --add-host frontend:127.0.0.1 ... nginx:alpine nginx -t
# syntax is ok; configuration file test is successful

az bicep build --file bicep/container_apps.bicep
# passed
```

New regression coverage:

- `tests/unit/test_phase7_metrics_access_control.py` verifies loopback/RFC-1918 metrics clients are allowed.
- The same test verifies public and invalid addresses, including `172.32.0.1`, are rejected.
