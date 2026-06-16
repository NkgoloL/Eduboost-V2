# Phase 5 Implementation Report

**Date**: 2026-06-10  
**Refresh**: 2026-06-14
**Phase**: 5 - Migrations and Schema Management  
**Status**: Complete locally; tracker closeout remains

---

## Executive Summary

Phase 5 was implemented to restore Alembic as the source of truth for schema changes, remove production startup DDL, and add blocking migration checks to CI.

The work completed in three main layers:

1. Repair the migration graph so it resolves to one head.
2. Remove startup schema repair from `app/api_v2.py`.
3. Prove the migration path against a fresh PostgreSQL database and add CI drift checks.

The live smoke test now passes end to end, including upgrade, downgrade, re-upgrade, and idempotency verification.

---

## Before

### Baseline migration graph failure

Before the fix, the migration graph validator failed with four errors:

```text
Migration graph validation failed:
- 20260609_0800_practice_sessions_durable.py: down_revision '20260605_0500_fix_migration_graph' does not exist
- 3f8a2c1d9e04_add_auth_extensions.py: new migration names must match YYYYMMDD_HHMM_<short_description>.py
- f2faf5aa12fd_merge_migration_branches.py: new migration names must match YYYYMMDD_HHMM_<short_description>.py
- expected exactly one head revision, found ['20260609_0800_practice_sessions_durable', 'f2faf5aa12fd']
```

Root causes:

- The practice sessions migration pointed to a non-existent parent revision.
- Two legacy migration files were not exempted from the naming rule.

### Startup schema repair existed in the FastAPI entrypoint

Before the cleanup, [`app/api_v2.py`](../../app/api_v2.py) contained `run_startup_migrations()`, which ran production-only DDL at startup:

- `ALTER TABLE guardians ADD COLUMN IF NOT EXISTS email_verified`
- `CREATE TYPE tokenpurpose AS ENUM (...)`
- `CREATE TABLE IF NOT EXISTS secure_tokens (...)`
- `CREATE INDEX IF NOT EXISTS ...`

That meant schema repair could happen outside Alembic’s migration tracking on every API restart in production.

### CI did not block on schema drift

Before the change, `.github/workflows/ci-cd.yml` did not run:

- `python scripts/verify_migration_graph.py`
- `python scripts/validate_schema_integrity.py`

So broken migration topology could reach the branch without a hard CI gate.

---

## After

### Migration graph is valid

The graph now resolves to a single head revision.

Verified output:

```text
Migration graph OK: 34 revisions, head=20260609_0800_practice_sessions
```

The revision ID for the practice sessions migration was shortened to fit Alembic’s version table width, and the head now writes cleanly to the database.

### Startup schema repair removed

[`app/api_v2.py`](../../app/api_v2.py) no longer contains `run_startup_migrations()`, and the lifespan context manager no longer invokes schema mutation before serving requests.

This restores a clean separation of responsibilities:

- Alembic owns schema changes
- API startup only starts application services

### CI now blocks schema drift

The CI workflow now includes a dedicated `schema-drift` job that runs:

- `python scripts/verify_migration_graph.py`
- `python scripts/validate_schema_integrity.py`

That makes migration integrity and ORM schema integrity blocking checks rather than informal local-only scripts.

### Migration smoke test passes

`make migration-smoke` now passes against a disposable PostgreSQL 15 instance.

Verified result:

- `alembic upgrade head` succeeded
- `alembic current --verbose` reported a single head
- `alembic downgrade -1` succeeded
- `alembic upgrade head` succeeded again
- second `upgrade head` was idempotent

Smoke test result:

```text
Migration smoke test PASSED.
```

And the current head was confirmed as:

```text
Rev: 20260609_0800_practice_sessions (head)
Parent: f2faf5aa12fd
```

---

## Files Changed

- [`alembic/versions/20260609_0800_practice_sessions_durable.py`](../../alembic/versions/20260609_0800_practice_sessions_durable.py)
- [`alembic/versions/3f8a2c1d9e04_add_auth_extensions.py`](../../alembic/versions/3f8a2c1d9e04_add_auth_extensions.py)
- [`alembic/versions/f2faf5aa12fd_merge_migration_branches.py`](../../alembic/versions/f2faf5aa12fd_merge_migration_branches.py)
- [`app/api_v2.py`](../../app/api_v2.py)
- [`.github/workflows/ci-cd.yml`](../../.github/workflows/ci-cd.yml)
- [`Makefile`](../../Makefile)
- [`scripts/verify_migration_graph.py`](../../scripts/verify_migration_graph.py)

Evidence artifacts added:

- [`docs/release/phase_5_evidence.md`](../../docs/release/phase_5_evidence.md)
- [`docs/release/phase_5_implementation_audit.md`](../../docs/release/phase_5_implementation_audit.md)

---

## Verification Summary

Completed locally:

- `python3 scripts/verify_migration_graph.py`
- `python3 scripts/validate_schema_integrity.py`
- `python3 -m compileall -q alembic app scripts`
- `make migration-smoke`
- `alembic current --verbose`

All of the above passed in the final state.

Fresh 2026-06-14 refresh:

- `python3 scripts/verify_migration_graph.py` passed with 34 revisions and head `20260609_0800_practice_sessions`.
- `python3 scripts/validate_schema_integrity.py` passed.
- `python3 -m compileall -q alembic app scripts` passed.
- `DATABASE_URL=... make migration-smoke` passed against a temporary Postgres 16 container on localhost port 55433.
- `app/api_v2.py` inspection found no startup schema-repair DDL path.

---

## Residual Work

The implementation itself is complete, but the Phase 5 closeout steps still remain:

- update `docs/roadmap/roadmap.md`
- update `context/build-plan.md`
- update `context/progress-tracker.md`
- update `docs/todos/todo.md`
- merge the branch and delete it after merge
