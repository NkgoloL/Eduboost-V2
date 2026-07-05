---
title: "On-Call Escalation Policy"
status: "active"
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

# On-Call Escalation Policy

## Required Escalation Fields

- policy ID
- primary role
- secondary role
- escalation minutes
- coverage hours
- backup required
- handoff required
- evidence path

## Required Policies

- technical lead escalates to incident commander for sev1/sev2
- privacy lead escalates to incident commander for privacy events
- support lead escalates to communications lead for customer-facing incidents
- release owner is escalated for deployment-related incidents
- handoff is required at shift change
- backup on-call is required

## Boundary

This policy records on-call expectations. It does not page or schedule operators.
