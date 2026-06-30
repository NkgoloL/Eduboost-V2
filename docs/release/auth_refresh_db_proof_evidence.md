# Auth Refresh DB Proof Evidence

**Item:** AUTH-REFRESH-DB-PROOF-001

**Database DSN label:** github-actions-postgres-service

**Test command:** python -m pytest -c pytest.ini tests/integration/test_auth_refresh_db_proof.py -q --no-cov --tb=short -rs

**Test result:** passed

**Refresh persistence result:** passed

**Logout revocation result:** passed

**Revoke-all result:** passed

**Reuse detection result:** passed

**Evidence URL:** https://github.com/NkgoloL/Eduboost-V2/actions/runs/26226114014

**Commit SHA:** 84ace987e1f577fcf647fbe105f78680003c5aaa

**Verified by:** github-actions

**Date verified:** 2026-05-21

## Required proof

- Refresh token is persisted after login/refresh flow.
- Logout invalidates the active refresh token.
- Revoke-all invalidates all user refresh tokens.
- Reuse of an already-consumed refresh token is rejected.
- Evidence URL points to CI/staging logs or an auditable proof artifact.

## No false-closure rule

This file is not proof while any required field is pending or placeholder-like.
