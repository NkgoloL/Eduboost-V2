---
title: "KG-3 Learner Graph Shadow Schema"
status: active
owner: knowledge-graph
---

# KG-3 Learner Graph Shadow Schema

The learner shadow graph contains:

- `learner_profiles`: synthetic learner aliases only.
- `learner_shadow_states`: one learner-target state per synthetic learner and KG-2 target state.
- `shadow_evidence_events`: synthetic observations supporting each shadow state.
- `shadow_edges`: edges from synthetic learner aliases to shadow states and from shadow states to KG-2 target keys.

Each learner shadow state must include:

- `learner_alias`
- `target_key`
- `required_mastery`
- `required_confidence`
- `observed_mastery`
- `observed_confidence`
- `mastery_gap`
- `shadow_status`
- `source_sha256`
- `target_graph_sha256`
- `shadow_mode: true`
- `no_live_learner_data: true`
