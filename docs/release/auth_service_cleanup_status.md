# Auth Service Cleanup Status

Generated at: `2026-05-20T15:13:26Z`
Commit: `629906580bd58863ec4a55ab9cdbe93f600f3951`

**Status:** `auth-service-monkeypatch-cleaned-route-delegation-pending`

## Service methods present

- `create_dev_session`
- `login`
- `logout`
- `refresh`
- `register`
- `revoke_all_tokens`

## Route delegation

- Present: `-`
- Missing: `logout, revoke_all_tokens`

## Monkey patches

- None

## Blockers

- auth router does not delegate logout to auth_service.logout
- auth router does not delegate revoke_all_tokens to auth_service.revoke_all_tokens

## No false-closure rules

- No module-level `AuthApplicationService.<method> = ...` assignments may remain.
- Service method presence does not prove HTTP route semantics.
- Missing logout/revoke route delegation remains visible until repaired.
- This cleanup does not approve beta release.
