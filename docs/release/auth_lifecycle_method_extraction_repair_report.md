---
title: Auth Lifecycle Method Extraction Repair Report
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

# Auth Lifecycle Method Extraction Repair Report

Generated at: `2026-05-18T16:23:42Z`

**Status:** implemented

## Delegated lifecycle methods


## Boundary

Routes now delegate through AuthApplicationService methods. Original route bodies are preserved as private `_auth_lifecycle_legacy_*_impl` helpers to avoid behavior changes while completing the service-boundary transition.

## Remaining debt

- Move private legacy helper bodies out of auth.py into AuthApplicationService proper.
- Add full HTTP request/response integration tests for register/login/refresh/dev-session.
