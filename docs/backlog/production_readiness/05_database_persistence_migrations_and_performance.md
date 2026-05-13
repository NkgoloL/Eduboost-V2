# 5. Database, persistence, migrations, and performance

## 5.1 Schema readiness

- [verify] `P0` Confirm every production table has explicit primary key.
- [verify] `P0` Confirm every production table has timestamps.
- [verify] `P0` Confirm every relationship has appropriate foreign key.
- [verify] `P0` Confirm role enum constraints.
- [verify] `P0` Confirm consent status constraints.
- [verify] `P0` Confirm audit event constraints.
- [verify] `P0` Confirm immutable audit identifier constraints.
- [verify] `P0` Confirm unique guardian-learner relationship constraints.
- [verify] `P0` Confirm non-null constraints for sensitive workflow fields.
- [verify] `P0` Verify index on user email hash.
- [verify] `P0` Verify index on learner ID.
- [verify] `P0` Verify index on guardian ID.
- [verify] `P0` Verify index on consent status.
- [verify] `P0` Verify index on token identifiers.
- [verify] `P0` Verify index on diagnostic attempt/session ID.
- [verify] `P0` Verify index on lesson generation job ID.
- [verify] `P0` Verify index on audit timestamp.
- [verify] `P0` Verify index on audit actor ID.
- [verify] `P0` Verify index on subscription/customer ID.
- [verify] `P1` Add partial index for active consent.
- [verify] `P1` Add partial index for active subscriptions.
- [verify] `P1` Add partial index for non-revoked sessions.
- [verify] `P1` Add partial index for incomplete jobs.

## 5.2 Migration discipline

- [verify] `P0` Ensure `alembic upgrade head` runs in CI from empty DB.
- [verify] `P0` Ensure `alembic check` runs in CI.
- [verify] `P0` Add migration graph validation. Evidence: `scripts/verify_migration_graph.py`, `tests/unit/test_migration_graph.py`, `make migration-check`.
- [verify] `P0` Add schema integrity validation. Evidence: `scripts/validate_schema_integrity.py`, `tests/unit/test_schema_integrity.py`, `make schema-integrity`.
- [verify] `P0` Document rollback for every destructive migration.
- [verify] `P0` Require backup plan for migrations touching learner/guardian data.
- [verify] `P0` Require staging dry run for migrations touching learner/guardian data.
- [verify] `P0` Require validation script for migrations touching learner/guardian data.
- [verify] `P0` Require rollback plan for migrations touching learner/guardian data.
- [verify] `P1` Enforce migration naming convention:
  ```text
  YYYYMMDD_HHMM_<short_description>.py
  ```
- [verify] `P1` Add migration smoke test using production-like data volume.
- [verify] `P1` Add synthetic seed data for local development.
- [verify] `P1` Ensure no real learner PII appears in fixtures.
- [verify] `P2` Add migration-diff summary artifact in CI.

## 5.3 Transaction boundaries

- [verify] `P1` Review transaction boundary for signup.
- [verify] `P1` Review transaction boundary for learner creation.
- [verify] `P1` Review transaction boundary for consent submission.
- [verify] `P1` Review transaction boundary for diagnostic completion.
- [verify] `P1` Review transaction boundary for lesson generation.
- [verify] `P1` Review transaction boundary for billing changes.
- [verify] `P1` Review transaction boundary for erasure requests.
- [verify] `P1` Add tests for rollback on partial failure.
- [verify] `P1` Add tests for idempotent retries where appropriate.

## 5.4 Repository layer

- [verify] `P1` Add repository tests for guardian repository.
- [verify] `P1` Add repository tests for learner repository.
- [verify] `P1` Add repository tests for consent repository.
- [verify] `P1` Add repository tests for diagnostic repository.
- [verify] `P1` Add repository tests for lesson repository.
- [verify] `P1` Add repository tests for study-plan repository.
- [verify] `P1` Add repository tests for gamification repository.
- [verify] `P1` Add repository tests for audit repository.
- [verify] `P1` Add repository tests for billing repository.
- [verify] `P1` Ensure repositories do not expose raw ORM objects to API responses.
- [verify] `P1` Standardize repository method prefixes:
  - `get_*`
  - `list_*`
  - `create_*`
  - `update_*`
  - `soft_delete_*`
  - `append_*`
- [verify] `P1` Add pagination to all list queries.
- [verify] `P1` Add deterministic sorting to all list queries.
- [verify] `P2` Add cursor pagination for high-volume audit/event streams.

## 5.5 Performance

- [verify] `P1` Add slow-query logging in staging.
- [verify] `P1` Add slow-query logging in production.
- [verify] `P1` Add performance test for dashboard endpoints.
- [verify] `P1` Add performance test for diagnostic endpoints.
- [verify] `P1` Add performance test for lesson-generation endpoints.
- [verify] `P1` Add performance test for parent-report endpoints.
- [verify] `P1` Add performance test for audit endpoints.
- [verify] `P1` Add performance test for POPIA export endpoints.
- [verify] `P2` Define query latency budgets.
- [verify] `P2` Add DB connection pool monitoring.
- [verify] `P2` Add N+1 query checks for dashboard flows.

---



## 5.6 Repository-side implementation evidence

The Database, persistence, migrations, and performance backlog is implemented as repository-verifiable evidence through:

- `docs/database/schema_readiness_contract.md`
- `docs/database/migration_release_discipline_contract.md`
- `docs/database/repository_transaction_performance_contract.md`
- `scripts/check_database_persistence_production_readiness.py`
- `tests/unit/test_database_persistence_production_readiness.py`
- `make database-persistence-production-readiness-check`

Verification boundary: these checks prove repository-side readiness evidence. They do not replace live staging migration dry runs, production database administrator approval, production slow-query telemetry, or release-owner authorization.
