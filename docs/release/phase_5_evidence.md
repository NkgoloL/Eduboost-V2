# Phase 5 Evidence

Date: 2026-06-10
Refresh: 2026-06-14

## Static Checks

- `python3 scripts/verify_migration_graph.py` passed.
- `python3 scripts/validate_schema_integrity.py` passed.
- `python3 -m compileall -q alembic app scripts` passed.

Fresh 2026-06-14 output:

```text
python3 scripts/verify_migration_graph.py
Migration graph OK: 34 revisions, head=20260609_0800_practice_sessions

python3 scripts/validate_schema_integrity.py
Schema integrity OK

python3 -m compileall -q alembic app scripts
# passed
```

## Migration Graph

Observed head revision:

- `20260609_0800_practice_sessions`

`alembic current --verbose` reported a single head revision on the disposable PostgreSQL database:

- Head: `20260609_0800_practice_sessions`
- Parent: `f2faf5aa12fd`

## Live Database Smoke

Disposable database:

- PostgreSQL container on `localhost:5433`
- DSN: `postgresql+asyncpg://eduboost:testpassword@localhost:5433/eduboost_test`

Validation run:

- `make migration-smoke` passed end to end.
- The smoke test completed upgrade, downgrade `-1`, re-upgrade, and idempotency verification successfully.

Fresh 2026-06-14 smoke refresh:

```text
DATABASE_URL=postgresql+asyncpg://eduboost:testpassword@127.0.0.1:55433/eduboost_test \
SYNC_DATABASE_URL=postgresql://eduboost:testpassword@127.0.0.1:55433/eduboost_test \
make migration-smoke

Current version:
20260609_0800_practice_sessions (head)
Testing rollback (downgrade -1)...
Re-upgrading to head...
Running idempotency check...
Idempotency check PASSED — no migrations were applied on second run.
Migration smoke test PASSED.
```

The smoke target requires `DATABASE_URL`; running it without a database URL fails fast before any migration work.

## Notes

- `run_startup_migrations()` was removed from `app/api_v2.py`, so API startup no longer performs schema repair DDL.
- CI now includes blocking schema drift checks for migration graph and schema integrity.
