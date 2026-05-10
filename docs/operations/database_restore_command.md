# Database Restore Command

## Purpose

`python3 scripts/run_database_restore.py --dry-run --target-environment staging`
provides a non-destructive restore command contract for CI.

## Required Inputs

- `DATABASE_URL`
- `BACKUP_ENCRYPTION_KEY`

## Safety Behavior

- staging dry-run is allowed in CI
- production target is blocked unless `--allow-production-target` is passed
- restore plans must verify learner, consent, and audit event counts

## Command

```bash
make database-restore-dry-run
```

## Verification

```bash
pytest -c pytest.ini tests/unit/test_database_restore_command.py -q --no-cov
```
