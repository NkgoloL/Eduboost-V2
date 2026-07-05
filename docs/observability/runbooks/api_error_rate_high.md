---
title: "Runbook: api_error_rate_high"
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

# Runbook: api_error_rate_high

## Symptom

Alert api_error_rate_high fired.

## Impact

Potential degradation in production service reliability, privacy operations, provider integrations, or support workflows.

## Immediate Mitigation

- Confirm alert route owner.
- Open the relevant dashboard.
- Check recent deploys and provider status.
- Apply documented rollback criteria where applicable.
- Record post-incident evidence.

## Escalation Owner

Engineering, privacy, release owner, or support route based on alert metadata.

## Boundary

This runbook is repository-side evidence. It does not execute remediation automatically.
