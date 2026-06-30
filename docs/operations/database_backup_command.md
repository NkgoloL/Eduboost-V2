# Database Backup Command

## Purpose

`python3 scripts/run_database_backup.py --dry-run` provides a non-destructive
backup command contract for CI.

## Required Inputs

- `DATABASE_URL`
- `BACKUP_ENCRYPTION_KEY`
- `AZURE_STORAGE_CONNECTION_STRING`
- `AZURE_STORAGE_CONTAINER`

## CI Behavior

CI uses dry-run mode only. The command validates required inputs and renders a
backup plan without dumping data.

## Command

```bash
make database-backup-dry-run
```

## Verification

```bash
pytest -c pytest.ini tests/unit/test_database_backup_command.py -q --no-cov
```
