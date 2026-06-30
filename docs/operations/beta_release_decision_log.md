# Beta Release Decision Log

## Purpose

The beta release decision log records approval, rejection, rollback, and
post-deploy verification decisions for the controlled staging/beta release path.

## Decision Record Template

| Field | Value |
| --- | --- |
| Decision ID | pending |
| Decision Type | approve / reject / rollback / defer |
| Release Candidate | pending |
| Commit SHA | pending |
| Decision Owner | pending |
| Decision Time UTC | pending |
| Evidence Bundle | docs/operations/beta_release_evidence_bundle.md |
| Release State Snapshot | docs/operations/release_state_snapshot.md |
| Final Verification Bundle | docs/operations/final_release_verification_bundle.md |
| Rollback Runbook | docs/operations/beta_rollback_runbook.md |
| Post-Deploy Smoke Checklist | docs/operations/post_deploy_staging_smoke_checklist.md |
| Notes | pending |

## Required Decision Rules

- approval decision must reference the release candidate and commit SHA
- rejection decision must record the failed check or missing approval
- rollback decision must reference the rollback runbook
- defer decision must record the owner and next action
- post-deploy verification outcome must be recorded after deployment
- decision log does not replace platform workflow logs

## Boundary

This log records decisions. It does not approve release automatically and does not execute deployment or rollback.

## Command

```bash
make beta-release-decision-log-check
```

## Feedback Issues Acceptance Evidence

- `docs/operations/beta_feedback_intake_contract.md`
- `docs/operations/beta_known_issues_register.md`
- `docs/operations/beta_acceptance_exit_criteria.md`
