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

## Release Gate

- `make staging-release-gate-check`
- `make release-evidence-artifacts-check`
- `make cluster-d-closure-check`
