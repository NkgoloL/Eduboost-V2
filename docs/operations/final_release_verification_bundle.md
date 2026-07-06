---
title: Final Release Verification Bundle
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

# Final Release Verification Bundle

## Purpose

The final release verification bundle provides one command target that executes
the final CI-safe release-readiness checks for the staging/beta layer.

## Included Commands

```bash
make generated-artifact-hygiene-check
make branch-sync-rebase-checklist-check
make beta-release-final-checklist-check
make project-release-closure-index-check
make beta-release-execution-plan-check
make beta-pr-body-check
make cluster-h-release-readiness-check
make cluster-h-closure-check
```

## Boundary

This bundle is intentionally CI-safe and evidence-focused. Runtime deployment,
manual approval, release tagging, and post-deploy browser execution remain
operator-controlled actions.

## Command

```bash
make final-release-verification
```

## Release State Consistency Merge Readiness Evidence

- `docs/operations/release_state_snapshot.md`
- `docs/operations/beta_evidence_consistency_guard.md`
- `docs/operations/final_pr_merge_readiness_contract.md`
