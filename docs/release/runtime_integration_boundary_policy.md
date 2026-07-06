---
title: Runtime Integration Boundary Policy
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

# Runtime Integration Boundary Policy

**Status:** active

## Blocked changes

- route registration
- schema migration
- audit repository deletion
- consent table merge
- public health write probe
- production DB mutation
- `alembic stamp head`

## Rule

A runtime integration PR must change one scoped path only and must include rollback notes and full test evidence.
