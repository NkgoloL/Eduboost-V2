# Legacy Compatibility — Route Classification

**Status:** Active reference document
**Relates to:** PR-002R §1.4

---

## V2 Production Routes

The following route prefixes are registered on `app.api_v2:app` and are
considered V2 production surfaces.  All endpoints under these prefixes must:

- Return responses wrapped in `ApiEnvelope[T]`.
- Use canonical error codes from `app/core/exceptions.py`.
- Appear in `docs/route_inventory.md` and `docs/openapi.json`.

| Prefix | Router module | OpenAPI tag |
|---|---|---|
| `/api/v2/auth` | `app.api_v2_routers.auth` | `auth` |
| `/api/v2/learners` | `app.api_v2_routers.learners` | `learners` |
| `/api/v2/lessons` | `app.api_v2_routers.lessons` | `lessons` |
| `/api/v2/study-plans` | `app.api_v2_routers.study_plans` | `study_plans` |
| `/api/v2/diagnostics` | `app.api_v2_routers.diagnostics` | `diagnostics` |
| `/api/v2/gamification` | `app.api_v2_routers.gamification` | `gamification` |
| `/api/v2/onboarding` | `app.api_v2_routers.onboarding` | `onboarding` |
| `/api/v2/parents` | `app.api_v2_routers.parents` | `parents` |
| `/api/v2/billing` | `app.api_v2_routers.billing` | `billing` |
| `/api/v2/consent` | `app.api_v2_routers.consent` | `consent` |
| `/api/v2/consent-renewal` | `app.api_v2_routers.consent_renewal` | `consent` |
| `/api/v2/popia` | `app.api_v2_routers.popia` | `popia` |
| `/api/v2/jobs` | `app.api_v2_routers.jobs` | `jobs` |
| `/api/v2/system` and `/health`, `/ready` | `app.api_v2_routers.system` | `ops` |

> **Shorthand prefixes:** the same routers are also mounted under `/v2/*` for
> reverse-proxy convenience.  Both prefixes resolve to the same handlers.

---

## Legacy-Only Routes (forbidden in production)

The following prefixes are **not** mounted on `app.api_v2:app`.  They existed
in the V1 runtime (`app.legacy.api.main:app`) and must not reappear in V2.

| Prefix | Reason excluded |
|---|---|
| `/api/v1/*` | Replaced by `/api/v2/*` |
| `/v1/*` | Replaced by `/v2/*` |
| `/legacy/*` | Archived; import shim only |
| `/admin/*` (V1 style) | Not reimplemented in V2; use direct DB tools |

Tests that enforce these exclusions:

- `tests/unit/test_api_v2_router_contract.py::test_no_v1_routers_included`
- `tests/test_entrypoints.py::test_legacy_routes_not_exposed_by_v2_app`

---

## Compatibility Shims

| Module | Delegates to | Purpose |
|---|---|---|
| `app.api.main` | `app.api_v2:app` | Drop-in import alias for tools/scripts that expect the old path |
| `app.legacy.api.main` | Shim object (not V2 app) | Retained for legacy test fixtures; **not** used in production |

The shim in `app.api.main` must:
- Expose the same `title` and `/health` + `/ready` routes as V2.
- Not add any routes of its own.
- Be tested by `tests/test_entrypoints.py`.

---

## CI Enforcement

The `legacy-route-guard` CI job runs on every push/PR that touches `app/` and
will fail if:
1. Any V1/legacy prefix appears in `app.api_v2:app`'s route table.
2. `scripts/check_runtime_entrypoints.py` exits non-zero.

---

## Migration Notes for Future Router Changes

1. New routes go under `/api/v2/<resource>` — never under `/v1/`.
2. Any route that needs to be retired must be removed from the router and the
   removal documented in `CHANGELOG.md`.
3. Breaking changes (removed or renamed routes) require a version bump per
   `docs/api_versioning_policy.md`.
