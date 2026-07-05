---
title: "Dashboard and Runbook Contract"
status: "active-runbook"
owner: "operations"
reviewers: ["operations", "security", "backend"]
audience: "operator"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-06-24"
review_interval_days: 60
evidence_command: "make docs-housekeeping-stage5-check"
code_anchors: "[app/api_v2.py, docs/observability]"
---

# Dashboard and Runbook Contract

## Purpose

This contract defines dashboard and runbook requirements for production observability.

## Required Dashboards

- Production API Overview
- AI Provider Safety and Latency
- Notifications and Billing Operations
- POPIA Privacy Operations
- Frontend Experience and Errors
- Database Performance and Saturation

## Required Dashboard Panels

- traffic
- latency
- errors
- saturation
- SLO burn
- retry count
- dead-letter count
- provider failures

## Required Runbook Sections

- symptom
- impact
- dashboard links
- likely causes
- immediate mitigation
- rollback criteria
- escalation owner
- post-incident evidence

## Boundary

This contract records dashboard and runbook readiness. It does not create live dashboards or execute incident response.
