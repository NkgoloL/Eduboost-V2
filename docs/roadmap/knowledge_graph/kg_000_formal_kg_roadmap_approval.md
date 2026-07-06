---
title: "KG-0 Formal KG Roadmap Approval"
status: active
owner: roadmap-governance
reviewers: [architecture, product, privacy, curriculum, engineering]
audience: developer
source_of_truth: true
supersedes: []
superseded_by: null
last_reviewed: 2026-07-05
review_interval_days: 60
evidence_command: make kg000-formal-kg-roadmap-approval-check
code_anchors: []
---


# KG-0 — Formal KG Roadmap Approval

## Purpose

KG-0 formally opens the EduBoost Knowledge Graph roadmap after the reconciled RR register was closed through `RR-018` and final roadmap reconciliation closure.

This slice does not implement runtime knowledge graph behaviour. It records the architecture decision, roadmap, risk register, verification plan, and boundary controls required before KG implementation work may begin.

## Scope

KG-0 approves the knowledge graph roadmap as the next roadmap stream by landing and indexing:

- `docs/adr/ADR-036-knowledge-graph-learning-state-core.md`
- `docs/architecture/knowledge_graph_learning_state_architecture.md`
- `docs/architecture/knowledge_graph_data_model.md`
- `docs/architecture/knowledge_graph_transition_plan.md`
- `docs/product/knowledge_graph_learning_model_brief.md`
- `docs/caps/knowledge_graph_mapping_contract.md`
- `docs/ai/knowledge_graph_grounding_contract.md`
- `docs/security/knowledge_graph_privacy_and_popia_contract.md`
- `docs/testing/knowledge_graph_verification_plan.md`
- `docs/roadmap/knowledge_graph_pivot_roadmap.md`
- `docs/roadmap/risk_register_knowledge_graph_pivot.md`
- `docs/roadmap/knowledge_graph/kg_implementation_roadmap.md`
- `docs/roadmap/knowledge_graph/kg_roadmap_register.json`

## Exit criteria

- Final RR closure remains valid.
- KG formalisation package docs exist and are indexed.
- KG roadmap register contains `KG-0` through `KG-8`.
- ADR-030 is present and indexed.
- No runtime KG implementation is claimed.
- No database migration, learner-facing model change, runtime KG authority switch, production release, deployment, release tag, public beta, billing launch, or live payment processing is authorised.

## Next-work rule

After KG-0 closes, the next implementation slice is `KG-1 — CAPS graph foundation` unless a new approved roadmap amendment changes the sequence.

KG-1 must still be treated as a controlled implementation slice with its own authority, evidence, and boundaries.
