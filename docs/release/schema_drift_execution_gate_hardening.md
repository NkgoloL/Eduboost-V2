# Schema Drift Execution Gate Hardening

**Status:** preflight guard active

## Rule

Schema drift execution remains blocked until a real disposable PostgreSQL database is available.

## Required command sequence

```bash
export DATABASE_URL="postgresql+asyncpg://<real_user>:<real_password>@localhost:5432/eduboost_test"
make schema-drift-disposable-proof
make schema-drift-disposable-proof-check
make schema-drift-check-db
```

## Forbidden shortcuts

- placeholder credentials
- production DB
- `alembic stamp head` as a blind repair
- dropping extra tables without data-retention decision
