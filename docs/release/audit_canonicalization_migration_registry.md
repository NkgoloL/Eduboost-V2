---
title: Audit Canonicalization Migration Registry
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

# Audit Canonicalization Migration Registry

**Status:** first implementation registry active

## Current migration candidates

| Candidate | Scope | Status | Destructive? |
|---|---|---|---|
| consent_audit_events | Consent runtime audit events | migration_ready | no |
| popia_data_rights_audit | POPIA service audit events | adapter_ready | no |
| legacy_audit_logs | Historical/legacy audit persistence | deferred | no |

## Rule

Only non-destructive candidates with adapter coverage may proceed to runtime wiring. Legacy deletion remains blocked by the deletion candidate inventory, data-retention checklist, and release-owner approval.
