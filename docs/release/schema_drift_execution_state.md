---
title: "Release — Schema Drift Execution State"
status: "active"
owner: "release"
reviewers: ['release', 'engineering']
audience: "internal"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-09-13"
review_interval_days: 90
evidence_command: "make docs-housekeeping-check"
code_anchors: "[]"
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
