---
title: "KG-4 Intervention Planner Contract"
status: authority-recorded
owner: knowledge-graph
---

# KG-4 Intervention Planner Contract

The intervention planner emits one primary advisory recommendation per KG-4 gap item.

## Recommendation classes

- `reteach_with_guided_practice`
- `prerequisite_review_and_mini_lesson`
- `targeted_practice_with_feedback`
- `confidence_check_and_spaced_practice`

## Contract

Recommendations must include:

- learner alias
- target key
- gap key
- intervention type
- priority bucket
- priority score
- rationale
- expected follow-up evidence event type
- source reference and checksum

The planner does not schedule, send, or apply interventions to live learners in KG-4.
