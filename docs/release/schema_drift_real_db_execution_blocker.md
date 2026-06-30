# Schema Drift Real DB Execution Blocker

**Status:** blocked until real disposable DB credentials are provided

Schema drift proof is not considered complete until the following passes against a real disposable database:

```bash
make schema-drift-disposable-proof
make schema-drift-disposable-proof-check
make schema-drift-check-db
```

Placeholder credentials and production databases are forbidden.
