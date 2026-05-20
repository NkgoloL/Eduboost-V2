# Auth Repository Fixture Proof Report

Generated at: `2026-05-19T19:36:21Z`

**Status:** implemented

## Proven

- AuthApplicationService resolves canonical session-bound ORM repositories first.
- Auth runtime context resolves canonical session-bound ORM repositories first.
- Register/login/refresh repository paths are exercised against actual project ORM models in an AsyncSession fixture.
- Guardian learner scope is recovered from the actual learner repository path.

## Not claimed

- Live Postgres migration proof.
- Redis-backed refresh-token cache proof.
- Staging auth flow proof.
- Production secret rotation evidence.
