# Auth Boundary Evidence

This document indexes the current authentication, session, RBAC, rate-limit,
and object-authorization evidence. It does not claim public-beta readiness for
every auth path; router-specific and abuse-path checks still need item-level
reconciliation before TODO rollups can become `[x]`.

## Authentication

- Router: `app/api_v2_routers/auth.py`
- Service: `app/modules/auth/service.py`
- Tests: `tests/unit/test_v2_auth.py` and `tests/integration/test_auth_refresh.py`

## Token Rotation And Revocation

- Refresh tokens: `app/core/refresh_tokens.py`
- Revocation store: `app/core/token_revocation.py`
- Tests: `tests/unit/test_refresh_token_rotation.py` and
  `tests/unit/test_token_denylist.py`

## Cookie Policy

- Policy doc: `docs/security/auth_session_policy.md`
- Tests: `tests/unit/test_auth_cookie_policy.py`

## RBAC

- Implementation: `app/core/rbac.py`
- Tests: `tests/integration/test_rbac.py`

## Object Authorization

- Implementation: `app/security/object_authorization.py`
- Evidence docs: `docs/security/object_authorization.md` and
  `docs/security/authorization_dependencies.md`
- Tests: `tests/unit/test_object_authorization.py` and
  `tests/unit/test_authorization_policy.py`

## Rate Limiting

- Implementation: `app/core/rate_limit.py`
- Tests: `tests/integration/test_rate_limits.py`

## Aggregate Check

```bash
make auth-boundary-check
```

## Verification Gaps

- Login/signup/password-reset abuse paths still need complete negative tests.
- Redis outage behavior for token revocation remains part of the DR batch.
- Branch protection must require this check before it can support release
  promotion.
