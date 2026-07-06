---
title: "Knowledge Graph Data Model"
status: active
owner: architecture
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

# Knowledge Graph Data Model

## Purpose

This document defines the first-pass data model for the CAPS graph, target graph, learner graph, and evidence events.

## Design principles

1. Source-grounded: every curriculum node must trace to approved source evidence.
2. Reviewable: graph mappings can be pending, approved, rejected, or superseded.
3. Immutable where necessary: source and mapping evidence should not be overwritten silently.
4. Dynamic where necessary: learner state evolves over time through evidence events.
5. POPIA-aware: learner graph data is derived personal information.
6. Database-first: initial implementation uses PostgreSQL and Alembic.

## Core tables

### `kg_nodes`

Represents curriculum/domain objects.

Suggested columns include `id`, `node_key`, `node_type`, `label`, `description`, `grade`, `subject`, `term`, `metadata`, `review_status`, `source_ref`, `source_sha256`, `version`, `superseded_by_node_id`, `created_at`, and `updated_at`.

`grade`, `subject`, and `term` are promoted to explicit nullable columns rather than left inside `metadata`, because target graph generation and gap analysis filter on them constantly; a composite index on `(node_type, grade, subject, term)` keeps those queries index-backed. Not every node type populates all three (a misconception or source-evidence node may span grades), so the columns stay nullable.

`version` and `superseded_by_node_id` make the `superseded` review status concrete: superseding a node creates a new row and sets the old row's `superseded_by_node_id` rather than mutating the original in place, which preserves the "immutable where necessary" principle for anything that already has downstream references (target graph entries, evidence events, generated content).

### `kg_edges`

Represents relationships between nodes.

Suggested columns include `id`, `source_node_id`, `target_node_id`, `edge_type`, `weight`, `metadata`, `review_status`, `version`, `superseded_by_edge_id`, and `created_at`.

Allowed edge types include `contains`, `belongs_to`, `prerequisite_of`, `supports`, `assesses`, `remediates`, `has_misconception`, and `derived_from_source`.

Recommended indexes: `(source_node_id, edge_type)`, `(target_node_id, edge_type)`, and a partial index on rows where `review_status = 'approved'`, since production reads should almost always filter to approved edges only.

### `kg_target_states`

Represents expected mastery for a grade/subject/term/scope.

Suggested columns include `id`, `target_key`, `grade`, `subject`, `term`, `node_id`, `required_mastery`, `required_confidence`, `priority`, `pacing_window`, and `metadata`.

### `kg_learner_states`

Represents current learner-state estimates per graph node.

Suggested columns include `id`, `learner_id`, `node_id`, `mastery_score`, `confidence`, `theta`, `theta_se`, `evidence_count`, `last_evidence_event_id`, `state_reason`, `metadata`, and `updated_at`.

### `kg_evidence_events`

Represents observations that change or support learner graph state.

Suggested columns include `id`, `learner_id`, `node_id`, `event_type`, `source_id`, `observed_score`, `mastery_delta`, `confidence_delta`, `evidence_payload`, and `created_at`.

## Traversal considerations

Prerequisite-chain queries (used by the gap engine and study plan traversal) can use a recursive CTE over `kg_edges` filtered to `review_status = 'approved'`. CAPS hierarchies are shallow enough that this should perform acceptably at Grade 4 Mathematics beta scope. If tutor-facing latency becomes a problem as coverage grows, add a materialised `kg_edge_closure` table (ancestor/descendant pairs with path length) refreshed when CAPS graph edges are approved, rather than moving to a graph database first — this keeps the KG-R6 mitigation path (indexes and measured query plans before a new datastore) intact.

## Learner graph update rule

State updates must be append-first:

1. create evidence event,
2. compute proposed state update,
3. persist learner-state snapshot,
4. record reason and source event,
5. expose update in audit/export surfaces.

Do not mutate learner state without a corresponding evidence event.

## Mapping from existing features

| Existing feature | Graph role |
|---|---|
| CAPS ingestion | Creates source-grounded CAPS nodes and edges. |
| Content Factory registry | Becomes a reviewed graph projection / compatibility output. |
| Diagnostics | Creates evidence events and initial learner state. |
| IRT | Calibrates learner ability and item difficulty evidence. |
| Lessons | Attempts graph transitions from weak state to target state. |
| Practice | Produces repeated evidence for mastery and confidence. |
| Assessments | Produces stronger evidence and promotion decisions. |
| Study plans | Traverse prerequisite and target gaps. |
| Gamification | Rewards verified graph progress. |
| Parent portal | Explains learner graph vs target graph. |

## Privacy classification

- CAPS graph: non-personal curriculum data.
- Target graph: non-personal policy/configuration data.
- Learner graph: derived personal information.
- Evidence events: personal information and educational records.

Learner graph and evidence events must be included in POPIA export, correction, restriction, and erasure workflows.
