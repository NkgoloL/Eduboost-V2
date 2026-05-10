# Beta Release Final Checklist

## Purpose

This checklist is the final pre-approval checklist for a controlled EduBoost V2
staging or beta release.

## Required Pre-Approval Checks

- working tree is clean except intentional release evidence files
- branch is rebased on remote target branch
- OpenAPI drift check passes
- staging release gate check passes
- release evidence artifacts check passes
- Cluster C POPIA consent closure check passes
- Cluster D deployment closure check passes
- Cluster E data resilience closure check passes
- Cluster F AI safety closure check passes
- Cluster G frontend journey closure check passes
- Cluster H closure check passes

## Required Generated Evidence

- staging smoke evidence manifest generated
- beta sign-off manifest generated
- beta release evidence bundle generated
- release candidate tag manifest generated

## Required Manual Confirmations

- technical lead approval recorded
- privacy/POPIA approval recorded
- data resilience approval recorded
- AI safety approval recorded
- frontend journey approval recorded
- rollback owner approval recorded
- post-deploy verification owner assigned

## Explicit Non-Goals

- no unrestricted production launch
- no real learner data migration without a separate approved plan
- no release tag push before approval
- no generated `coverage.xml` conflict carried into release commit

## Command

```bash
make beta-release-final-checklist-check
```

## Release Hygiene and PR Closeout Evidence

- `docs/operations/generated_artifact_hygiene_contract.md`
- `docs/operations/branch_sync_rebase_checklist.md`
- `docs/operations/pr_closeout_evidence_checklist.md`

## Release Execution PR Verification Evidence

- `docs/operations/beta_release_execution_plan.md`
- `docs/operations/beta_release_pr_body.md`
- `docs/operations/final_release_verification_bundle.md`
