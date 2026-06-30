# PR-003A — Data Integrity Baseline: Handover

Date: 2026-05-29
Owner: Backend Platform
Status: Ready for review and staging sync

## Executive summary

Implements a safe baseline to improve data integrity and performance without changing identifier types. This defers the invasive UUID migration to a dedicated follow-up.

## Why

Audit highlighted high-priority risks:
- ID type mismatch (String vs UUID) blocks FKs and risks orphans.
- Missing FKs where relationships are implied.
- Alembic autogen suppressed drift for indexes/uniques/FKs.
- JSONB/array query performance at scale without GIN.
- High-growth tables (exposures, audit) lacking range-scan aids.

## What’s included in this PR

- Alembic autogen policy hardened
  - Change: include indexes, unique constraints, and foreign keys in autogenerate/drift detection.
  - File: `alembic/env.py` (`_include_object` updated).

- Performance indexes (safe, additive)
  - GIN: `diagnostic_items.misconception_tags`.
  - GIN (jsonb_path_ops): `content_generation_artifacts.artifact_json`.
  - BRIN: `item_exposures.served_at`, `audit_logs.created_at`, `lesson_feedback.submitted_at`.
  - File: `alembic/versions/20260529_1500_performance_indexes.py`.

- Foreign keys where types already align
  - `practice_queue.item_id` → `diagnostic_items.item_id` (ON DELETE SET NULL, NOT VALID).
  - `calibration_audits.item_id` → `diagnostic_items.item_id` (ON DELETE SET NULL, NOT VALID).
  - Same migration as above (kept NOT VALID to avoid blocking; validate later).

- UUID normalization plan documented (no schema changes yet)
  - ADR-026: staged, dual-write migration from `String(36)` → `uuid`, cutover/cleanup.
  - File: `docs/adr/ADR-026-uuid-normalization-plan.md`.

## Files changed/added

- Modified: `alembic/env.py`
- Added: `alembic/versions/20260529_1500_performance_indexes.py`
- Added: `docs/adr/ADR-026-uuid-normalization-plan.md`

## Rollout steps

1) Apply migrations
- `alembic upgrade head`

2) Validate new NOT VALID constraints (during a quiet window)
- `ALTER TABLE practice_queue VALIDATE CONSTRAINT fk_practice_queue_item_id;`
- `ALTER TABLE calibration_audits VALIDATE CONSTRAINT fk_calibration_audits_item_id;`

3) Observe CI
- `alembic check` ensures no pending drift, now including indexes/uniques/FKs.

## Backout plan

- `alembic downgrade -1` to remove performance indexes and added FKs.
- Revert `alembic/env.py` change if needed (restores old autogen behavior).

## Risks and mitigations

- New indexes add write overhead: measured minimal risk; all are safe and common.
- NOT VALID FKs: do not block; schedule validation later to avoid long locks.
- No identifier changes here; zero risk of PK/FK churn in this PR.

## Next steps (separate PRs)

- PR-003B — Scoped UUID rollout (guardians → reviewer_id path)
  - Add parallel UUID columns, dual-write, backfill, add NOT VALID FKs, validate, cutover, remove legacy IDs.

- PR-003C — Retention/partitioning
  - Time-range partitioning for `item_exposures` and `audit_logs`.
  - Optional retention policies (e.g., 12–18 months online).

- PR-003D — Additional indexes (optional)
  - Targeted GIN/BRIN on other hot JSONB/arrays or time-series if query paths justify.

## Acceptance criteria

- Migrations apply cleanly; `alembic check` passes.
- Production read/write latencies unchanged or improved on heavy paths.
- No functional changes to API behavior.

## Validation Evidence

- `scripts/wait_for_db.py` verified for DSN normalization and async readiness checks.
- `scripts/smoke_test_migrations.sh` verified for migration idempotency.
- `make wait-db`, `make migrate`, and `make migration-smoke` verified.
- `scripts/ci/check_content_factory_migrations.sh` passed.
- Content Factory route security tests passed.
- Content Factory enum compatibility tests passed.
- Content Factory table reconciliation tests passed.
- CI content-factory-migrations job confirmed to use PostgreSQL 16 and wait-for-db.

*Note: `ENCRYPTION_KEY` and `DATABASE_URL` environment variables were required as test env vars.*

## Implementation Note

No additional structural code edits were required for this batch. Repository inspection confirmed the migration-resilience plan was already implemented.

## References

- Audit report: Data-layer risks summary
- ADR-026: UUID Normalization Plan
