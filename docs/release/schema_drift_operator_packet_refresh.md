# Schema Drift Operator Packet Refresh

**Status:** still pending real disposable DB execution

## Required commands

```bash
export DATABASE_URL="postgresql+asyncpg://<real_user>:<real_password>@localhost:5432/eduboost_test"
make schema-drift-disposable-proof
make schema-drift-disposable-proof-check
make schema-drift-check-db
```

## Blocked shortcuts

- placeholder credentials
- production database
- `alembic stamp head` as repair
- destructive table cleanup without data-retention decision
