---
title: Beta Release Communications Plan
status: active-control
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

# Beta Release Communications Plan

## Purpose

The beta release communications plan defines the minimum communication evidence
required before, during, and after a controlled EduBoost V2 staging/beta release.

## Required Audiences

- release operator
- technical approver
- privacy/POPIA approver
- rollback owner
- post-deploy verification owner
- incident contact
- beta support contact
- project owner

## Required Pre-Release Communications

- release candidate identifier
- merged commit SHA
- release window
- beta boundary and non-production scope
- rollback owner and rollback runbook link
- post-deploy staging smoke checklist link
- incident contact
- support contact
- known follow-ups

## Required During-Release Communications

- release start notification
- deployment status notification
- smoke verification status notification
- rollback trigger notification if applicable
- approval or rejection outcome

## Required Post-Release Communications

- release completion or rollback outcome
- beta release decision log update
- release audit trail index link
- post-deploy smoke checklist result
- follow-up owner assignment

## Boundary

The communications plan informs stakeholders. It does not approve release, execute deployment, create release tags, or replace the beta release decision log.

## Command

```bash
make beta-release-communications-plan-check
```
