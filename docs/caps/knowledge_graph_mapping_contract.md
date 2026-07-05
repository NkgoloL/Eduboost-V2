---
title: "Knowledge Graph CAPS Mapping Contract"
status: active
owner: curriculum
reviewers: [architecture, product, privacy, curriculum, engineering]
audience: developer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-05
review_interval_days: 60
evidence_command: make kg000-formal-kg-roadmap-approval-check
code_anchors: []
---

# CAPS Knowledge Graph Mapping Contract

## Purpose

This contract defines how CAPS source material becomes graph nodes and edges in EduBoost.

## Source authority

Only approved CAPS source documents and reviewed extraction outputs may create authoritative curriculum graph records.

A mapping is not production-grade unless it has source document identifier, source page or section reference, source checksum, extraction method, review status, reviewer or approval manifest, and stable graph key.

## Node contract

Each graph node must include stable `node_key`, `node_type`, label, grade/subject/term metadata where applicable, source reference, review status, and creation/update timestamps.

## Edge contract

Each graph edge must include source node, target node, edge type, review status, source or rationale, and optional weight.

## Required edge types

| Edge type | Meaning |
|---|---|
| `contains` | A parent curriculum object contains a child object. |
| `belongs_to` | A child object belongs to a parent object. |
| `prerequisite_of` | One skill is needed before another. |
| `supports` | A skill supports another skill or outcome. |
| `assesses` | An item or assessment expectation assesses a skill. |
| `remediates` | A lesson or activity remediates a weak skill. |
| `has_misconception` | A skill is associated with a misconception. |
| `derived_from_source` | A node or edge is grounded in source evidence. |

## Review status

Allowed review statuses are `draft`, `pending_review`, `approved`, `rejected`, and `superseded`.

Only `approved` nodes and edges may be used for production lesson generation, target graph generation, or learner-state authority.

## Compatibility outputs

Existing Content Factory registry files may remain as compatibility projections. They should be generated from, or reconciled with, the approved CAPS graph instead of becoming an independent source of truth.

## Retrieval integration

`source_ref` and `source_sha256` on graph nodes and `derived_from_source` edges must resolve to the same source-chunk identifiers already used by the Phase 2 `EmbeddingService`/`RetrievalService` (SHA-256 keyed). CAPS ingestion should not create a second, parallel definition of "approved source chunk" — the graph layer references the retrieval layer's approved chunks, it does not re-derive them.

## Validation rules

A graph mapping verifier must fail when a node has no source reference, a production node is not approved, a target graph references an unapproved CAPS node, a lesson references a node outside approved scope, an edge points to missing nodes, graph keys are duplicated, or source checksum is missing for CAPS-derived nodes.
