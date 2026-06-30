# Next Execution Queue After DIAG-001R / code_2951_2990

## Required before closing DIAG-001

Repair the live `/api/v2/health/deep` 503 and attach accepted evidence:

```bash
DIAG_DEEP_HEALTH_ACCEPT=1 \
DIAG_DEEP_HEALTH_RUN_ID=<numeric_successful_github_actions_run_id> \
DIAG_DEEP_HEALTH_URL=https://<real-staging-host>/api/v2/health/deep \
DIAG_DEEP_HEALTH_TEST_COMMAND='<actual command that hit /api/v2/health/deep>' \
DIAG_DEEP_HEALTH_DB_RESULT=passed \
DIAG_DEEP_HEALTH_MIGRATION_RESULT=passed \
DIAG_DEEP_HEALTH_AUDIT_RESULT=passed \
DIAG_DEEP_HEALTH_SESSION_RESULT=passed \
make diag-deep-health-runtime-registry-patch
```

## Remaining blocker themes

- JWT production secret provisioning and rotation evidence.
- ARQ live Redis worker enqueue/dequeue staging evidence.
- Legal/security/content external approval metadata.
- Lesson authorization full HTTP/staging proof.
- Diagnostic scoring live DB/full scoring audit.
- EXT-GATE rollup closure after approvals are accepted.
