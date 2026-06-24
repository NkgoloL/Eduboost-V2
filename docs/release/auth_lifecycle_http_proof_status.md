# Auth Lifecycle HTTP Route Proof Status

Generated at: `2026-06-24T11:30:23Z`
Commit: `f5d72b8380da6403371ea91f6c8298626ba07aa1`

**Status:** `auth-lifecycle-http-route-proof-passing`
**Router import OK:** `True`
**Synthetic app registration OK:** `True`

| Function | Service method | Source route | Registered | Service method | Dependency | Delegates | Methods | Paths | Passed |
|---|---|---:|---:|---:|---:|---:|---|---|---:|
| `register` | `register` | True | True | True | True | True | `POST` | `/auth/register` | True |
| `login` | `login` | True | True | True | True | True | `POST` | `/auth/login` | True |
| `refresh` | `refresh` | True | True | True | True | True | `POST` | `/auth/refresh` | True |
| `logout` | `logout` | True | True | True | True | True | `POST` | `/auth/logout` | True |
| `revoke_all_tokens` | `revoke_all_tokens` | True | True | True | True | True | `POST` | `/auth/revoke-all` | True |

## Blockers

- None

## No false-closure rules

- Route registration/source proof does not prove database-backed auth semantics.
- Cookie persistence and refresh-token revocation semantics remain separate runtime concerns.
- This proof does not approve beta release.
