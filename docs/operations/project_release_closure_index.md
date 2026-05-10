# Project Release Closure Index

## Purpose

This index provides the project-wide release closure map for EduBoost V2 through
the final staging and beta-release evidence layer.

## Backend and API Closure

- `docs/openapi.json`
- `docs/api_v2.md`
- `docs/operations/release_evidence_manifest.md`

## Authorization and Consent Closure

- `docs/security/authorization_boundary.md`
- `docs/security/POPIA_CONSENT_GATE_CLOSURE.md`
- `docs/security/popia_consent_boundary_matrix.md`

## Deployment and Environment Closure

- `docs/operations/CLUSTER_D_CLOSURE.md`
- `docs/operations/deployment_readiness_checklist.md`
- `docs/operations/staging_release_gate.md`

## Data Resilience Closure

- `docs/operations/CLUSTER_E_CLOSURE.md`
- `docs/operations/data_resilience_evidence_index.md`
- `docs/operations/database_restore_drill.md`

## AI Safety Closure

- `docs/ai/CLUSTER_F_CLOSURE.md`
- `docs/ai/ai_safety_evidence_index.md`
- `docs/ai/ai_fixture_coverage_matrix.md`

## Frontend Journey Closure

- `docs/frontend/CLUSTER_G_CLOSURE.md`
- `docs/frontend/frontend_evidence_index.md`

## Staging and Beta Release Closure

- `docs/operations/CLUSTER_H_CLOSURE.md`
- `docs/operations/beta_release_readiness_contract.md`
- `docs/operations/beta_release_evidence_bundle.md`
- `docs/operations/beta_signoff_manifest.md`
- `docs/operations/beta_rollback_runbook.md`
- `docs/operations/beta_release_final_checklist.md`
- `docs/operations/release_artifact_retention_contract.md`
- `docs/operations/project_release_closure_index.md`

## Required Final Commands

```bash
make staging-release-gate-check
make release-evidence-artifacts-check
make cluster-g-closure-check
make cluster-h-closure-check
make project-release-closure-index-check
```

## Release Hygiene and PR Closeout Evidence

- `docs/operations/generated_artifact_hygiene_contract.md`
- `docs/operations/branch_sync_rebase_checklist.md`
- `docs/operations/pr_closeout_evidence_checklist.md`

## Release Execution PR Verification Evidence

- `docs/operations/beta_release_execution_plan.md`
- `docs/operations/beta_release_pr_body.md`
- `docs/operations/final_release_verification_bundle.md`

## Release State Consistency Merge Readiness Evidence

- `docs/operations/release_state_snapshot.md`
- `docs/operations/beta_evidence_consistency_guard.md`
- `docs/operations/final_pr_merge_readiness_contract.md`

## Post-Merge Governance Handoff Evidence

- `docs/operations/post_merge_release_handoff_checklist.md`
- `docs/operations/release_owner_accountability_matrix.md`
- `docs/operations/beta_release_decision_log.md`

## Audit Attestation Rollup Evidence

- `docs/operations/release_audit_trail_index.md`
- `docs/operations/beta_release_closure_attestation.md`
- `docs/operations/final_cluster_h_closeout_rollup.md`

## Governance Seal Terminal Closure Evidence

- `docs/operations/beta_governance_seal_checklist.md`
- `docs/operations/beta_release_final_index.md`
- `docs/operations/cluster_h_terminal_closure_assertion.md`

## Post-Terminal Handoff Archive Audit Evidence

- `docs/operations/final_release_handoff_package.md`
- `docs/operations/evidence_archive_completeness_guard.md`
- `docs/operations/post_terminal_audit_readiness_assertion.md`

## Execution Guardrail Closeout Checksum Evidence

- `docs/operations/release_owner_execution_guardrail.md`
- `docs/operations/final_project_closeout_attestation.md`
- `docs/operations/cluster_h_release_evidence_checksum_index.md`
