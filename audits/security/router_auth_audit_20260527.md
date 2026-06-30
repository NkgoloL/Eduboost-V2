# Phase 1 — T103 — Router Placeholder Auth Audit

**Branch:** `remediation/phase0-phase1`
**Date:** 2026-05-27
**Tool:** AST-based static analysis (`/tmp/audit_router_auth.py`) + manual review
**Scope:** All `app/api_v2_routers/*.py` files (30 router modules)

---

## Methodology

1. Automated scan: parse every router file with `ast` and flag every route
   function (decorated with `@router.{get,post,put,patch,delete,head}`) that
   does **not** have a `Depends(...)` parameter in its function signature.
2. Manual review of every flagged route to determine whether the lack of
   auth is intentional (e.g., public health endpoints, webhooks) or an
   omission.
3. Cross-check router-level `dependencies=[Depends(...)]` on `APIRouter`
   constructors, which the AST scan does not catch (function-level only).

---

## Findings summary

| Category | Count | Details |
|---|---|---|
| **False positives** (router-level auth) | 2 routers | `admin_etl.py`, `content_factory.py` both declare `dependencies=[Depends(require_admin)]` on the router. All their routes are protected. |
| **Intentionally public** | 2 routers | `system.py` (diagnostic/info endpoints), `api_v2.py` (root health + root endpoint). |
| **Placeholder auth found** | 0 | No `TODO auth`, `fake_auth`, `mock_auth`, `bypass_auth`, or `skip_auth` patterns found in production routers after removing the stale `popia.py` TODO. |
| **Missing auth (genuine finding)** | 0 | No production route was found that should be protected but isn't. |

---

## Detailed file-by-file

### `system.py` — intentionally public diagnostic routes

```python
@router.get("/health")       # get_health()      -> public OK
@router.get("/pillars")      # get_pillars()     -> public OK (system architecture info)
@router.get("/schema-status") # get_schema_status() -> public OK (schema version info)
@router.get("/capabilities") # get_capabilities()  -> public OK (feature flags)
```

These are diagnostic/read-only endpoints. They do not expose learner PII,
financial data, or mutable state. The `/system/health` route is distinct
from the main `/health` liveness probe but serves the same purpose for
system-level diagnostics.

**No action required.**

### `api_v2.py` — main app endpoints (not a router module)

```python
@app.get("/health")   # health()  -> public OK (liveness probe)
@app.get("/ready")    # ready()   -> public OK (readiness probe)
@app.get("/")         # root()    -> public OK (API info)
```

These are the canonical health and root endpoints defined directly on the
FastAPI app object, not on a router. They are intentionally public by
contract (see `docs/operations/health.md`).

**No action required.**

### `admin_etl.py` — router-level admin auth

```python
router = APIRouter(
    ...
    dependencies=[Depends(require_admin)],
)
```

Every route in this router (`/status`, `/documents`, `/review-queue`,
`/metrics`, etc.) inherits `require_admin`. The AST scan flagged these as
"public" because the auth is on the router constructor, not on each
individual route function.

**No action required.**

### `content_factory.py` — router-level admin auth

```python
router = APIRouter(
    ...
    dependencies=[Depends(require_admin)],
)
```

Same pattern as `admin_etl.py`. All content-factory admin routes are
protected by `require_admin` at the router level.

**No action required.**

### `billing.py` — mixed auth (intentional)

```python
@router.post("/checkout", ...)
async def create_checkout(current_user: dict = Depends(require_parent_or_admin)):

@router.post("/webhook")
async def stripe_webhook(request: Request, ...):
```

- `/checkout` requires `require_parent_or_admin` — correct.
- `/webhook` has no auth dependency — **intentionally public**. Stripe
  webhooks are called by Stripe's servers, not by authenticated EduBoost
  users. The webhook handler validates the Stripe signature header
  (`stripe-signature`) cryptographically. No session/JWT auth is
  applicable.

**No action required.**

---

## T102 — POPIA router auth fix (applied in this PR)

### Finding

`app/api_v2_routers/popia.py` contained a TODO comment:

```python
# TODO: replace with real auth dependency that injects actor_id from JWT
```

### Investigation — dependency chain evidence

**Dependency used:** `current_user = Depends(get_current_user)`  
`get_current_user` is defined in `app/core/security.py:93`. It uses
`HTTPBearer` to extract the `Authorization: Bearer <token>` header, calls
`decode_token()` which uses `jwt_keyring.py` for verification, and returns a
dict of JWT claims (the "principal").

**Principal object/type:** `dict[str, Any]` containing at minimum:
- `sub` (subject UUID string)
- `role` (UserRole enum value)
- `exp`, `iat`, `jti`, `type` (standard JWT claims)

**401 behavior:** `get_current_user` raises `HTTPException(status_code=401)`
when:
- No `Authorization` header is present.
- Token decode fails (expired, invalid signature, malformed).
- Token type is not `"access"` (e.g., a refresh token is presented).
- Token JTI is in the Redis revocation list.
- User's global revocation epoch is set and token predates it.

**403 behavior:** `_enforce_popia_learner_write(current_user, learner_id)`
(defined in `app/api_v2_deps/consent_lifecycle.py:55`) dynamically loads
`require_learner_write_for_current_user` from `app/security/dependencies.py:263`.
This builds an `Actor` from the JWT claims and calls `can_access_learner()`
with `Permission.WRITE`. If the actor is not a guardian of the learner, an
admin, or an educator with an assignment, it raises `HTTPException(status_code=403)`.

**Audit actor propagation:** `_authenticated_actor_id(current_user)`
(`app/api_v2_deps/consent_lifecycle.py:39`) extracts the actor ID for POPIA
audit events by reading `sub`, `id`, or `user_id` from the JWT claims dict.
This actor_id is passed to every ConsentService mutation (`grant`, `deny`,
`withdraw`, `renew`) as the `actor_id` parameter and is stored in the
`ConsentRecord.audit_actor_id` column.

**Conclusion:** The TODO was stale — the auth it described was already fully
implemented with attributable actor identity, 401/403 enforcement, and POPIA
audit propagation. The TODO comment has been removed in this PR.

### Changes applied

- `app/api_v2_routers/popia.py` — removed stale TODO comment. No functional
  change; auth was already wired.

---

## Remaining placeholder patterns (post-fix)

After removing the stale `popia.py` TODO, a broad `grep` for auth-related
placeholder terms returns zero hits in production router code:

```bash
grep -rni "placeholder.*auth\|fake.*auth\|mock.*auth\|bypass.*auth\|skip.*auth\|TODO.*auth" app/api_v2_routers/*.py
# no output
```

**AC met:** Zero placeholder auth patterns in production-serving routers.

---

## Recommendations

1. **Add a CI gate** (Phase 1 J): a lightweight script that fails if any
   production router file contains `TODO.*auth`, `placeholder`, or
   `fake_auth`. This can piggyback on the existing `observability_check.yml`
   or a new `security_audit.yml` workflow.
2. **Document router-level auth** in `docs/operations/auth.md` (future task):
   explain which routers use router-level `dependencies=` vs
   function-level `Depends(...)`, and why.
3. **Consider adding auth to `system.py`** if `/pillars`, `/schema-status`,
   or `/capabilities` begin to expose implementation details that could aid
   an attacker. Currently they are safe as public read-only endpoints.
