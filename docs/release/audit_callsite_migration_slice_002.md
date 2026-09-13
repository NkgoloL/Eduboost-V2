---
title: "Release — Audit Call-Site Migration Slice 002"
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
# Audit Call-Site Migration Slice 002

**Status:** adapter-backed migration orchestrator active

## Scope

This slice introduces `app/services/audit_migration_orchestrator.py` to create canonical audit events only for migration candidates already marked adapter-ready.

## Guardrails

- Candidate must be listed in the audit canonicalization registry.
- Candidate must be non-destructive.
- Event is routed through `AuditRepositoryCompatAdapter`.
- Legacy deletion remains blocked.
