# Auth Lifecycle Controlled Semantic Proof Status

Generated at: `2026-08-01T20:58:38Z`
Commit: `66323711cba9ebc39919f32491c707aeb92e5e58`

**Status:** `auth-lifecycle-controlled-semantic-proof-passing`

## Route semantic proof

| Function | Delegates | Has auth_service dependency | Passed context keywords | Prohibited route calls | Passed |
|---|---:|---:|---|---|---:|
| `register` | True | True | `auth_runtime, body, db, request, response` | `-` | True |
| `login` | True | True | `auth_runtime, body, db, request, response` | `-` | True |
| `refresh` | True | True | `auth_runtime, body, cookie_refresh, db, request, response` | `-` | True |
| `logout` | True | True | `cookie_refresh, current_user, db, response` | `-` | True |
| `revoke_all_tokens` | True | True | `cookie_refresh, current_user, db, response` | `-` | True |

## Controlled cookie proof

| Method | Callable | Deleted cookies | Returned mapping | Detail | Passed |
|---|---:|---|---:|---|---:|
| `logout` | True | `refresh_token` | True | controlled fallback invocation completed | True |
| `revoke_all_tokens` | True | `refresh_token` | True | controlled fallback invocation completed | True |

## Blockers

- None

## No false-closure rules

- Controlled fallback invocation does not prove production repository revocation.
- This does not prove refresh-token reuse detection against Redis/Postgres.
- This does not prove cookie behavior in a real browser/client.
- This proof does not approve beta release.
