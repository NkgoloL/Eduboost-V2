---
title: Auth Router Boundary Repair Report
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

# Auth Router Boundary Repair Report

Generated at: `2026-05-18T06:56:32Z`

**Status:** implemented

- Added `app/api_v2_deps/auth_runtime.py` dependency module.
- Added `app/services/auth_runtime_boundary.py` runtime context service.
- Removed direct `LearnerRepository` construction/import from auth router.
- Routed guardian learner scope lookup through `AuthRuntimeContext.guardian_learner_ids`.

## Boundary

This batch closes the direct learner-repository refresh allowance. Remaining auth repository imports must be handled by a later full AuthService extraction batch.
