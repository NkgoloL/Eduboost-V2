# Next Execution Queue After STAGING-SMOKE-WORKFLOW-001 / code_2911_2950

## Required external action

Run the `Staging Smoke` GitHub Actions workflow with a real HTTPS staging URL.

After it passes, attach evidence with:

```bash
STAGING_SMOKE_RUN_ID=<numeric_successful_staging_smoke_run_id> \
STAGING_SMOKE_BASE_URL=https://<real-staging-host> \
STAGING_SMOKE_TEST_COMMAND='python scripts/staging_smoke_probe.py' \
STAGING_SMOKE_RESULT=passed \
STAGING_SMOKE_HEALTHCHECK_RESULT=passed \
STAGING_SMOKE_API_RESULT=passed \
bash temp/code_2911_2950/code_2911_2950_staging_smoke_evidence_repair.sh
```

## Remaining blocker themes

- STAGING-001 remains external-blocked until accepted run evidence is attached.
- Legal/security/content approvals remain external-blocked.
- JWT, ARQ, diagnostics, lesson auth, and diagnostic scoring evidence remain open.
