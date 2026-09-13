---
title: "Runtime Integration PR Template (Runtime Integration Pr Template)"
status: "active"
owner: "engineering"
reviewers: ['engineering', 'architecture']
audience: "developer"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-09-13"
review_interval_days: 90
evidence_command: "make docs-housekeeping-check"
code_anchors: "[]"
---
# Runtime Integration PR Template

## Purpose

Plan a future runtime-integration PR from dry-run evidence only.

## Required evidence

- Runtime integration readiness check output.
- Runtime integration blocklist check output.
- Rollback checklist reference.

## Non-scope

This template does not approve route registration, schema migration, audit repository deletion, consent table merge, production DB mutation, or Alembic stamp head.
