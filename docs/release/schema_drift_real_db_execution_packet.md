---
title: Schema Drift Real DB Execution Packet
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

# Schema Drift Real DB Execution Packet

**Status:** blocked pending disposable DB credentials

## Operator steps

```bash
export DATABASE_URL="postgresql+asyncpg://<real_user>:<real_password>@localhost:5432/eduboost_test"
make schema-drift-disposable-proof
make schema-drift-disposable-proof-check
make schema-drift-check-db
```

## Acceptance

- migration proof passes
- ORM-vs-DB comparison passes
- no placeholder credentials
- no production database
- no `alembic stamp head` repair
