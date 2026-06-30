# No False-Closure Status After AUTH-REPO-001 / code_1271_1310

**Status:** production repository auth fixture proof added at integration-fixture level.

## Proven

- AuthApplicationService resolves canonical session-bound ORM repositories before legacy/direct repository shims.
- Auth runtime context resolves canonical session-bound ORM repositories before legacy/direct repository shims.
- Register/login/refresh repository paths are exercised against actual project ORM models using an SQLAlchemy AsyncSession fixture.
- Duplicate registration, wrong-password rejection, persisted password hash verification, and refresh learner-scope recovery are covered.

## Not claimed

- Live Postgres migration proof.
- Redis-backed refresh-token cache proof.
- Full staging auth flow proof.
- Production secret rotation evidence.
