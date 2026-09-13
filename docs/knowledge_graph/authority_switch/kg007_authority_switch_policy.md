---
title: "KG-7 Authority Switch Policy (Kg007 Authority Switch Policy)"
status: "active"
owner: "pedagogy"
reviewers: ['pedagogy', 'engineering']
audience: "internal"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-09-13"
review_interval_days: 90
evidence_command: "make docs-housekeeping-check"
code_anchors: "[]"
---
# KG-7 Authority Switch Policy

KG-7 is a readiness gate. It may document how the KG authority switch would be
controlled, but it may not flip the switch.

Required controls:

- feature flag defaults off;
- environment-scoped enablement;
- rollback path documented before activation;
- legacy compatibility projections retained through rollback window;
- privacy, curriculum, engineering, and release approvals required before any
  future runtime activation.
