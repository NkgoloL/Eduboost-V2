---
title: "Release — Backend Data Retention Approval Update"
status: "active"
owner: "release"
reviewers: ['release', 'engineering']
audience: "developer"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-09-13"
review_interval_days: 90
evidence_command: "make docs-housekeeping-check"
code_anchors: "[]"
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
