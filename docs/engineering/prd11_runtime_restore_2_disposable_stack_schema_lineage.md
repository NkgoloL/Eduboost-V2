# PRD-11.0R.RUNTIME-RESTORE-2 — Disposable Stack Execution and Schema Lineage Reconciliation

**Status:** Authority recorded; evidence records the current non-green runtime state without greenwashing.
**Scope:** Restore executable proof for a disposable stack and database lineage path before any production-release evidence is captured.

## Purpose

PRD-11.0R.RUNTIME-RESTORE-1 installed fail-closed readiness checks. PRD-11.0R.RUNTIME-RESTORE-2 adds the execution contract needed to prove those checks safely:

- a complete disposable stack command plan;
- exact Alembic repository-head reconciliation;
- live database lineage/schema probing when `DATABASE_URL` is supplied;
- a no-blind-stamp policy for unknown database revisions;
- snapshot/inventory-before-bridge-or-rebuild policy;
- explicit handoff to product/runtime gate repair after stack/lineage controls are in place.

## Non-negotiable policy

```json
{
  "no_blind_alembic_stamp": true,
  "snapshot_before_lineage_repair": true,
  "fresh_disposable_database_must_migrate_to_head": true,
  "existing_database_requires_inventory_before_bridge_or_rebuild": true,
  "runtime_schema_contract_required_after_migration": true,
  "ready_probe_required_after_stack_start": true
}
```

## Required proof model

Static contract checks may pass without Docker or a live database. Live proof is only accepted when:

1. the disposable stack is running with PostgreSQL, Redis, API, worker, and frontend;
2. a fresh database migrates to the single repository Alembic head;
3. an existing database is snapshotted and inventoried before bridge/rebuild decisions;
4. critical runtime tables and columns satisfy the readiness schema contract;
5. `/ready` returns 200 against the running API;
6. the true-state baseline collector is rerun with expensive checks enabled.

## Boundaries

This slice does not authorise production release, deployment, public beta, live payment processing, or operational learner traffic safety. The controlled-beta authority remains historical, but activation remains on operational hold until the runtime baseline is green.
