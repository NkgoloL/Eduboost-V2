# Next Execution Queue After DB-ROLLBACK-001R / code_3311_3350

## Recommended next backend/runtime batches

1. `JWT-001R / code_3351_3390` — attach staging/production secret provisioning and rotation evidence.
2. `ARQ-001R / code_3351_3390` — prove live Redis worker enqueue/dequeue.
3. `IMAGE-SBOM-001R / code_3351_3390` — attach backend image digest and SBOM evidence.
4. `SECURITY-ARTIFACTS-001R / code_3351_3390` — capture Trivy/Bandit/gitleaks reports as release artifacts.

## Accepted evidence reference

```bash
DB_ROLLBACK_ACCEPT=1 \
DB_ROLLBACK_SOURCE_DATABASE_URL='<staging/source postgres URL>' \
DB_ROLLBACK_RESTORE_DATABASE_URL='<disposable restore postgres URL>' \
DB_ROLLBACK_RUN_ID='<successful GitHub Actions run id>' \
DB_ROLLBACK_RUN_DRILL=1 \
make db-backup-restore-rollback-release-check
```
