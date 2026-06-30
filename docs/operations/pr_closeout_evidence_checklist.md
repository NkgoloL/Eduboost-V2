# PR Closeout Evidence Checklist

## Purpose

A release-readiness PR should close with reproducible evidence, a clean branch,
and a reviewable summary of scope.

## Required Closeout Evidence

- final commit includes source, docs, workflow, and test evidence
- generated local artifacts are excluded
- branch is synchronized with remote
- release readiness checks are green
- Cluster H closure check is green
- PR integration summary is updated
- project status is updated
- final verification command list is included in PR body
- known non-goals and beta boundaries are documented
- rollback and post-deploy owners are documented

## Required Final Commands

```bash
make generated-artifact-hygiene-check
make branch-sync-rebase-checklist-check
make beta-release-final-checklist-check
make project-release-closure-index-check
make cluster-h-release-readiness-check
make cluster-h-closure-check
```

## PR Body Evidence Sections

- Summary
- Verification
- Release Boundary
- Rollback
- Evidence Index
- Known Follow-Ups

## Command

```bash
make pr-closeout-evidence-checklist-check
```

## Release Execution PR Verification Evidence

- `docs/operations/beta_release_execution_plan.md`
- `docs/operations/beta_release_pr_body.md`
- `docs/operations/final_release_verification_bundle.md`

## Release State Consistency Merge Readiness Evidence

- `docs/operations/release_state_snapshot.md`
- `docs/operations/beta_evidence_consistency_guard.md`
- `docs/operations/final_pr_merge_readiness_contract.md`

## Final Verification Command

- make final-release-verification
