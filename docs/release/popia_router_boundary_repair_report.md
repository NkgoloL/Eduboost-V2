---
title: "Release — POPIA Router Boundary Repair Report"
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
# POPIA Router Boundary Repair Report

Generated at: `2026-05-17T21:19:07Z`

**Status:** implemented

- Moved canonical consent service factory to `app/api_v2_deps/consent_lifecycle.py`.
- Moved authenticated actor extraction to dependency module.
- Moved POPIA learner-write wrapper to dependency module.
- Removed direct `app.repositories` import from POPIA router.
