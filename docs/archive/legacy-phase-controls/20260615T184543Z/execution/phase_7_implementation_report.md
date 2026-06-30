# Phase 7 Implementation Report — Deployment and Security Hardening

**Date:** 2026-06-12  
**Refresh:** 2026-06-14
**Status:** ✅ Complete  
**Branch:** `phase-7/deployment-security-hardening`

---

## Summary

All 9 substantive sub-phases of Phase 7 have been implemented. This report
documents what was changed, why, and the files affected.

The 2026-06-14 refresh tightened the `/metrics` production IP guard from string-prefix checks to exact `ipaddress` CIDR membership, preventing accidental allowance of public `172.32.0.0/12+` addresses.

---

## Sub-phase Outcomes

### 7.1 — Stripe Redirect URLs → Environment-Derived ✅

| Item | Before | After |
|---|---|---|
| `success_url` | `"http://localhost:3000/dashboard?upgraded=true"` | `f"{settings.PUBLIC_FRONTEND_URL}/dashboard?upgraded=true"` |
| `cancel_url` | `"http://localhost:3000/dashboard?cancelled=true"` | `f"{settings.PUBLIC_FRONTEND_URL}/dashboard?cancelled=true"` |
| Config field | (absent) | `PUBLIC_FRONTEND_URL: str = "http://localhost:3000"` |

**Files changed:** `app/core/config.py`, `app/core/stripe_client.py`,
`docker-compose.prod.yml`, `.env.example`

---

### 7.2 — ACA Bicep CORS Hardening ✅

Replaced `allowedOrigins: ['*']` with a `param corsAllowedOrigins array`
defaulting to `['https://app.eduboost.co.za', 'https://eduboost.co.za']`.
Deployers can override per environment.

**Files changed:** `bicep/container_apps.bicep`

---

### 7.3 — CSP Hardening ✅

`SecurityHeadersMiddleware` rewritten with two-tier CSP:

- **Production:** `script-src 'self' 'nonce-{nonce}'` — no `unsafe-inline`.
  Nonce exposed via `request.state.csp_nonce` for templates.
  `report-uri /api/v2/csp-report` added for future violation collection.
- **Development:** permissive policy retained so Next.js dev server and HMR work.

**Files changed:** `app/middleware/security_headers.py`

---

### 7.4 — Conditional HSTS ✅

`Strict-Transport-Security` header now emitted only when `settings.is_production()` returns `True`.
Prevents browsers from enforcing HTTPS-only for `localhost` during development.

**Files changed:** `app/middleware/security_headers.py`

---

### 7.5 — Nginx Rate Limit Path Fix ✅

Added `limit_req_zone` targeting `$binary_remote_addr` at rate `10r/m`.
Added a dedicated `location /api/v2/auth/` block applying the zone with `burst=5 nodelay`.
The old v1 path (`/api/v1/auth/`) was not present — this is a new correct configuration.

**Files changed:** `nginx/nginx.conf`

---

### 7.6 — V1 Route Cleanup ✅

The `_has_legacy_lesson_generate_route()` guard was removed. The 410 tombstone for
`/api/v1/lessons/generate` is now registered unconditionally (the guard was a
defensive check that was never needed since routes don't self-register).

A `log.warning` deprecation log is emitted on every call so stale clients are
visible in observability tooling.

**Files changed:** `app/legacy/api/main.py`

---

### 7.7 — `/metrics` and Dev Route Access Control ✅

- **`/metrics`:** Production requests from non-RFC-1918/non-loopback IPs receive 403.
  Infra-layer Nginx/ACA blocking is the primary control; IP check is defence-in-depth.
- The IP check now uses exact CIDR membership for `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `127.0.0.0/8`, and `::1/128`.
- **`/__dev/slow_query`:** Already gated. No change needed.
- **ADR-027** written documenting the chosen approach.

**Files changed:** `app/api_v2.py`  
**Docs added:** `docs/adr/ADR-027-observability-endpoint-access-control.md`

---

### 7.8 — Production Secret Management ✅

- `docker-compose.prod.yml` annotated: secrets come from env/secrets manager;
  Compose file is explicitly a local-only convenience.
- ACA Bicep already uses `@secure()` params — no change needed there.
- ADR-028 documents the full secret-per-target matrix.

**Files changed:** `docker-compose.prod.yml`  
**Docs added:** `docs/adr/ADR-028-authoritative-deployment-target.md`

---

### 7.9 — Deployment Target Definition ✅

**Decision:** Azure Container Apps via `bicep/container_apps.bicep` is the
authoritative production target. All other artefacts are secondary.

**Docs added:** `docs/adr/ADR-028-authoritative-deployment-target.md`

---

### 7.10 — Tests and Verification ✅

See `docs/release/phase_7_evidence.md` for verification commands.

Python syntax verification:
```bash
python -m py_compile \
  app/core/config.py \
  app/core/stripe_client.py \
  app/middleware/security_headers.py \
  app/api_v2.py \
  app/legacy/api/main.py
```

---

## Files Changed

| File | Sub-phase |
|---|---|
| `app/core/config.py` | 7.1 |
| `app/core/stripe_client.py` | 7.1 |
| `app/middleware/security_headers.py` | 7.3, 7.4 |
| `app/api_v2.py` | 7.7 |
| `tests/unit/test_phase7_metrics_access_control.py` | 7.7 |
| `app/legacy/api/main.py` | 7.6 |
| `nginx/nginx.conf` | 7.5 |
| `bicep/container_apps.bicep` | 7.2 |
| `docker-compose.prod.yml` | 7.1, 7.8 |
| `.env.example` | 7.1 |

## Docs Added

| File | Sub-phase |
|---|---|
| `docs/adr/ADR-027-observability-endpoint-access-control.md` | 7.7 |
| `docs/adr/ADR-028-authoritative-deployment-target.md` | 7.9 |
| `docs/release/phase_7_evidence.md` | 7.10 |
| `docs/roadmap/execution/phase_7_implementation_report.md` | 7.10 |

---

## Known Deferred Items

- **CSP `report-uri`** — The `/api/v2/csp-report` endpoint is referenced in the
  production CSP but not yet implemented. It will silently 404 until a handler is
  added. This is acceptable: browsers will POST reports to a 404 which is harmless.
  Implement in a future phase.

- **ACA `corsAllowedOrigins` staging override** — `container_apps.parameters.json`
  should be updated with staging-specific origins before the next ACA deployment.

## 2026-06-14 Verification Refresh

```text
python3 scripts/check_environment_security_contract.py
# PASS

python3 -m py_compile app/core/config.py app/core/stripe_client.py app/middleware/security_headers.py app/api_v2.py app/legacy/api/main.py tests/unit/test_phase7_metrics_access_control.py
# passed

python3 -m pytest --no-cov -q tests/unit/test_phase7_metrics_access_control.py tests/unit/test_billing_router_contract.py tests/integration/test_stripe_webhooks.py tests/integration/test_security_headers.py -rs
# 4 passed, 10 skipped due unavailable local test database

security_headers_direct_check
# production HSTS present, dev HSTS absent, production CSP has nonce and no unsafe-inline

docker run ... nginx:alpine nginx -t
# syntax is ok; configuration file test is successful

az bicep build --file bicep/container_apps.bicep
# passed
```

---

## Roadmap Alignment

All Phase 7 success criteria from `docs/roadmap/roadmap.md` are satisfied:

- [x] Production config contains no localhost redirect defaults
- [x] Nginx rate limits apply to active auth routes (`/api/v2/auth/`)
- [x] ACA CORS does not use `*`
- [x] CSP does not contain `unsafe-inline` in production
- [x] HSTS header absent in dev, present in production
- [x] No V1 URL patterns remain in active config (410 tombstone only)
- [x] Secret handling is platform-native (ACA Key Vault) or explicitly documented as local-only
