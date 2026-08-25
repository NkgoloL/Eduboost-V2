# Auth Refresh DB Proof Status

Generated at: `2026-08-01T20:59:08Z`
Commit: `66323711cba9ebc39919f32491c707aeb92e5e58`

**Status:** `auth-refresh-db-proof-external-blocked`
**DSN present:** `False`
**Pytest return code:** `None`

## Evidence fields

| Field | Value | Valid | Reason |
|---|---|---:|---|
| `Database DSN label` | `github-actions-postgres-service` | True | ok |
| `Test command` | `python -m pytest -c pytest.ini tests/integration/test_auth_refresh_db_proof.py -q --no-cov --tb=short -rs` | True | ok |
| `Test result` | `passed` | True | ok |
| `Refresh persistence result` | `passed` | True | ok |
| `Logout revocation result` | `passed` | True | ok |
| `Revoke-all result` | `passed` | True | ok |
| `Reuse detection result` | `passed` | True | ok |
| `Evidence URL` | `https://github.com/NkgoloL/Eduboost-V2/actions/runs/26226114014` | True | ok |
| `Commit SHA` | `84ace987e1f577fcf647fbe105f78680003c5aaa` | True | ok |
| `Verified by` | `github-actions` | True | ok |
| `Date verified` | `2026-05-21` | True | ok |

## Pytest summary

```text
DB pytest not requested
```

## Blockers

- AUTH_REFRESH_DB_PROOF_DSN is not set

## No false-closure rules

- Skipped DB tests are not proof.
- Mock-only tests are not DB proof.
- AUTH_REFRESH_DB_PROOF_DSN must be explicit.
- Release mode requires accepted DB proof evidence.
