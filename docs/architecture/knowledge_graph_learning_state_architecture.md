---
title: "Knowledge Graph Learning-State Architecture"
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

# Knowledge Graph Learning-State Architecture

## Purpose

This document defines the EduBoost architecture pivot from a set of adaptive-learning features to a CAPS-grounded knowledge graph learning-state platform.

## Architecture thesis

EduBoost should not be centred on lesson generation, diagnostics, or AI chat. Those are important tools, but the durable product advantage is the ability to model and change learner knowledge in an explainable, curriculum-grounded way.

The core loop is:

```text
CAPS Graph
  -> Target Graph
  -> Learner Graph
  -> Gap Profile
  -> Intervention Selection
  -> Evidence Event
  -> Learner Graph Update
```

## Graph layers

### 1. CAPS Graph

The CAPS graph is the immutable curriculum/domain graph. It answers: **What exists in the curriculum and how is it related?**

It contains curriculum source, phase, grade, subject, term, content area, topic, skill, micro-skill, assessment expectation, teaching guidance, misconception, prerequisite and dependency edges, source page and checksum provenance, and review status.

The CAPS graph is governed by Phase 02R source acquisition, extraction, review, and evidence gates.

### 2. Target Graph

The target graph is the expected learner state for a specific grade, subject, term, pacing period, and beta scope. It answers: **Where should the learner be now?**

It contains target mastery thresholds, confidence thresholds, pacing windows, priority weights, and prerequisite expectations.

A target graph is derived from the CAPS graph and policy configuration. It must not contain ungrounded concepts.

### 3. Learner Graph

The learner graph is the dynamic state of one learner. It answers: **Where is this learner actually?**

It contains per-node mastery, confidence, evidence count, IRT estimates, misconception markers, blocker relationships, recent interventions, and update provenance.

The learner graph must be explainable and POPIA-compliant because it is derived personal information.

## Supporting engines

- CAPS graph builder: builds and validates graph nodes and edges from reviewed CAPS extraction outputs.
- Target graph builder: creates grade/subject/term expectations from the CAPS graph and approved product scope.
- Evidence engine: normalises diagnostic attempts, IRT results, practice attempts, lesson completions, assessment answers, and tutor interactions into graph evidence events.
- State update engine: updates learner graph state based on evidence events while preserving why the state changed.
- Gap engine: compares learner graph to target graph and returns missing concepts, weak concepts, prerequisite blockers, likely misconceptions, readiness estimates, and next actions.
- Intervention planner: chooses whether the next intervention should be diagnostic, remediation lesson, practice, assessment, study plan update, tutor prompt, parent explanation, or human review.
- Grounded generation engine: generates lessons, assessments, explanations, and tutor responses using graph-selected context and source evidence. Source evidence lookup is performed by the existing Phase 2 `RetrievalService`/`EmbeddingService` (pgvector-backed, approval/status filtered); this engine does not implement a second retrieval mechanism, it supplies that service with graph-selected node and scope constraints.

## Runtime placement

The first implementation stays inside the existing modular monolith:

```text
app/domain/knowledge_graph.py
app/repositories/knowledge_graph_repository.py
app/services/knowledge_graph/
app/api_v2_routers/knowledge_graphs.py
alembic/versions/*knowledge_graph*.py
```

This keeps the pivot aligned with existing FastAPI, PostgreSQL, Alembic, tests, auth, consent, audit, and CI controls.

## Persistence model

Initial persistence uses PostgreSQL tables for graph nodes, edges, target state, learner state, and evidence events.

A dedicated graph database may be evaluated later only if traversal depth grows beyond what indexed PostgreSQL queries and, if needed, a materialised closure table can serve efficiently, query latency blocks tutor interactions, graph analytics become operationally important, and governance can support an additional datastore.

## Caching

CAPS graph and target graph reads are frequent and change rarely once approved, which makes them good Redis cache candidates. Cache keys should follow the existing project convention of hashing the query scope (for example a SHA-256 of grade/subject/term/node-set) rather than caching individual rows, and cache entries must be invalidated on approval-status change, not on a fixed TTL alone. Learner graph state should not be cached as the sole source for authoritative decisions; it may be cached for read-only display with a short TTL.

## AI boundary

AI generation is not allowed to invent curriculum structure. AI may assist extraction and lesson generation, but graph nodes, source evidence, target expectations, and learner-state updates must remain deterministic, reviewable, and auditable.

## Parent and educator explanation boundary

Parent and educator views must explain graph state in accessible language: current mastery, expected mastery, gap reason, evidence supporting the state, next recommended intervention, and progress over time.

They must avoid exposing unsafe raw internal inference details or unsupported predictions.

## Non-goals

This pivot does not immediately require replacing PostgreSQL with a dedicated graph database, replacing all current content systems, replacing IRT, replacing the AI Gateway, exposing graph internals directly to learners, or completing full CAPS coverage before proving Grade 4 Mathematics.

## Success measures

The architecture succeeds when EduBoost can answer, for any learner and active topic:

1. What CAPS node is this about?
2. What should the learner know?
3. What does the learner appear to know?
4. What evidence supports that state?
5. What is the next best action?
6. Did the action move the learner closer to the target graph?
