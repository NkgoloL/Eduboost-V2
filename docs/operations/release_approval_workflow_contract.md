---
title: Release Approval Workflow Contract
status: active
owner: operations
reviewers: [operations, security, release-management]
audience: operator
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-06
review_interval_days: 90
evidence_command: make docs-housekeeping-stage7-check
code_anchors: [docs/operations, docs/documentation/stage_7_release_archive_backlog_codemaps_governance.md]
---

# Release Approval Workflow Contract

## Purpose

Beta release approval must be explicit, traceable, and tied to a release
candidate, commit, evidence bundle, and rollback owner.

## Required Approval Inputs

- release candidate identifier
- target environment
- commit SHA
- beta release evidence bundle
- beta sign-off manifest
- staging smoke evidence manifest
- rollback runbook
- post-deploy smoke checklist

## Required Approval Gates

- manual workflow dispatch
- release evidence bundle generated
- beta sign-off manifest generated
- staging smoke manifest generated
- readiness checks pass
- rollback runbook check passes
- post-deploy smoke checklist check passes

## Required Approval Outputs

- approval workflow run URL
- release candidate identifier
- approved commit SHA
- approver identity from platform audit trail
- deployment target
- rollback owner
- post-deploy verification owner

## Command

```bash
make release-approval-workflow-contract-check
```
