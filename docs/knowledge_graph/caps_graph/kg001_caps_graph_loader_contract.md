---
title: "KG-1 CAPS Graph Loader Contract"
status: active
owner: knowledge-graph
reviewers: [architecture, curriculum, engineering, privacy]
audience: developer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-05
review_interval_days: 60
evidence_command: make kg001-caps-graph-foundation-check
code_anchors: []
---

# KG-1 CAPS Graph Loader Contract

The KG-1 loader is `scripts/knowledge_graph/build_kg001_caps_graph_foundation.py`.

## Required input

`data/caps/topic_maps/caps_topic_map_grade4_maths.json`

## Required output

`data/knowledge_graph/caps_graph_foundation/grade4_mathematics_caps_graph.json`

## Contract

- Generate deterministic node and edge identifiers from stable graph keys.
- Preserve source reference and source SHA-256 on every node and edge.
- Fail if duplicate node keys or orphan edges are detected.
- Emit a summary artifact with node/edge counts and source checksum.
- Keep runtime KG authority switch authorised: false.
