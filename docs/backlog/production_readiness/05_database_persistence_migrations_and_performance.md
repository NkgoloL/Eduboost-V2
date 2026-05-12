# 5. Database, persistence, migrations, and performance

## 5.1 Schema readiness

- [ ] `P0` Confirm every production table has explicit primary key.
- [ ] `P0` Confirm every production table has timestamps.
- [ ] `P0` Confirm every relationship has appropriate foreign key.
- [ ] `P0` Confirm role enum constraints.
- [ ] `P0` Confirm consent status constraints.
- [ ] `P0` Confirm audit event constraints.
- [ ] `P0` Confirm immutable audit identifier constraints.
- [ ] `P0` Confirm unique guardian-learner relationship constraints.
- [ ] `P0` Confirm non-null constraints for sensitive workflow fields.
- [ ] `P0` Verify index on user email hash.
- [ ] `P0` Verify index on learner ID.
- [ ] `P0` Verify index on guardian ID.
- [ ] `P0` Verify index on consent status.
- [ ] `P0` Verify index on token identifiers.
- [ ] `P0` Verify index on diagnostic attempt/session ID.
- [ ] `P0` Verify index on lesson generation job ID.
- [ ] `P0` Verify index on audit timestamp.
- [ ] `P0` Verify index on audit actor ID.
- [ ] `P0` Verify index on subscription/customer ID.
- [ ] `P1` Add partial index for active consent.
- [ ] `P1` Add partial index for active subscriptions.
- [ ] `P1` Add partial index for non-revoked sessions.
- [ ] `P1` Add partial index for incomplete jobs.

## 5.2 Migration discipline

- [ ] `P0` Ensure `alembic upgrade head` runs in CI from empty DB.
- [ ] `P0` Ensure `alembic check` runs in CI.
- [verify] `P0` Add migration graph validation. Evidence: `scripts/verify_migration_graph.py`, `tests/unit/test_migration_graph.py`, `make migration-check`.
- [verify] `P0` Add schema integrity validation. Evidence: `scripts/validate_schema_integrity.py`, `tests/unit/test_schema_integrity.py`, `make schema-integrity`.
- [ ] `P0` Document rollback for every destructive migration.
- [ ] `P0` Require backup plan for migrations touching learner/guardian data.
- [ ] `P0` Require staging dry run for migrations touching learner/guardian data.
- [ ] `P0` Require validation script for migrations touching learner/guardian data.
- [ ] `P0` Require rollback plan for migrations touching learner/guardian data.
- [ ] `P1` Enforce migration naming convention:
  ```text
  YYYYMMDD_HHMM_<short_description>.py
  ```
- [ ] `P1` Add migration smoke test using production-like data volume.
- [ ] `P1` Add synthetic seed data for local development.
- [ ] `P1` Ensure no real learner PII appears in fixtures.
- [ ] `P2` Add migration-diff summary artifact in CI.

## 5.3 Transaction boundaries

- [ ] `P1` Review transaction boundary for signup.
- [ ] `P1` Review transaction boundary for learner creation.
- [ ] `P1` Review transaction boundary for consent submission.
- [ ] `P1` Review transaction boundary for diagnostic completion.
- [ ] `P1` Review transaction boundary for lesson generation.
- [ ] `P1` Review transaction boundary for billing changes.
- [ ] `P1` Review transaction boundary for erasure requests.
- [ ] `P1` Add tests for rollback on partial failure.
- [ ] `P1` Add tests for idempotent retries where appropriate.

## 5.4 Repository layer

- [ ] `P1` Add repository tests for guardian repository.
- [ ] `P1` Add repository tests for learner repository.
- [ ] `P1` Add repository tests for consent repository.
- [ ] `P1` Add repository tests for diagnostic repository.
- [ ] `P1` Add repository tests for lesson repository.
- [ ] `P1` Add repository tests for study-plan repository.
- [ ] `P1` Add repository tests for gamification repository.
- [ ] `P1` Add repository tests for audit repository.
- [ ] `P1` Add repository tests for billing repository.
- [ ] `P1` Ensure repositories do not expose raw ORM objects to API responses.
- [ ] `P1` Standardize repository method prefixes:
  - `get_*`
  - `list_*`
  - `create_*`
  - `update_*`
  - `soft_delete_*`
  - `append_*`
- [ ] `P1` Add pagination to all list queries.
- [ ] `P1` Add deterministic sorting to all list queries.
- [ ] `P2` Add cursor pagination for high-volume audit/event streams.

## 5.5 Performance

- [ ] `P1` Add slow-query logging in staging.
- [ ] `P1` Add slow-query logging in production.
- [ ] `P1` Add performance test for dashboard endpoints.
- [ ] `P1` Add performance test for diagnostic endpoints.
- [ ] `P1` Add performance test for lesson-generation endpoints.
- [ ] `P1` Add performance test for parent-report endpoints.
- [ ] `P1` Add performance test for audit endpoints.
- [ ] `P1` Add performance test for POPIA export endpoints.
- [ ] `P2` Define query latency budgets.
- [ ] `P2` Add DB connection pool monitoring.
- [ ] `P2` Add N+1 query checks for dashboard flows.

---

