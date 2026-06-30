# Schema Drift Disposable DB Proof

**Status:** pending disposable DB execution

This document records the new guarded execution path for disposable database schema drift proof.

## Commands

Dry-run the command plan:

```bash
DATABASE_URL="postgresql+asyncpg://real_user:real_password@localhost:5432/eduboost_test" \
  PYTHONPATH=. python3 scripts/run_disposable_schema_drift_proof.py --dry-run
```

Execute against a real disposable database:

```bash
export DATABASE_URL="postgresql+asyncpg://real_user:real_password@localhost:5432/eduboost_test"
make schema-drift-disposable-proof
make schema-drift-disposable-proof-check
```

## Guardrails

- Refuses missing `DATABASE_URL`.
- Refuses non-test-looking database URLs unless explicitly overridden.
- Refuses placeholder credentials such as `user:pass`.
- Runs migration evidence capture before ORM-vs-DB drift comparison.
- Writes latest output to `docs/release/schema_drift_disposable_latest.json` and `.md`.
