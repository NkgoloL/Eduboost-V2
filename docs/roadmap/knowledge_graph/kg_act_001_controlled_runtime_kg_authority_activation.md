---
title: "KG-ACT-001 Controlled Runtime KG Authority Activation"
status: authority
owner: knowledge-graph
---

# KG-ACT-001 Controlled Runtime KG Authority Activation

KG-ACT-001 is the explicit activation gate after KG-7 readiness. It is the
first KG package allowed to mark the repository-local KG authority switch as
authorised and executed, but only after the final go/no-go, feature flag,
rollback, learner safety, and POPIA boundary evidence files are present.

## Preconditions

- KG-7 authority-switch readiness must be valid.
- KG-7 must remain readiness-only before this gate.
- No production deployment, public beta launch, billing launch, or release tag
  is authorised by this gate.

## Outcome

Valid KG-ACT-001 evidence unblocks KG-8 post-switch optimisation and scale
review. KG-8 remains blocked until `kg8_post_switch_optimisation_unblocked`
is true in `kg_act_001_controlled_runtime_kg_authority_activation_record.json`.
