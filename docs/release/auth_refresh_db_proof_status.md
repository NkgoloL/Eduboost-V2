# Auth Refresh DB Proof Status

Generated at: `2026-05-20T23:54:20Z`
Commit: `aa1e1e883fe9ea07116238229dca4694c7216d3a`

**Status:** `auth-refresh-db-proof-external-blocked`
**DSN present:** `False`
**Pytest return code:** `None`

## Evidence fields

| Field | Value | Valid | Reason |
|---|---|---:|---|
| `Database DSN label` | `staging-postgres` | True | ok |
| `Test command` | `AUTH_REFRESH_DB_PROOF_DSN="$REAL_AUTH_REFRESH_DB_PROOF_DSN" make auth-refresh-db-proof-release-check` | True | ok |
| `Test result` | `passed` | True | ok |
| `Refresh persistence result` | `passed` | True | ok |
| `Logout revocation result` | `passed` | True | ok |
| `Revoke-all result` | `passed` | True | ok |
| `Reuse detection result` | `passed` | True | ok |
| `Evidence URL` | `https://github.com/NkgoloL/Eduboost-V2/actions/runs/REAL_RUN_ID` | True | ok |
| `Commit SHA` | `aa1e1e883fe9ea07116238229dca4694c7216d3a` | True | ok |
| `Verified by` | `Nkgolo Lebelo` | True | ok |
| `Date verified` | `2026-05-21` | True | ok |

## Pytest summary

```text
AUTH_REFRESH_DB_PROOF_DSN not set; DB proof not executed
```

## Blockers

- AUTH_REFRESH_DB_PROOF_DSN is not set
- DB pytest did not pass

## No false-closure rules

- Skipped DB tests are not proof.
- Mock-only tests are not DB proof.
- AUTH_REFRESH_DB_PROOF_DSN must be explicit.
- Release mode requires accepted DB proof evidence.
