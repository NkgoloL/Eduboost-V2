# Auth Refresh DB Evidence Status

Generated at: `2026-06-12T17:31:42Z`
Commit: `b33e49720860a084e7a7c42ead1b620cb859e64f`

**Status:** `auth-refresh-db-evidence-accepted`
**Accepted:** `True`

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

## Blockers

- None

## No false-closure rules

- Accepted metadata does not independently verify remote URLs.
- Accepted metadata must still correspond to real DB-backed test logs.
- Placeholder-like accepted evidence is reclassified to external-blocked.
- This evidence gate does not approve beta release.
