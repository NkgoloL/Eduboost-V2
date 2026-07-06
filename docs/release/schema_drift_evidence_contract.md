---
title: Schema Drift Evidence Contract
status: release-record
owner: release-management
reviewers: [release-management, evidence-custodian, documentation-governance]
audience: release-reviewer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-06
review_interval_days: 180
evidence_command: make docs-housekeeping-stage7-check
code_anchors: [docs/release, docs/documentation/stage_7_release_archive_backlog_codemaps_governance.md]
---

# Schema Drift Evidence Contract

This contract defines how EduBoost detects ORM-vs-database schema drift.

## Required evidence

| Evidence | Command |
|---|---|
| ORM table inventory | `make schema-drift-check` |
| DB table inventory | `DATABASE_URL=... make schema-drift-check-db` |
| Drift failure mode | `DATABASE_URL=... PYTHONPATH=. python3 scripts/compare_orm_tables_to_database.py --require-db --fail-on-drift` |
| Migration evidence | `make migration-evidence-capture` |

## Decision rules

- If ORM tables are missing from a fresh DB after `alembic upgrade head`, the migration graph is incomplete.
- If a live DB is missing ORM tables but reports Alembic head, the database may have been incorrectly stamped or baselined.
- If extra DB tables are intentional legacy tables, document them before deletion.
- Do not use `alembic stamp head` as a repair without a written decision record.
