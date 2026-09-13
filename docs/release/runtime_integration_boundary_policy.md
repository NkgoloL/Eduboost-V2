---
title: "Release — Runtime Integration Boundary Policy"
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
