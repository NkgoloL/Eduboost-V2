---
title: "KG-2 Target Graph Runtime Boundary"
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


# KG-2 Target Graph Runtime Boundary

- runtime kg implementation claimed: false
- runtime kg authority switch authorised: false
- database schema migration authorised: false
- learner facing model change authorised: false
- learner graph implementation authorised: false
- target graph runtime authority authorised: false
- production release authorised: false
- deployment authorised: false
- release tag authorised: false
- public beta authorised: false

KG-2 creates a target graph read model only. It does not become authoritative for
learner progress, lesson selection, tutor behaviour, or parent reporting.
