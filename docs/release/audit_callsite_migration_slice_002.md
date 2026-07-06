---
title: Audit Call-Site Migration Slice 002
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

# Audit Call-Site Migration Slice 002

**Status:** adapter-backed migration orchestrator active

## Scope

This slice introduces `app/services/audit_migration_orchestrator.py` to create canonical audit events only for migration candidates already marked adapter-ready.

## Guardrails

- Candidate must be listed in the audit canonicalization registry.
- Candidate must be non-destructive.
- Event is routed through `AuditRepositoryCompatAdapter`.
- Legacy deletion remains blocked.
