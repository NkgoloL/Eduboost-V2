---
title: "KG-7 Authority Switch and Legacy Cleanup"
status: authority-approved-pending-evidence
owner: knowledge-graph
---

# KG-7 — Authority Switch and Legacy Cleanup

KG-7 records the authority-switch readiness and legacy-cleanup control package
for the EduBoost knowledge-graph roadmap.

This slice is deliberately conservative: it prepares the authority switch,
legacy compatibility projections, cleanup tasks, and rollback controls, but it
**does not execute** a runtime authority switch, mutate database schema, or make
any learner-facing model change.

## Preconditions

- KG-6 product-alignment evidence is valid.
- Product-alignment data remains preview-only, synthetic, and human-review-gated.
- No live learner data or guardian PII is used.

## Deliverables

- Authority-switch readiness artifact.
- Feature-flag control contract.
- Legacy projection mapping contract.
- Legacy cleanup plan.
- Rollback boundary.
- Evidence verifier and capture script.

## Boundary

The following remain false until a separate activation approval exists:

- `runtime_kg_authority_switch_authorised`
- `authority_switch_executed`
- `legacy_cleanup_executed`
- `database_schema_migration_authorised`
- `learner_facing_model_change_authorised`
- `production_release_authorised`
- `deployment_authorised`
- `public_beta_authorised`
