---
title: "KG-4 Gap Engine Schema"
status: authority-recorded
owner: knowledge-graph
---

# KG-4 Gap Engine Schema

The generated KG-4 artifact contains:

- `learner_gap_profiles`: synthetic learner-level summary records.
- `gap_items`: non-mastered learner-target state gaps.
- `intervention_recommendations`: advisory recommended interventions.
- `planner_edges`: source-grounded relationships between shadow states, gap items, and interventions.

Required flags on all gap and intervention records:

```text
advisory_only: true
shadow_mode: true
no_live_learner_data: true
review_status: approved
```
