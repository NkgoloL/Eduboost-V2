---
title: "Operations — Beta Evidence Consistency Guard"
status: "active"
owner: "operations"
reviewers: ['operations', 'sre', 'engineering']
audience: "internal"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-09-13"
review_interval_days: 90
evidence_command: "make docs-housekeeping-check"
code_anchors: "[]"
---
# Beta Evidence Consistency Guard

## Purpose

The beta evidence consistency guard verifies that final release documents agree
on the same closure artifacts, verification commands, and beta boundaries.

## Required Shared References

- `docs/operations/CLUSTER_H_CLOSURE.md`
- `docs/operations/beta_release_evidence_bundle.md`
- `docs/operations/project_release_closure_index.md`
- `docs/operations/final_release_verification_bundle.md`
- `docs/operations/beta_release_pr_body.md`
- `docs/operations/beta_rollback_runbook.md`

## Required Shared Commands

- `make final-release-verification`
- `make cluster-h-release-readiness-check`
- `make cluster-h-closure-check`
- `make generated-artifact-hygiene-check`
- `make branch-sync-rebase-checklist-check`

## Required Shared Boundary

- controlled staging/beta validation only
- does not authorize unrestricted production launch
- release tag push requires manual approval
- generated coverage output is not release evidence

## Command

```bash
make beta-evidence-consistency-check
```
