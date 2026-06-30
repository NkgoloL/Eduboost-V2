# Post-Merge Release Handoff Checklist

## Purpose

This checklist defines the handoff required after the release-readiness PR is
merged but before any staging or beta release action is executed.

## Required Handoff Inputs

- merged commit SHA recorded
- release state snapshot generated after merge
- final PR merge readiness check passed before merge
- final release verification bundle passed before merge
- beta release evidence bundle linked
- Cluster H closure report linked
- rollback runbook linked
- post-deploy staging smoke checklist linked
- release candidate tag manifest linked
- manual approval workflow location documented

## Required Handoff Owners

- release operator
- technical approver
- privacy/POPIA approver
- rollback owner
- post-deploy verification owner
- incident contact

## Required Post-Merge Actions

- verify remote default branch contains merged commit
- regenerate release state snapshot from merged branch
- confirm beta sign-off manifest still references intended commit
- confirm release candidate tag has not been pushed before approval
- confirm deployment platform workflow logs are retained
- record approval outcome in beta release decision log

## Boundary

Post-merge handoff does not execute deployment, tagging, approval, or production launch.

## Command

```bash
make post-merge-release-handoff-check
```

## Post-Merge Governance Handoff Evidence

- `docs/operations/post_merge_release_handoff_checklist.md`
- `docs/operations/release_owner_accountability_matrix.md`
- `docs/operations/beta_release_decision_log.md`

## Audit Attestation Rollup Evidence

- `docs/operations/release_audit_trail_index.md`
- `docs/operations/beta_release_closure_attestation.md`
- `docs/operations/final_cluster_h_closeout_rollup.md`
