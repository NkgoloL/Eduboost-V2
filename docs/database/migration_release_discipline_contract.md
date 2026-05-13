# Migration Release Discipline Contract

## Purpose

This contract records repository-verifiable migration discipline for empty-database upgrades, drift checks, rollback discipline, data-safety planning, and migration naming.

## Required Migration CI Evidence

- `alembic upgrade head` runs from an empty PostgreSQL database in CI
- `alembic check` runs in CI
- migration graph validation runs in repository checks
- schema integrity validation runs in repository checks
- downgrade and re-upgrade rollback smoke evidence exists in CI
- migration smoke script exists for disposable database validation
- migration naming convention is statically enforced for new migrations
- no real learner PII appears in migration seed fixtures

## Required Destructive Migration Controls

- destructive migrations require rollback notes
- migrations touching learner data require backup plan
- migrations touching guardian data require backup plan
- migrations touching learner or guardian data require staging dry run
- migrations touching learner or guardian data require validation script
- migrations touching learner or guardian data require rollback plan
- migration-diff summaries are retained as release evidence when generated

## Required Evidence Files

- `.github/workflows/migration_check.yml`
- `scripts/verify_migration_graph.py`
- `scripts/validate_schema_integrity.py`
- `scripts/smoke_test_migrations.sh`
- `docs/database/migration_discipline.md`
- `docs/database/schema_integrity.md`
- `alembic/env.py`
- `alembic/versions/`

## Verification Boundary

This contract validates repo-side migration discipline. It does not execute production migrations, approve destructive changes, or replace staging dry-run evidence from live infrastructure.
