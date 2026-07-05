---
title: "Post-Incident Review Contract"
status: "current-evidence"
owner: "operations"
reviewers: ["operations", "support", "privacy"]
audience: "operator"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-06-24"
review_interval_days: 60
evidence_command: "make docs-housekeeping-stage5-check"
code_anchors: "[docs/operations_support, docs/runbooks]"
---

# Post-Incident Review Contract

## Required Review Fields

- review ID
- incident ID
- completed flag
- root cause documented
- timeline documented
- corrective actions
- owner
- evidence path

## Required Review Rules

- sev1 incidents require post-incident review
- sev2 incidents require post-incident review
- root cause must be documented
- incident timeline must be documented
- corrective actions are required
- post-incident evidence must be retained

## Boundary

This contract records post-incident review readiness. It does not complete reviews automatically.
