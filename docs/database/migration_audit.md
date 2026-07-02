---
title: "Migration Audit"
status: "current-evidence"
owner: "database"
reviewers: ["backend", "database", "release-management"]
audience: "developer"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-06-24"
review_interval_days: 60
evidence_command: "make docs-housekeeping-stage5-check"
code_anchors: "[alembic, app/repositories, scripts/validate_schema_integrity.py]"
---

# Migration Audit

**Audit date:** 2026-06-14
**Status:** Current graph and schema integrity pass; squash deferred

## Current State

- Migration files under `alembic/versions/`: 34 tracked revisions.
- Current head: `20260609_0800_practice_sessions`.
- Graph verification: `python3 scripts/verify_migration_graph.py` passed.
- Schema integrity verification: `python3 scripts/validate_schema_integrity.py` passed.

## Revision Inventory

The migration chain includes the consolidated V2 baseline plus post-baseline
feature migrations for authentication, content factory, POPIA consent/erasure,
and durable practice sessions.

The earliest tracked revision is:

- `0001_v2_consolidated_schema.py`

The latest tracked revision is:

- `20260609_0800_practice_sessions_durable.py`

## Squash Recommendation

Do not squash in the current release line.

Reasons:

- The graph is already consolidated around a V2 baseline and currently verifies.
- Several later migrations include production-domain changes, not only mechanical schema creation.
- Squashing would create avoidable deployment risk unless paired with a fresh empty-database and upgrade/downgrade smoke cycle.

## Required Ongoing Checks

```bash
python3 scripts/verify_migration_graph.py
python3 scripts/validate_schema_integrity.py
make migration-smoke
```

`make migration-smoke` should be run in an environment with a disposable PostgreSQL database.
