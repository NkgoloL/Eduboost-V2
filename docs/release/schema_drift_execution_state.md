---
title: Schema Drift Execution State
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

# Schema Drift Execution State

**Status:** awaiting real disposable DB execution

## Current state

Schema drift tooling exists. Real database proof still requires an actual disposable PostgreSQL database with real credentials.

## Required commands

```bash
export DATABASE_URL="postgresql+asyncpg://<real_user>:<real_password>@localhost:5432/eduboost_test"
make schema-drift-disposable-proof
make schema-drift-disposable-proof-check
make schema-drift-check-db
```

## Guardrails

- Do not use placeholder credentials.
- Do not use production database.
- Do not run `alembic stamp head` as a repair.
