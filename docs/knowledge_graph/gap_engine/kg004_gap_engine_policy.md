---
title: "KG-4 Gap Engine Policy"
status: authority-recorded
owner: knowledge-graph
---

# KG-4 Gap Engine Policy

The KG-4 gap engine is a deterministic advisory read-model that compares KG-3 learner shadow states against KG-2 target states.

## Rules

1. Only KG-3 shadow states with `shadow_mode: true` and `no_live_learner_data: true` may be used.
2. Only non-mastered statuses are converted into gap items: `shadow_gap` and `shadow_developing`.
3. Each gap item must preserve source provenance from the KG-3 shadow state and the KG-2 target graph.
4. Recommendations are advisory only and cannot replace the current learner-facing progress/mastery authority.
5. No database schema migration, learner graph persistence, or runtime KG authority switch is authorised by KG-4.
