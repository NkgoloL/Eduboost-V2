# Project Evidence Index

## Runtime/API Contract

- `docs/pr/PR-002R_BACKEND_RUNTIME_API_CONTRACT.md`
- `docs/openapi.json`
- `docs/route_inventory.md`

## Authorization Contract

- `docs/security/PHASE2_AUTHORIZATION_CLOSURE.md`
- `docs/security/learner_authz_matrix.md`

## POPIA Consent/Audit Contract

- `docs/security/POPIA_CONSENT_GATE_CLOSURE.md`
- `docs/security/popia_consent_boundary_matrix.md`
- `docs/security/popia_consent_gate_inventory.md`

## CI/Deployment/Environment Contract

- `docs/operations/CLUSTER_D_CLOSURE.md`
- `docs/operations/deployment_readiness_checklist.md`
- `docs/operations/release_evidence_manifest.md`
- `docs/operations/staging_release_gate.md`
- `.github/workflows/cluster-d-ci.yml`


## Data Resilience Contract

- `docs/operations/CLUSTER_E_CLOSURE.md`
- `docs/operations/data_resilience_evidence_index.md`
- `docs/operations/database_backup_manifest.md`
- `docs/operations/database_restore_evidence.md`
- `.github/workflows/cluster-e-data-resilience.yml`


## AI/CAPS Safety Contract

- `docs/ai/CLUSTER_F_CLOSURE.md`
- `docs/ai/ai_safety_evidence_index.md`
- `.github/workflows/cluster-f-ai-safety.yml`


## Frontend Journey Contract

- `docs/frontend/CLUSTER_G_CLOSURE.md`
- `docs/frontend/frontend_evidence_index.md`
- `.github/workflows/cluster-g-frontend.yml`
- `.github/workflows/frontend-e2e-opt-in.yml`

## Release Gate

- `make staging-release-gate-check`
- `make release-evidence-artifacts-check`
- `make cluster-d-closure-check`
- `make cluster-e-closure-check`
- `make cluster-f-closure-check`
- `make cluster-g-closure-check`

## Final Project Closure Evidence

- `docs/operations/release_artifact_retention_contract.md`
- `docs/operations/beta_release_final_checklist.md`
- `docs/operations/project_release_closure_index.md`
