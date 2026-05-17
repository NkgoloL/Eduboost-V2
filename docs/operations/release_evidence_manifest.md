# Release Evidence Manifest

Generated: `2026-05-17T09:34:49Z`
Branch: `codex/production_readiness`
Commit: `7edd5965c75337cddf07bac3852e53bc4ff5f689`

## Required Evidence Commands

| Area | Command | Evidence Status |
| --- | --- | --- |
| Runtime contract | `make runtime-check` | pending |
| OpenAPI drift | `make openapi-check` | pending |
| Route inventory | `make route-inventory-check` | pending |
| PR-002R evidence | `make pr002r-check` | pending |
| Phase 2 authorization | `make phase2-authz-closure` | pending |
| POPIA consent/audit | `make popia-consent-closure-check` | pending |
| Cluster D environment/deployment | `make cluster-d-closure-check` | pending |
| Cluster E data resilience | `make cluster-e-closure-check` | pending |
| Cluster F AI safety | `make cluster-f-closure-check` | pending |
| Cluster G frontend journey | `make cluster-g-closure-check` | pending |

## Release Evidence Notes

Attach command output for each row before staging or production promotion.

## Artifact References

- `docs/openapi.json`
- `docs/route_inventory.md`
- `docs/security/PHASE2_AUTHORIZATION_CLOSURE.md`
- `docs/security/POPIA_CONSENT_GATE_CLOSURE.md`
- `docs/operations/deployment_readiness_checklist.md`
- `docs/operations/cluster_d_closure_check.md`
