---
title: "KG-1 CAPS Graph Schema"
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

# KG-1 CAPS Graph Schema

The KG-1 graph artifact contains:

- `graph_id`
- `graph_version`
- `scope`
- `source`
- `review`
- `counts`
- `nodes`
- `edges`
- `boundary`

## Node fields

Each node must include `node_id`, `node_key`, `node_type`, `label`, `description`, `grade`, `subject`, `term`, `source_ref`, `source_sha256`, `review_status`, `version`, and `metadata`.

## Edge fields

Each edge must include `edge_id`, `source_node_key`, `target_node_key`, `edge_type`, `label`, `source_ref`, `source_sha256`, `review_status`, `version`, and `metadata`.

## Review status

Production-eligible KG-1 nodes and edges are emitted with `review_status: approved` because they are derived from the reviewed Grade 4 Mathematics CAPS topic map. Later gates must preserve or supersede this review status explicitly.
