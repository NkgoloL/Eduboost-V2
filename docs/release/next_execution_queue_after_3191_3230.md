# Next Execution Queue After DIAG-SCORE-001R / code_3191_3230

## Recommended next backend/database batches

1. `AUDIT-WRITE-001R / code_3231_3270` — exercise a staging flow that writes `audit_events`, then verify and attach evidence.
2. `DB-ROLLBACK-001R / code_3231_3270` — add backup/restore/rollback evidence.
3. `JWT-001R / code_3231_3270` — attach production/staging secret provisioning and rotation evidence.
4. `ARQ-001R / code_3231_3270` — prove live Redis worker enqueue/dequeue.

## Acceptance reference

```bash
DIAG_SCORE_ACCEPT=1 \
DIAG_SCORE_DATABASE_URL='<live postgres URL>' \
DIAG_SCORE_ALLOW_BRIDGE_SEED=1 \
DIAG_SCORE_RUN_ID='<successful GitHub Actions run id>' \
DIAG_SCORE_TEST_COMMAND='python scripts/diagnostic_score_live_audit.py --apply-seed' \
DIAG_SCORE_SEED_RESULT=passed \
DIAG_SCORE_SCORING_RESULT=passed \
DIAG_SCORE_AUDIT_RESULT=passed \
make diagnostic-score-live-audit-release-check
```
