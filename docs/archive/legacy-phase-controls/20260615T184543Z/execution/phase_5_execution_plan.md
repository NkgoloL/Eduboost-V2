# Phase 5 Execution Plan — Migrations and Schema Management

**Date**: 2026-06-10
**Status**: COMPLETE (refreshed 2026-06-14)
**Branch**: `phase-5/migrations-and-schema-management`
**Scope**: Fix broken migration graph, remove production startup schema repair, add migration verification to CI.
**Priority**: P1 (per [roadmap.md](../roadmap.md#L231-L253))

---

## Pre-Conditions

Before Phase 5 implementation begins:

- [x] Use the WSL Python 3.12 runtime for verification. The earlier broken `.venv/bin/python` precondition is no longer current for this checkout.
  ```bash
  python -m venv .venv
  .venv/bin/pip install -e ".[dev]"
  ```
  **Current state (2026-06-14):** Phase 5 verification uses `python3` in the WSL checkout.

---

## Pre-Execution Baseline

### 5.0.1 — Migration Graph Check (captured 2026-06-10)

```bash
$ python scripts/verify_migration_graph.py
```

**Actual output (baseline — FAILING):**

```
Migration graph validation failed:
- 20260609_0800_practice_sessions_durable.py: down_revision '20260605_0500_fix_migration_graph' does not exist
- 3f8a2c1d9e04_add_auth_extensions.py: new migration names must match YYYYMMDD_HHMM_<short_description>.py
- f2faf5aa12fd_merge_migration_branches.py: new migration names must match YYYYMMDD_HHMM_<short_description>.py
- expected exactly one head revision, found ['20260609_0800_practice_sessions_durable', 'f2faf5aa12fd']
```

4 errors, exit code 1. Two distinct root causes:
1. Broken `down_revision` pointer (`20260605_0500_fix_migration_graph` ghost reference)
2. Two legacy migrations not registered in `LEGACY_EXEMPTIONS`

### 5.0.2 — Startup Schema Repair (code inspection)

The function `run_startup_migrations()` at [app/api_v2.py](../../app/api_v2.py#L35-L115) runs **only in production** (`if not settings.is_production(): return`). It performs DDL against the live database:

- `ALTER TABLE guardians ADD COLUMN IF NOT EXISTS email_verified`
- `CREATE TYPE tokenpurpose AS ENUM (...)`
- `CREATE TABLE IF NOT EXISTS secure_tokens (...)`
- `CREATE UNIQUE INDEX IF NOT EXISTS ...`

This means production database schema is mutated on every API restart outside of Alembic's control. The migration responsibility is split between Alembic (for dev/CI) and this startup repair (for production).

### 5.0.3 — CI Coverage

Static migration graph validation and schema integrity checks are **not present** in `.github/workflows/ci-cd.yml`. No CI job blocks on migration correctness.

---

## Phase 5.1 — Fix Broken Migration Graph

### Problem Statement

`python scripts/verify_migration_graph.py` fails with 4 errors. The practice-sessions migration references a non-existent parent, and two legacy migrations violate the naming convention without being exempted.

### Acceptance Criteria

- [x] `python scripts/verify_migration_graph.py` passes with 0 errors
- [x] Migration graph resolves to exactly one head revision

### Implementation Tasks

- [x] Fix `down_revision` in [alembic/versions/20260609_0800_practice_sessions_durable.py](../../alembic/versions/20260609_0800_practice_sessions_durable.py): change `'20260605_0500_fix_migration_graph'` → `'f2faf5aa12fd'`
- [x] Add `"3f8a2c1d9e04_add_auth_extensions.py"` to `LEGACY_EXEMPTIONS` in [scripts/verify_migration_graph.py](../../scripts/verify_migration_graph.py)
- [x] Add `"f2faf5aa12fd_merge_migration_branches.py"` to `LEGACY_EXEMPTIONS`
- [x] Run `python scripts/verify_migration_graph.py` — confirmed 0 errors, exit code 0
- [x] Commit with message: `fix: repair migration graph (down_revision + legacy exemptions)`; historical implementation is now represented on `master`

---

## Phase 5.2 — Remove Production Startup Schema Repair

### Problem Statement

`run_startup_migrations()` in [app/api_v2.py](../../app/api_v2.py#L35) mutates the production database schema on every API restart. This is dangerous because:

- DDL runs against a live production database without migration tracking
- Schema state depends on which API instance restarts first
- Alembic has no visibility into these mutations
- The function is conditional on `settings.is_production()` — meaning it only runs where it's most dangerous

### Acceptance Criteria

- [x] `run_startup_migrations()` function removed from [app/api_v2.py](../../app/api_v2.py)
- [x] `lifespan` context manager no longer calls any schema mutation
- [x] All schema objects created by `run_startup_migrations` are covered by existing Alembic migrations (verified via `alembic upgrade head` against a fresh database)
- [x] API startup produces no DDL statements against the database

### Implementation Tasks

- [x] Verify that Alembic migrations already cover: `guardians.email_verified`, `tokenpurpose` enum, `secure_tokens` table, and indexes
- [x] Delete the `run_startup_migrations()` function from [app/api_v2.py](../../app/api_v2.py)
- [x] Remove the call to `run_startup_migrations()` from the `lifespan` context manager
- [x] Clean up unused imports resulting from the removal
- [x] Commit with message: `fix: remove production startup schema repair (Alembic is authoritative)`; historical implementation is now represented on `master`

---

## Phase 5.3 — Prove Migration Correctness Against a Live Database

### Problem Statement

The RoadMap requires proof that `alembic upgrade head` succeeds in an isolated test database and that `alembic current` reports the expected head. This has not been demonstrated.

### Acceptance Criteria

- [x] `alembic upgrade head` succeeds in an isolated test database (Docker PostgreSQL or local)
- [x] `alembic current --verbose` reports a single head revision matching the latest migration
- [x] `make migration-smoke` passes (upgrade -> downgrade -> upgrade cycle) when `DATABASE_URL` is set to a disposable PostgreSQL database

### Implementation Tasks

- [x] Start a disposable PostgreSQL instance (Docker or local)
- [x] Run `alembic upgrade head` — captured through `make migration-smoke`
- [x] Run `alembic current --verbose`/`alembic current` — captured single head `20260609_0800_practice_sessions`
- [x] Run `alembic downgrade -1` then `alembic upgrade head` to verify downgrade path
- [x] Capture output summary to `docs/release/phase_5_evidence.md`
- [x] Commit evidence file

---

## Phase 5.4 — Add Migration Checks to CI

### Problem Statement

`verify_migration_graph.py` and `validate_schema_integrity.py` exist but are not executed as blocking steps in the CI/CD pipeline. Schema drift can reach `master` undetected.

### Acceptance Criteria

- [x] `python scripts/verify_migration_graph.py` runs as a blocking step in CI
- [x] `python scripts/validate_schema_integrity.py` runs as a blocking step in CI
- [x] CI job fails if either script exits non-zero

### Implementation Tasks

- [x] Add a `schema-drift` job (or extend existing `lint` job) in [.github/workflows/ci-cd.yml](../../.github/workflows/ci-cd.yml):
  ```yaml
  - name: Migration Graph Check
    run: python scripts/verify_migration_graph.py
  - name: Schema Integrity Check
    run: python scripts/validate_schema_integrity.py
  ```
- [x] Commit CI config change

---

## Evidence Output

| Artifact | Path | Status |
|----------|------|--------|
| Phase 5 evidence (before/after migration checks) | `docs/release/phase_5_evidence.md` | [x] |
| CI run URL with passing schema checks | Captured from PR | [verify outside local checkout] |
| Implementation audit | `docs/release/phase_5_implementation_audit.md` | [x] |

---

## Success Criteria

**Phase 5 is complete when:**

- [x] `python scripts/verify_migration_graph.py` passes with 0 errors
- [x] `alembic upgrade head` succeeds against an isolated database
- [x] `alembic current --verbose` reports a single expected head
- [x] API startup performs zero DDL (no schema repair in `lifespan`)
- [x] CI blocks on migration graph and schema integrity checks
- [x] All evidence files committed
- [x] `docs/release/phase_5_implementation_audit.md` committed
- [x] Tracking documents updated (`roadmap.md`, `build-plan.md`, `progress-tracker.md`, `todo.md`)

---

## Close Checklist (per PROCESS_DISCIPLINE.md)

- [x] Execution plan exists: `docs/roadmap/execution/phase_5_execution_plan.md` (this file)
- [x] Implementation report exists: `docs/roadmap/execution/phase_5_implementation_report.md`
- [x] Audit report exists: `docs/release/phase_5_implementation_audit.md`
- [x] Evidence files committed and accurate
- [x] `roadmap.md` Phase 5 status updated to "Complete (YYYY-MM-DD)"
- [x] `context/build-plan.md` Phase 5 status updated
- [x] `context/progress-tracker.md` updated
- [ ] CI gates pass on the phase branch
- [x] Branch merged to `master` / represented on current `master`
- [ ] Remote branch deleted after merge
- [x] `docs/todos/todo.md` North Star tasks updated

---

## Next Phase

**Phase 6: Durable Background Jobs** — Wire ARQ durable background worker into Compose/Production. Replace non-durable FastAPI `BackgroundTasks` with durable jobs.

---

## References

- RoadMap Phase 5: [roadmap.md](../roadmap.md#L231)
- Process Discipline: [PROCESS_DISCIPLINE.md](../PROCESS_DISCIPLINE.md)
- Migration graph script: [scripts/verify_migration_graph.py](../../scripts/verify_migration_graph.py)
- Startup repair code: [app/api_v2.py](../../app/api_v2.py#L35-L115)
- CI workflow: [.github/workflows/ci-cd.yml](../../.github/workflows/ci-cd.yml)
