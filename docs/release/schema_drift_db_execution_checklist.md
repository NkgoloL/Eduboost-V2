# Schema Drift DB Execution Checklist

**Status:** pending disposable DB execution

## Required implementation slices

| Slice | Command | Expected |
|---|---|---|
| Configure disposable DB | `export DATABASE_URL=...eduboost_test` | real disposable credentials |
| Migration capture | `make migration-evidence-capture` | pass |
| Migration validation | `make migration-evidence-check` | pass |
| ORM-only inventory | `make schema-drift-check` | pass |
| DB drift comparison | `make schema-drift-check-db` | pass |
| Record decision | update decision record | no blind stamp |

## Failure interpretation

- Missing ORM tables after fresh upgrade means migration graph is incomplete.
- Missing live DB tables while Alembic reports head means the DB may have been incorrectly baselined.
- Extra DB tables require explicit legacy/retention classification.
