# PR-003 Auth/session/RBAC hardening — implementation summary

## Scope

This patch hardens the V2 authentication/session baseline while keeping changes focused on security-critical behavior:

- password/passphrase policy
- bcrypt cost configuration
- refresh-token family rotation and reuse detection
- session metadata inventory
- logout-all refresh-token cleanup
- auth route rate-limit coverage expansion
- refresh-cookie policy test
- role catalogue and object-level learner authorization helpers
- learner read/mastery route object-level authorization

## Runtime changes

### Passwords

- Added `app.core.password_policy.validate_password_strength`.
- Registration now uses the centralized password policy.
- bcrypt hashing now uses `settings.PASSWORD_BCRYPT_ROUNDS`, default `12`.
- `verify_password` now returns `False` for malformed hashes instead of raising.

### Refresh tokens

- Refresh tokens now include a `family` claim.
- Refresh tokens are stored hashed at rest.
- Refresh tokens are single-use.
- Refresh-token reuse revokes the token family.
- Session metadata is indexed by user and exposed through `/api/v2/auth/sessions` without returning token values.
- `/api/v2/auth/revoke-all` now clears indexed refresh-token metadata for the current user.

### Auth routes

- Fixed missing `FourthEstateService` import in the auth router.
- Added failed-login audit events.
- Added rate limiting to `/api/v2/auth/refresh`.
- Registration and login now use `settings.RATE_LIMIT_AUTH`.
- Dev bootstrap password was updated to satisfy the stricter password policy.

### RBAC and authorization

- Added `app.core.rbac.OperationalRole` to document persisted and reserved roles.
- Added `app.core.authorization.assert_can_access_learner`.
- Wired object-level authorization into learner read and mastery routes.

## Documentation

Added `docs/security/auth_session_policy.md` covering:

- password policy
- access-token TTL
- refresh-token TTL and family rotation
- cookie policy
- persisted/reserved roles
- learner object-level authorization baseline
- Redis persistence caveat

## Tests added

- `tests/unit/test_password_policy.py`
- `tests/unit/test_refresh_token_rotation.py`
- `tests/unit/test_authorization_policy.py`
- `tests/unit/test_auth_cookie_policy.py`

## Validation

Passed:

```bash
python -m py_compile \
  app/core/password_policy.py \
  app/core/security.py \
  app/core/refresh_tokens.py \
  app/core/authorization.py \
  app/core/rbac.py \
  app/api_v2_routers/auth.py \
  app/api_v2_routers/learners.py \
  tests/unit/test_password_policy.py \
  tests/unit/test_refresh_token_rotation.py \
  tests/unit/test_authorization_policy.py
```

Passed:

```bash
PYTHONPATH=. pytest \
  tests/unit/test_password_policy.py \
  tests/unit/test_refresh_token_rotation.py \
  tests/unit/test_authorization_policy.py \
  tests/unit/test_auth_cookie_policy.py \
  --no-cov -q
```

Result: `15 passed`.

Generated updated OpenAPI schema:

```bash
PYTHONPATH=. python scripts/generate_openapi.py
```

## TODO items completed

- TODO-069
- TODO-070
- TODO-073
- TODO-076
- TODO-077
- TODO-078
- TODO-079
- TODO-082
- TODO-083
- TODO-085

## TODO items left partial

- TODO-068: email verification/password reset E2E remains pending.
- TODO-071: reset/verification endpoints need rate limits once implemented.
- TODO-080: Redis persistence/failover must be verified in the deployment environment.
- TODO-084: object-level tests are started, but every actor/resource case is not complete.
- TODO-086: every-router policy coverage remains pending.
- TODO-087: policy helpers exist, but full PBAC migration is future work.

## Follow-up recommendations

Next PR should be `PR-004 POPIA consent/data-rights/audit`, because auth/session hardening now creates a safer substrate for learner-data workflows.
