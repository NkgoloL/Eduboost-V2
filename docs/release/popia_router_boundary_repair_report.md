---
title: POPIA Router Boundary Repair Report
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

# POPIA Router Boundary Repair Report

Generated at: `2026-05-17T21:19:07Z`

**Status:** implemented

- Moved canonical consent service factory to `app/api_v2_deps/consent_lifecycle.py`.
- Moved authenticated actor extraction to dependency module.
- Moved POPIA learner-write wrapper to dependency module.
- Removed direct `app.repositories` import from POPIA router.
