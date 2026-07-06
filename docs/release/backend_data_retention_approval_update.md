---
title: Backend Data Retention Approval Update
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

# Backend Data Retention Approval Update

**Status:** destructive data changes remain blocked

## Current decision

- `audit_logs` deletion: blocked
- audit history discard: blocked
- `consent_records` / `parental_consents` merge: blocked
- consent history deletion: blocked

## Required approvals

Legal/security/release-owner approval is required before any destructive audit or consent data action.
