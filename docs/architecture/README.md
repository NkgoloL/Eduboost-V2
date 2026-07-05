---
title: "Architecture Documentation"
status: active
owner: architecture
reviewers: [backend, frontend, security, operations]
audience: developer
source_of_truth: true
supersedes: []
superseded_by: null
last_reviewed: 2026-06-23
review_interval_days: 60
evidence_command: "make docs-housekeeping-stage4-check"
code_anchors: [docs/architecture/README.md]
---

# Architecture Documentation

Architecture documents must describe the real EduBoost V2 implementation and must not import stale concepts from unrelated systems.

Canonical architectural claims should be anchored to code paths, OpenAPI generation, migration checks, or ADRs.

<!-- KG000_FORMAL_ROADMAP_APPROVAL:start -->
## Knowledge Graph architecture documents

- [Knowledge Graph Learning-State Architecture](knowledge_graph_learning_state_architecture.md)
- [Knowledge Graph Data Model](knowledge_graph_data_model.md)
- [Knowledge Graph Transition Plan](knowledge_graph_transition_plan.md)

KG-0 records these documents as architecture authority only; runtime KG implementation remains unauthorised until a later approved KG slice.
<!-- KG000_FORMAL_ROADMAP_APPROVAL:end -->
