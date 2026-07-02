---
title: "Support SLA Policy"
status: active
owner: operations
reviewers: [operations, support, privacy]
audience: operator
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-06-24
review_interval_days: 60
evidence_command: "make docs-housekeeping-stage5-check"
code_anchors: [docs/operations_support, docs/runbooks]
---

# Support SLA Policy

## Required Support Priorities

| Priority | First Response | Target Resolution | Escalation |
| --- | --- | --- | --- |
| p0 | 15 minutes | 4 hours | required |
| p1 | 60 minutes | 24 hours | required |
| p2 | 240 minutes | 72 hours | optional |
| p3 | 1440 minutes | 168 hours | optional |

## Required Controls

- p0 support requires escalation
- p1 support requires escalation
- p0 first response must be <= 30 minutes
- p1 first response must be <= 120 minutes
- support cases involving privacy or security classify as p0
- customer-visible support priorities must have communication path

## Boundary

This policy records support SLA readiness. It does not create support tickets.
