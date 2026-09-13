---
title: "Release — Schema Drift Execution Gate Hardening"
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
# Schema Drift Execution Gate Hardening

**Status:** preflight guard active

## Rule

Schema drift execution remains blocked until a real disposable PostgreSQL database is available.

## Required command sequence

```bash
export DATABASE_URL="postgresql+asyncpg://<real_user>:<real_password>@localhost:5432/eduboost_test"
make schema-drift-disposable-proof
make schema-drift-disposable-proof-check
make schema-drift-check-db
```

## Forbidden shortcuts

- placeholder credentials
- production DB
- `alembic stamp head` as a blind repair
- dropping extra tables without data-retention decision
