# Staging Release Gate

## Purpose

The staging release gate records the minimum evidence required before promoting
EduBoost V2 to a staging environment.

## Required Commands

- `make runtime-check`
- `make openapi-check`
- `make route-inventory-check`
- `make pr002r-check`
- `make phase2-authz-closure`
- `make popia-consent-closure-check`
- `make cluster-d-closure-check`
- `python3 scripts/generate_release_evidence_manifest.py`

## Required Artifacts

- `docs/operations/release_evidence_manifest.md`
- `docs/operations/deployment_readiness_checklist.md`
- `docs/security/POPIA_CONSENT_GATE_CLOSURE.md`
- `docs/security/PHASE2_AUTHORIZATION_CLOSURE.md`
- `docs/openapi.json`
- `docs/route_inventory.md`

## Production Promotion Constraint

Production promotion is blocked unless staging evidence is attached to the PR
or release record.
