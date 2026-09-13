---
title: "Authority Switch — KG-7 Rollback Boundary"
status: "active"
owner: "operations"
reviewers: ['operations', 'sre', 'engineering']
audience: "internal"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-09-13"
review_interval_days: 90
evidence_command: "make docs-housekeeping-check"
code_anchors: "[]"
---
# KG-7 Rollback Boundary

Rollback controls are defined in KG-7 but not executed. A future activation must
prove the ability to disable KG authority, restore legacy routing, preserve
legacy read models, freeze KG-derived writes, notify review owners, and capture
rollback evidence.
