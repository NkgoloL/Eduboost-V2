# Next Execution Queue After AUTH-REFRESH-DB-EVIDENCE-001 / code_2711_2750

## Recommended next action

Run the real DB proof, then attach evidence:

```bash
AUTH_REFRESH_DB_DSN_LABEL="staging-postgres" \
AUTH_REFRESH_DB_TEST_COMMAND="AUTH_REFRESH_DB_PROOF_DSN=... make auth-refresh-db-proof-release-check" \
AUTH_REFRESH_DB_TEST_RESULT="passed" \
AUTH_REFRESH_DB_REFRESH_PERSISTENCE_RESULT="passed" \
AUTH_REFRESH_DB_LOGOUT_REVOCATION_RESULT="passed" \
AUTH_REFRESH_DB_REVOKE_ALL_RESULT="passed" \
AUTH_REFRESH_DB_REUSE_DETECTION_RESULT="passed" \
AUTH_REFRESH_DB_EVIDENCE_URL="https://github.com/NkgoloL/Eduboost-V2/actions/runs/<run_id>" \
AUTH_REFRESH_DB_COMMIT_SHA="<sha>" \
AUTH_REFRESH_DB_VERIFIED_BY="<name>" \
AUTH_REFRESH_DB_DATE_VERIFIED="YYYY-MM-DD" \
make auth-refresh-db-evidence-attach
```

Then run:

```bash
make auth-refresh-db-evidence-release-check
make final-gate-refresh
```
