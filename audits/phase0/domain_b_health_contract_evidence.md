# Phase 0 — Domain B — Health Contract Evidence

**Branch:** `remediation/phase0-phase1`
**Date:** 2026-05-27
**Scope:** T010

---

## Findings vs. TODO baseline

The TODO doc stated:

> Smoke tests expect `/health/ready`. App exposes `/health`, `/ready`,
> `/api/v2/health/deep`, `/v2/health/deep`. Docker Compose uses `/ready`.
> Render uses `/health`.

**Audit-vs-reality reconciliation:**

| Claim | Reality on `origin/master` |
|---|---|
| Smoke tests want `/health/ready` | False — no test references `/health/ready` anywhere. (`grep -r '/health/ready' .` returns zero hits.) |
| App exposes `/health`, `/ready`, `/api/v2/health/deep`, `/v2/health/deep` | True — confirmed in `app/api_v2.py` lines 290–308. |
| Docker Compose uses `/ready` | True — `docker-compose.yml`, `staging/pr_008/docker-compose*.yml` all use `/ready`. |
| Render uses `/health` | True — `render.yaml` line 10 used `/health` before T010 fix. |

**Real drift identified:**

1. `render.yaml` used `/health` (liveness) for `healthCheckPath` while every
   Docker-based environment used `/ready` (deep readiness). This meant Render
   would mark an instance healthy if the FastAPI process was alive even if the
   database or Redis were unreachable.
2. Two smoke files (`tests/smoke/test_content_factory_admin_api_smoke.py`,
   `tests/smoke/test_content_factory_startup_flags.py`) imported `from app.main
   import app`, but `app.main` does not exist. The V2 ASGI app is exported from
   `app.api_v2`. These imports caused the failures observed in T005.

---

## T010 — Align health contract

**Status:** Done.

### Canonical decision

| Path | Semantics | Status codes | Probe consumers |
|---|---|---|---|
| `/health` | Liveness | `200` always | Lightweight uptime monitors |
| `/ready` | Deep readiness (canonical) | `200`/`503` | Docker Compose, Dockerfile HEALTHCHECK, Render `healthCheckPath` |
| `/v2/health/deep` | Alias of `/ready` | `200`/`503` | Versioned API callers |
| `/api/v2/health/deep` | Alias of `/ready` | `200`/`503` | `/api/v2/`-namespaced callers |

### Changes applied

1. **`render.yaml`** — `healthCheckPath: /health` → `healthCheckPath: /ready`,
   with a comment block pointing at this doc.
2. **`tests/smoke/test_content_factory_admin_api_smoke.py`** — `from app.main
   import app` → `from app.api_v2 import app` (1 occurrence in client fixture).
3. **`tests/smoke/test_content_factory_startup_flags.py`** — `from app.main
   import app` → `from app.api_v2 import app` (4 occurrences).
4. **`docs/operations/health.md`** — created as authoritative contract document,
   enumerating all four routes, every config surface, and the change procedure.

### Validation

```text
$ .venv/bin/python -m pytest tests/smoke --no-cov -v
... [full log in audits/phase0/domain_b_smoke_after.txt] ...
============================= 32 passed in 10.44s =============================
```

- `tests/smoke/test_v2_smoke.py` — both `/health` (liveness) and `/ready`
  (readiness) cases pass.
- `tests/smoke/test_content_factory_*` — all 12 cases pass after import fix.
- No skipped, no errors.

**AC met:** App, smoke tests, Docker Compose healthcheck, and Render
`healthCheckPath` all agree on `/ready` for deep readiness and `/health` for
liveness. Full contract documented in `docs/operations/health.md`.
