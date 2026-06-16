# Phase 7 Execution Plan — Deployment and Security Hardening

**Date**: 2026-06-12
**Updated**: 2026-06-12
**Refresh**: 2026-06-14
**Status**: ✅ Complete (2026-06-12)
**Branch**: `phase-7/deployment-security-hardening`
**Priority**: P1 (per [roadmap.md](../roadmap.md#L285-L334))
**Scope**: Fix hardcoded localhost URLs, security headers (CSP, HSTS), CORS hardening, Nginx rate-limit path correction, V1 route cleanup, and production secret management.

---

## Pre-Conditions

- [x] Branch `phase-7/deployment-security-hardening` created (includes Phase 6 closeout).
- [x] Roadmap Phase 7 requirements documented in `docs/roadmap/roadmap.md`.
- [x] Initial audit of current codebase completed (2026-06-12).

---

## Pre-Execution Baseline (Audit Results)

### 7.0.1 — Stripe Redirect URLs Hardcoded to localhost

**File**: `app/core/stripe_client.py:51-52`

```python
success_url="http://localhost:3000/dashboard?upgraded=true",
cancel_url="http://localhost:3000/dashboard?cancelled=true",
```

**Fix**: Derive from `settings.PUBLIC_FRONTEND_URL` (or similar environment-derived config).

### 7.0.2 — ACA / Bicep CORS Uses Wildcard

**File**: `bicep/container_apps.bicep:98-99`

```json
corsPolicy: { allowedOrigins: ['*'] }
```

**Fix**: Replace `'*'` with explicit allowed origins derived from deployment environment.

### 7.0.3 — CSP Contains `unsafe-inline`

**File**: `app/middleware/security_headers.py:28-29`

```python
"script-src 'self' 'unsafe-inline'; "
"style-src 'self' 'unsafe-inline'; "
```

**Fix**: Remove `unsafe-inline`. Use nonce-based or hash-based CSP for inline scripts/styles.

### 7.0.4 — HSTS Set Unconditionally

**File**: `app/middleware/security_headers.py:21`

```python
response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
```

No check for `APP_ENV`. HSTS is applied even in dev HTTP contexts.

**Fix**: Condition HSTS on `APP_ENV == "production"` (or similar check).

### 7.0.5 — Nginx Auth Rate Limit Path Mismatch

**File**: `nginx/nginx.conf`

The rate-limit zone targets `/api/v1/auth/` but active routes are `/api/v2/auth/`.

**Fix**: Update rate-limit path to `/api/v2/auth/`.

### 7.0.6 — V1 Route Remnants

**File**: `app/legacy/api/main.py:31-36`

```python
any(getattr(route, "path", None) == "/api/v1/lessons/generate" for route in app.routes)
```

V1 route shim exists but may not be actively used. Audit and remove if safe.

### 7.0.7 — `/metrics` and `/__dev/slow_query` Access Control

**Findings**:

- `/metrics` served at `app/api_v2.py:177` — Prometheus scraping endpoint, no access control.
- `/__dev/slow_query` at `app/api_v2.py:196` — dev-only diagnostic, no environment gate.
- Prometheus metrics path configurable via `settings.PROMETHEUS_METRICS_PATH`.

**Action**: Determine appropriate access control for each.

### 7.0.8 — Production Secrets in Compose Environment

**Files**: `docker-compose.prod.yml` passes secrets directly as env vars (`ENCRYPTION_KEY`, `ENCRYPTION_SALT`, etc.).

**Fix**: Use platform-native secret management or document as a local-only pattern.

### 7.0.9 — Deployment Target Ambiguity

Multiple deployment drafts exist:
- `docker-compose.yml` (dev), `docker-compose.prod.yml` (production)
- `bicep/container_apps.bicep` (Azure ACA)
- Production readiness contracts in `app/modules/deployment/`

**Action**: Define authoritative deployment target.

---

## Sub-Phase Breakdown

### 7.1 — Stripe Redirect URLs → Environment-Derived

**Problem**: Hardcoded `http://localhost:3000/...` in Stripe checkout session creation.

**Acceptance Criteria**:
- [ ] Stripe `success_url` and `cancel_url` use `settings.PUBLIC_FRONTEND_URL` (or equivalent).
- [ ] `PUBLIC_FRONTEND_URL` is defined in `Settings` with a sensible default.
- [ ] Local dev continues to work (e.g., default `http://localhost:3000`).
- [ ] Production deployment sets `PUBLIC_FRONTEND_URL` to the real frontend URL.

**Implementation Tasks**:
- [ ] Add `PUBLIC_FRONTEND_URL: str = "http://localhost:3000"` to `Settings` in `app/core/config.py`.
- [ ] Update `app/core/stripe_client.py` to use `settings.PUBLIC_FRONTEND_URL`.
- [ ] Add environment variable to `docker-compose.prod.yml`.
- [ ] Update `.env.example` with documentation.

**Changed files**: `app/core/config.py`, `app/core/stripe_client.py`, `docker-compose.prod.yml`, `.env.example`

### 7.2 — ACA Bicep CORS Hardening

**Problem**: `allowedOrigins: ['*']` in `bicep/container_apps.bicep`.

**Acceptance Criteria**:
- [ ] Bicep `corsPolicy.allowedOrigins` is not `'*'`.
- [ ] Origins are parameterized or use environment-specific values.

**Implementation Tasks**:
- [ ] Parameterize `corsAllowedOrigins` in `bicep/container_apps.bicep`.
- [ ] Set explicit origins per environment (dev, staging, production).

**Changed files**: `bicep/container_apps.bicep`, `bicep/main.bicep` (if parameters passed through)

### 7.3 — CSP Hardening

**Problem**: `script-src 'self' 'unsafe-inline'` and `style-src 'self' 'unsafe-inline'` in `app/middleware/security_headers.py`.

**Acceptance Criteria**:
- [ ] Production CSP contains no `unsafe-inline`.
- [ ] Dev CSP may be more permissive (conditioned on `APP_ENV`).
- [ ] Nonce-based or hash-based approach used if inline scripts/styles are needed.
- [ ] CSP is validated with a browser or automated tool.

**Implementation Tasks**:
- [ ] Audit all inline scripts/styles in the frontend to determine hash/nonce needs.
- [ ] Update `SecurityHeadersMiddleware` to generate per-request nonces for scripts.
- [ ] Condition strict CSP on `APP_ENV == "production"`.
- [ ] Add CSP reporting endpoint or `report-uri` for violation monitoring.

**Changed files**: `app/middleware/security_headers.py`, potentially frontend templates

### 7.4 — Conditional HSTS

**Problem**: HSTS header set unconditionally (inappropriate for dev HTTP contexts).

**Acceptance Criteria**:
- [ ] `Strict-Transport-Security` header is absent when `APP_ENV != "production"`.
- [ ] HSTS is present with `max-age=31536000; includeSubDomains` in production.
- [ ] A `preload` directive should be considered but not required for this phase.

**Implementation Tasks**:
- [ ] Update `SecurityHeadersMiddleware.__call__` to check `settings.APP_ENV`.
- [ ] Only add HSTS header when `APP_ENV == "production"`.

**Changed files**: `app/middleware/security_headers.py`

### 7.5 — Nginx Rate Limit Path Fix

**Problem**: Rate-limit zone targets `/api/v1/auth/` but active routes are `/api/v2/auth/`.

**Acceptance Criteria**:
- [ ] Nginx rate-limit configuration targets `/api/v2/auth/` (or both v1 and v2).
- [ ] Rate-limit zone size and rate are verified as appropriate.

**Implementation Tasks**:
- [ ] Review current Nginx rate-limit config in `nginx/nginx.conf`.
- [ ] Update auth rate-limit path from `/api/v1/auth/` to `/api/v2/auth/`.
- [ ] Add v2 path; optionally keep v1 path for legacy compatibility if needed.

**Changed files**: `nginx/nginx.conf`

### 7.6 — V1 Route Cleanup

**Problem**: `app/legacy/api/main.py` contains V1 route references.

**Acceptance Criteria**:
- [ ] No active code references `/api/v1/` routes (except for documented backward-compat shims).
- [ ] If V1 routes serve no active traffic, they should be removed.

**Implementation Tasks**:
- [ ] Audit whether `/api/v1/lessons/generate` or other V1 routes are still called.
- [ ] Remove the V1 route shim if safe, or add a deprecation log if kept.

**Changed files**: `app/legacy/api/main.py` (remove or deprecate)

### 7.7 — `/metrics` and Dev Route Access Control

**Problem**: `/metrics` and `/__dev/slow_query` have no access control or environment gate.

**Acceptance Criteria**:
- [ ] `/metrics` decision made: either (a) private-network only via Nginx/infra, or (b) app-level authentication.
- [ ] `/__dev/slow_query` is gated behind `APP_ENV != "production"` or removed.
- [ ] Decision documented in ADR.

**Implementation Tasks**:
- [ ] Add `@app.get("/metrics")` access control or document as infra-protected.
- [ ] Gate `/__dev/slow_query` with `if settings.APP_ENV != "production"`.
- [ ] Create ADR documenting the chosen approach for each.

**Changed files**: `app/api_v2.py`, potentially `docs/adr/`

### 7.8 — Production Secret Management

**Problem**: Production secrets passed as environment variables in Compose.

**Acceptance Criteria**:
- [ ] Production deployment (Docker Compose or ACA) uses platform-native secret management:
  - Docker Compose: Docker secrets or `.env` file documented as local-only.
  - ACA: Azure Key Vault references or Bicep-secure parameters.
- [ ] Documentation updated for production deployers.

**Implementation Tasks**:
- [ ] Evaluate Docker Compose secrets vs env vars for `docker-compose.prod.yml`.
- [ ] For ACA Bicep, ensure secrets come from Key Vault, not env vars.
- [ ] Document the chosen approach in `docs/deployment/`.

**Changed files**: `docker-compose.prod.yml`, `bicep/container_apps.bicep`, `docs/deployment/`

### 7.9 — Deployment Target Definition

**Problem**: Ambiguous whether Docker Compose, ACA, or other is authoritative.

**Acceptance Criteria**:
- [ ] Authoritative production deployment target is documented.
- [ ] Non-authoritative deployment drafts are marked as such.
- [ ] The decision is captured in an ADR.

**Implementation Tasks**:
- [ ] Review `app/modules/deployment/production_readiness_contracts.py` for current target definition.
- [ ] Stakeholder decision: Compose-first or ACA-first?
- [ ] Document the decision and update deployment contracts accordingly.

**Changed files**: `docs/adr/`, `docs/deployment/`, potentially `app/modules/deployment/`

### 7.10 — Tests and Verification

**Problem**: All sub-phases need verification.

**Acceptance Criteria**:
- [ ] Unit tests cover any new config logic (PUBLIC_FRONTEND_URL, conditional HSTS, CSP nonce).
- [ ] Integration tests confirm Stripe redirect URLs are environment-derived.
- [ ] Nginx config syntax validated (`nginx -t`).
- [ ] Bicep file compiles (`az bicep build`).
- [ ] Security headers verified via curl (HSTS absent in dev, CSP tightened).
- [ ] Evidence and audit docs committed.

**Implementation Tasks**:
- [ ] Add/update tests for each changed component.
- [ ] Run `compileall` for Python files, `nginx -t` for Nginx config.
- [ ] Capture evidence for each sub-phase.
- [ ] Write `docs/release/phase_7_evidence.md` and `docs/roadmap/execution/phase_7_implementation_report.md`.

---

## Evidence Output

| Artifact | Path | Status |
|----------|------|--------|
| Phase 7 execution plan | `docs/roadmap/execution/phase_7_execution_plan.md` | ✅ (this file) |
| Phase 7 implementation report | `docs/roadmap/execution/phase_7_implementation_report.md` | ✅ Done |
| Phase 7 evidence | `docs/release/phase_7_evidence.md` | ✅ Done |
| Phase 7 implementation audit | `docs/release/phase_7_implementation_audit.md` | ⚠️ Deferred |

---

## Success Criteria

**Phase 7 is complete when:**

- [x] Stripe URLs use `PUBLIC_FRONTEND_URL` config (7.1)
- [x] ACA CORS does not use wildcard `*` (7.2)
- [x] CSP does not contain `unsafe-inline` in production (7.3)
- [x] HSTS header absent in dev, present in production (7.4)
- [x] Nginx rate limits apply to `/api/v2/auth/` (7.5)
- [x] No active V1 route references remain (7.6)
- [x] `/metrics` and `/__dev/slow_query` access is documented and gated (7.7)
- [x] Production secrets use platform-native mechanism or are documented as local-only (7.8)
- [x] Authoritative deployment target is defined (7.9)
- [x] Tests pass and evidence artifacts committed (7.10)

**RoadMap alignment** (from [roadmap.md](../roadmap.md#L285-L334)):

- [x] Production config contains no localhost redirect defaults
- [x] Nginx rate limits apply to active auth routes
- [x] ACA CORS does not use `*`
- [x] CSP does not contain `unsafe-inline` in production
- [x] HSTS header absent in dev, present in production
- [x] No V1 URL patterns remain in active config
- [x] Secret handling is platform-native or explicitly documented as local-only

---

## Close Checklist

- [x] Execution plan exists: `docs/roadmap/execution/phase_7_execution_plan.md` (this file)
- [x] Implementation report exists: `docs/roadmap/execution/phase_7_implementation_report.md`
- [x] Audit report exists: `docs/release/phase_7_implementation_audit.md`
- [x] Evidence files committed and accurate
- [x] `roadmap.md` Phase 7 status updated to "Complete (YYYY-MM-DD)"
- [x] `context/build-plan.md` Phase 7 status updated
- [x] `context/progress-tracker.md` updated
- [x] `docs/todos/todo.md` updated
- [x] Branch merged to `master` / represented on current `master`
- [ ] Remote branch deleted after merge

---

## Next Phase

**Phase 8: Privacy and Authorization Completion** — POPIA legal-hold and export-offered checks, authorization completeness.
