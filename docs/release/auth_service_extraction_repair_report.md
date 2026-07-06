---
title: Auth Service Extraction Repair Report
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

# Auth Service Extraction Repair Report

Generated at: `2026-06-27T02:18:40Z`

**Status:** implemented

## Implemented

- Added `app/services/auth_application_service.py`.
- Added `app/api_v2_deps/auth_service.py`.
- Replaced direct auth router repository constructors with `auth_service.<repo>` handles.
- Removed direct `app.repositories` imports from `app/api_v2_routers/auth.py`.
- Preserved `auth.py` eager route model evaluation by rejecting future annotations.

## Import-linter allowances removed


## Remaining debt

- Move auth business logic from router into AuthApplicationService methods in smaller semantic slices.
- Add HTTP integration tests for register/login/refresh/dev-session with dependency overrides.
