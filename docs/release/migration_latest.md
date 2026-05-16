# Database Migration Latest Run

**Status:** migration evidence passed
<!-- Status: migration evidence passed -->

- Captured at: `2026-05-16T18:13:36Z`
- Database URL: `postgresql+asyncpg://eduboost_user:***@localhost:5432/eduboost_test`
- Include downgrade: `False`
- JSON evidence: `/home/nkgolol/Dev/SandBox/dev/Eduboost-V2/docs/release/migration_latest.json`

| Step | Command | Return code | Passed |
|---|---|---:|---|
| alembic_current_before | `alembic current` | 0 | yes |
| alembic_upgrade_head | `alembic upgrade head` | 0 | yes |
| alembic_current_after | `alembic current` | 0 | yes |
| migration_graph_check | `/usr/bin/python3 scripts/verify_migration_graph.py` | 0 | yes |
| schema_integrity_check | `/usr/bin/python3 scripts/validate_schema_integrity.py` | 0 | yes |

## Command output

### alembic_current_before

```text
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
20260516_0100 (head)
```

### alembic_upgrade_head

```text
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
```

### alembic_current_after

```text
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
20260516_0100 (head)
```

### migration_graph_check

```text
Migration graph OK: 21 revisions, head=20260516_0100
```

### schema_integrity_check

```text
Schema integrity OK
```
