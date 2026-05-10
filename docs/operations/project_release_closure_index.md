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
