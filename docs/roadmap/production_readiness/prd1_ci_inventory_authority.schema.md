# PRD-1.1 CI Inventory Authority Schema

The PRD-1.1 inventory snapshot is stored at:

`docs/roadmap/production_readiness/prd1_ci_inventory_authority.json`

Required top-level fields:

| Field | Meaning |
|---|---|
| `schema_version` | Must be `prd1-ci-inventory-authority/v1`. |
| `prd_id` | Must be `PRD-1.1`. |
| `stream_id` | Must be `PRD-1-CI-RELEASE-GATE-CONVERGENCE`. |
| `workflow_inventory` | Per-workflow inventory of branch, release, deployment, pytest, and OpenAPI references. |
| `makefile_inventory` | Makefile target and command-reference inventory. |
| `openapi_inventory` | Presence and path inventory for OpenAPI artifacts. |
| `branch_protection_inventory` | Local documentation/configuration references to branch protection and required checks. |
| `summary` | Count-level summary used by PRD-1.2 classification. |
| `authority_boundaries` | Explicitly closed release/beta/billing/live/KG boundaries. |
| `implementation_boundaries` | Explicit no-change status for PRD-1.1. |

PRD-1.1 terminal state requires:

- `last_recorded_item: PRD-1.1`
- `next_authorised_item: PRD-1.2`
- `PRD-1.1` sequence entry status `recorded`
- `PRD-1.2` sequence entry authorised `true`
- CI inventory evidence recorded
- no required-check classification performed
- no workflow canonicalisation performed
- no release gate enforcement performed
