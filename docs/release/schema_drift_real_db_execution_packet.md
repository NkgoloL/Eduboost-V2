# Schema Drift Real DB Execution Packet

**Status:** blocked pending disposable DB credentials

## Operator steps

```bash
export DATABASE_URL="postgresql+asyncpg://<real_user>:<real_password>@localhost:5432/eduboost_test"
make schema-drift-disposable-proof
make schema-drift-disposable-proof-check
make schema-drift-check-db
```

## Acceptance

- migration proof passes
- ORM-vs-DB comparison passes
- no placeholder credentials
- no production database
- no `alembic stamp head` repair
