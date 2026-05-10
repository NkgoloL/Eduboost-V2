# Database Backup Integrity Check

## Purpose

This check validates that the generated backup manifest records the minimum
integrity evidence needed for release review.

## Required Evidence

- backup artifact ID
- retention period
- encrypted status
- restore drill linkage
- backup dry-run command reference

## Command

```bash
make database-backup-integrity-check
```

## Verification

```bash
pytest -c pytest.ini tests/unit/test_database_backup_integrity.py -q --no-cov
```
