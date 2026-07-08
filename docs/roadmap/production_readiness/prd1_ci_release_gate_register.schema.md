# PRD-1 CI/Release-Gate Register Schema

The PRD-1 register is stored at:

`docs/roadmap/production_readiness/prd1_ci_release_gate_register.json`

Required top-level fields:

| Field | Meaning |
|---|---|
| `schema_version` | Must be `prd1-ci-release-gate-register/v1`. |
| `stream_id` | Must be `PRD-1-CI-RELEASE-GATE-CONVERGENCE`. |
| `parent_stream_id` | Must be `PRD-PRODUCTION-READINESS`. |
| `goal` | Required CI and release gate convergence goal. |
| `last_recorded_item` | Last recorded PRD-1.x slice. |
| `next_authorised_item` | Next authorised PRD-1.x slice. |
| `prd1_sequence` | PRD-1.0 through PRD-1.9 authority sequence. |
| `authority_boundaries` | Explicitly closed release/beta/billing/live/KG boundaries. |
| `implementation_boundaries` | Explicit no-change status for PRD-1.0. |

PRD-1.0 terminal state requires:

- `last_recorded_item: PRD-1.0`
- `next_authorised_item: PRD-1.1`
- `PRD-1.0` sequence entry status `recorded`
- `PRD-1.1` sequence entry authorised `true`
- production release, deployment, release tags, beta, live learner traffic, billing, payments, and PRD-2 implementation all unauthorised
