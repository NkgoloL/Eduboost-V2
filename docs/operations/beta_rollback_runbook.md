---
title: Beta Rollback Runbook
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

# Beta Rollback Runbook

## Purpose

This runbook defines the minimum rollback procedure for a controlled staging or
beta release.

## Rollback Triggers

- material runtime import failure
- OpenAPI contract drift
- authentication or authorization regression
- consent gate or POPIA audit regression
- database backup/restore integrity failure
- AI safety fixture or prompt leakage failure
- frontend journey, denial UX, or accessibility regression
- elevated error rate after deployment
- manual release owner decision

## Rollback Preconditions

- last known good commit is identified
- database backup manifest is available
- restore evidence is available
- rollback owner is assigned
- user communication owner is assigned
- incident record is opened
- monitoring dashboard is available

## Rollback Procedure

1. Freeze new deployments.
2. Record current commit, release candidate, and environment.
3. Confirm last known good artifact.
4. Confirm database backup/restore boundary.
5. Deploy last known good artifact or revert the release commit.
6. Run staging smoke checks.
7. Verify learner and parent journey availability.
8. Verify consent/audit behavior.
9. Record rollback evidence.
10. Communicate status to release stakeholders.

## Post-Rollback Evidence

- rollback timestamp
- rollback owner
- previous commit
- restored commit
- database action taken
- staging smoke result
- learner journey result
- parent journey result
- consent/audit result
- incident reference

## Command

```bash
make beta-rollback-runbook-check
```
