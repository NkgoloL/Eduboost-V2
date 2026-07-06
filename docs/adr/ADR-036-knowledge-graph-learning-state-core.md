---
title: "ADR-036 Knowledge Graph Learning-State Core"
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

# ADR-036: Knowledge Graph Learning-State Core

## Status

Accepted for controlled implementation planning. Runtime implementation remains gated by Phase 02R evidence and approval controls.

## Date

2026-06-23

## Context

EduBoost currently has strong modular-monolith foundations, including a FastAPI V2 backend, Next.js frontend, PostgreSQL/Alembic persistence, Redis-backed runtime support, Content Factory curriculum tooling, diagnostics, IRT, AI lesson generation, parent-facing workflows, POPIA controls, and release-evidence automation.

The current architecture still risks treating these capabilities as separate features rather than as coordinated mechanisms for measuring and changing a learner's educational state. That makes it harder to answer the core educational questions:

1. What does CAPS say the learner should know?
2. What does this specific learner currently know?
3. What evidence supports that belief?
4. What is blocking progress?
5. Which intervention should happen next?
6. Did the intervention actually change the learner's state?

The June 2026 technical audit also identified source-of-truth and contract drift risks: missing Content Factory registry artifacts, frontend/backend POPIA route mismatch, stale OpenAPI, and CI/package-manager drift. These are not only delivery issues; they show why EduBoost needs a clearer canonical model for curriculum, content, evidence, and learner state.

## Decision

EduBoost will pivot its core learning architecture to a **CAPS-grounded knowledge graph learning-state model**.

The authoritative model becomes three connected graph layers:

1. **CAPS Graph** — immutable curriculum/domain graph derived from approved CAPS sources, with source provenance and review status.
2. **Target Graph** — expected grade/subject/term mastery state derived from CAPS, pacing, beta scope, and educator policy.
3. **Learner Graph** — dynamic, evidence-backed learner state containing mastery, confidence, IRT estimates, misconception markers, blockers, and update history.

Diagnostics, IRT, lessons, practice, assessments, study plans, gamification, parent reporting, and tutor interactions are no longer treated as independent product islands. They become tools that either:

- observe the learner graph,
- compare it with the target graph,
- select a graph transition path,
- execute an intervention, or
- emit evidence that updates graph state.

## Scope of this ADR

This ADR authorises design, documentation, and controlled roadmap alignment. It does not authorise unreviewed runtime replacement of current diagnostics, lessons, parent workflows, POPIA endpoints, or Content Factory surfaces.

## Architectural consequences

### CAPS becomes the domain model

CAPS ingestion must produce reviewed graph nodes and edges, not only files, chunks, or registry entries.

Required node classes include phase, grade, subject, term, content area, topic, skill, micro-skill, assessment expectation, teaching guidance, misconception, and source evidence.

Required edge classes include contains, belongs_to, prerequisite_of, supports, assesses, remediates, has_misconception, and derived_from_source.

### IRT remains necessary but becomes evidence, not the whole model

IRT continues to estimate learner ability and item difficulty. Those estimates update learner graph nodes and confidence values. IRT is therefore part of the learner-state evidence pipeline, not the sole adaptive-learning controller.

### Lesson generation becomes graph-transition generation

A generated lesson must declare source CAPS graph nodes, target learner-state gap, prerequisite assumptions, misconceptions addressed, expected graph transition, and assessment evidence required to validate the transition.

### Parent portal becomes graph explanation

Parent reporting must explain current state, target state, gaps, interventions, and evidence in human-readable form without exposing unsafe internal inference details.

### Gamification becomes verified graph-progress recognition

Points and badges must be tied to verified educational transitions, not only activity volume.

### POPIA and audit requirements increase

Learner graph records are derived personal information. They must support export, correction, restriction, erasure workflows, consent boundaries, retention rules, audit evidence, and explainability.

## Persistence decision

The initial implementation will use PostgreSQL graph tables inside the existing modular monolith rather than introducing a graph database immediately.

Reasons:

- EduBoost already operates PostgreSQL, Alembic, repositories, audit ledgers, and CI checks.
- The first implementation needs governance, correctness, provenance, and migration discipline more than deep traversal performance.
- A future dedicated graph database or RDF triple-store move remains possible after query patterns and performance requirements are measured.

## Alternatives considered

### Keep current feature-centric architecture

Rejected. It preserves existing feature delivery but does not create one canonical educational-state model.

### Use only IRT/adaptive testing

Rejected. IRT is valuable for measurement, but it does not naturally represent prerequisites, CAPS hierarchy, misconceptions, lesson evidence, or parent explanations.

### Move immediately to a dedicated graph database or RDF triple store

Deferred. A graph database may become useful later, but introducing it now would add operational complexity before the domain model is stable.

### Use AI embeddings as the primary state model

Rejected. Embeddings are useful for retrieval and similarity, but they are not sufficient as an auditable curriculum, mastery, assessment, and POPIA state model.

This rejects embeddings only as the *primary* state model. The existing pgvector-backed `EmbeddingService`/`RetrievalService` from the Phase 2 semantic retrieval work is not superseded by this ADR and should remain the retrieval mechanism the graph model calls into for source evidence lookup (see `docs/ai/knowledge_graph_grounding_contract.md`). The graph model adds structure, provenance, and review status on top of that retrieval layer; it does not duplicate it.

## Acceptance criteria

This ADR is implemented when:

1. CAPS source ingestion produces immutable graph nodes and edges with page/source provenance.
2. Target graph generation exists for Grade 4 Mathematics beta scope.
3. Learner graph update events exist for diagnostics, IRT, lesson completion, practice, and assessment.
4. Gap analysis can compare learner graph state to target graph state.
5. Lesson and assessment generation use graph-grounded gaps and source evidence.
6. Parent reporting can explain graph state and progress.
7. POPIA export/erasure/correction workflows include graph-derived learner state.
8. Verification gates prove mappings, state updates, and generated content are grounded.

## Documentation impact

This ADR requires updates to root `README.md`, `docs/README.md`, architecture documentation index, roadmap index, Phase 02R execution records, CAPS mapping contracts, AI grounding contracts, testing and release evidence gates, and POPIA/privacy documentation.

## Related documents

- `docs/architecture/knowledge_graph_learning_state_architecture.md`
- `docs/architecture/knowledge_graph_data_model.md`
- `docs/architecture/knowledge_graph_transition_plan.md`
- `docs/product/knowledge_graph_learning_model_brief.md`
- `docs/caps/knowledge_graph_mapping_contract.md`
- `docs/ai/knowledge_graph_grounding_contract.md`
- `docs/security/knowledge_graph_privacy_and_popia_contract.md`
- `docs/roadmap/knowledge_graph_pivot_roadmap.md`
- `docs/roadmap/risk_register_knowledge_graph_pivot.md`
- `docs/roadmap/execution/atlas/phase_02r_knowledge_graph_pivot_control.md`
- `docs/testing/knowledge_graph_verification_plan.md`
