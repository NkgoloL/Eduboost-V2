---
title: "KG-2 Target Graph Schema"
status: active
owner: knowledge-graph
reviewers: [architecture, product, privacy, curriculum, engineering]
audience: developer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: '2026-09-23'
review_interval_days: 90
evidence_command: 'make kg002-target-graph-generation-check'
code_anchors: [scripts/roadmap_reconciliation/verify_kg002_target_graph_generation.py, data/knowledge_graph/caps_graph_foundation/grade4_mathematics_caps_graph.json]
---
# KG-2 Target Graph Schema

The generated target graph contains:

- `target_states`: expected mastery targets per approved CAPS node.
- `target_edges`: prerequisite, containment, and assessment relationships between target states.
- `policies`: mastery/confidence thresholds, priority weights, and pacing windows.
- `source`: KG-1 CAPS graph checksum and provenance.
- `boundary`: false authorization flags.

Each target state must include `caps_node_key`, `caps_node_id`, `required_mastery`,
`required_confidence`, `priority`, `pacing_window`, source references, and review
status.
