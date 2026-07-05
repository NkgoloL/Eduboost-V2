---
title: "Runbook: API Outage"
status: "active-runbook"
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

# Runbook: API Outage

## Detection

- confirm alert
- check dashboard
- review recent deploy

## Triage

- classify severity
- assign incident commander
- identify affected routes

## Mitigation

- scale service
- rollback recent release
- disable failing dependency

## Recovery

- verify health checks
- run smoke tests

## Verification

- confirm API availability
- confirm error rate normal

## Rollback Criteria

- error rate remains elevated
- smoke tests fail
- customer impact persists

## Boundary

This runbook records API outage response readiness. It does not execute remediation.
