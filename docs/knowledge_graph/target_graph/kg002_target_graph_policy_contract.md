---
title: "KG-2 Target Graph Policy Contract"
status: active
owner: knowledge-graph
reviewers: [architecture, product, privacy, curriculum, engineering]
audience: developer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-05
review_interval_days: 60
evidence_command: make kg002-target-graph-generation-check
code_anchors: []
---


# KG-2 Target Graph Policy Contract

Target states use deterministic policy values:

| Target type | Required mastery | Required confidence |
|---|---:|---:|
| topic | 0.75 | 0.70 |
| subtopic | 0.80 | 0.75 |
| assessment_statement | 0.85 | 0.80 |

Priority weights are term-aware. Term 1 has the highest default priority because
it contributes prerequisites for the rest of the year. The policy is intentionally
simple and reviewable; KG-3 and later gates may compare it with learner evidence,
but KG-2 does not update learner state.
