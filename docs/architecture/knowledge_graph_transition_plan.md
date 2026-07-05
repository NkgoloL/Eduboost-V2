---
title: "Knowledge Graph Transition Plan"
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

# Knowledge Graph Transition Plan

## Purpose

This document defines how EduBoost moves from the current feature-centric architecture to the knowledge graph learning-state architecture without breaking existing beta paths.

## Transition principles

1. Do not replace working learner, diagnostic, lesson, parent, or POPIA flows until equivalent graph-backed flows exist.
2. Introduce graph read models before graph write authority.
3. Keep the first graph implementation inside PostgreSQL and the modular monolith.
4. Preserve Phase 02R gate discipline: source acquisition, extraction, review, retrieval, generation, tutor use, migration, and audit closure.
5. Every graph state update must have evidence.
6. Every generated lesson or assessment must declare the graph gap it targets.

## Migration stages

### Stage 0: Governance and documentation alignment

Accept ADR-030, update README and documentation indexes, add architecture/mapping/AI/privacy/testing/risk/roadmap docs, and add the docs verifier.

Exit criteria: pivot docs are present, documentation indexes reference pivot docs, and verification script passes.

### Stage 1: CAPS graph read model

Convert approved CAPS extraction outputs into graph nodes and edges. Keep the existing Content Factory registry as compatibility output. Add mapping review status, source page, and checksum provenance.

Exit criteria: Grade 4 Mathematics CAPS graph exists for beta scope, nodes and edges trace to source evidence, and review manifests identify approved mappings.

### Stage 2: Target graph generation

Generate Grade 4 Mathematics target graph from approved CAPS graph and beta scope, including term, pacing, mastery, confidence, and priority fields.

Exit criteria: target graph can answer expected state by grade/subject/term and contains no unapproved CAPS nodes.

### Stage 3: Learner graph shadow mode

Capture diagnostic, IRT, practice, and lesson events as graph evidence events. Build learner graph state in shadow mode while existing flows remain authoritative. Compare graph state with current progress/mastery outputs.

Exit criteria: learner graph can be computed for test learners, state differences are explainable, and POPIA export includes shadow graph data in test fixtures.

### Stage 4: Gap engine and intervention planner

Compare learner graph to target graph. Return blockers, weak nodes, ready nodes, and next actions. Keep recommendations advisory until validated.

Exit criteria: gap engine produces deterministic recommendations for fixtures and recommendations are grounded in prerequisite edges and target priorities.

### Stage 5: Grounded generation

Lesson and assessment generation require graph context. Generated content declares target graph node, prerequisite assumptions, misconception focus, and expected evidence. Source evidence for generation is retrieved through the existing Phase 2 `RetrievalService`, scoped by graph node — this stage does not introduce a second retrieval path.

Exit criteria: no generated lesson can be approved without graph grounding metadata and retrieval uses approved graph nodes and source evidence.

### Stage 6: Graph-backed tutor and study plans

Tutor uses graph gap profile to select explanations, practice, assessment, or remediation. Study plans become graph traversal plans.

Exit criteria: tutor can explain why an activity was selected and study plans connect blockers to target outcomes.

### Stage 7: Product surfaces and reporting

Parent portal, learner dashboard, and educator reports show graph-derived progress. Gamification rewards verified graph-state transitions.

Exit criteria: parent reports explain current state, target state, evidence, and next action; badges/points require verified educational progress.

### Stage 8: Authority switch and legacy cleanup

Make graph state authoritative for adaptive learning decisions. Retire or archive feature-specific mastery logic that duplicates graph state. Keep compatibility APIs only where needed.

Exit criteria: graph state is the authoritative adaptive-learning model and legacy progress logic is either removed or clearly derived from graph state.

## Rollback plan

Rollback is controlled by feature flags and authority boundaries. CAPS graph can be disabled as a read model without affecting current lessons. Learner graph shadow mode can be stopped without deleting current progress data. Gap recommendations can be hidden while evidence capture continues. Generation can fall back to existing approved lesson generation until graph grounding is required by gate. Authority switch must not happen until export/erasure, tests, OpenAPI, parent portal, and release evidence are green.

## Documentation rule

Each runtime implementation PR must update at least one architecture document, roadmap status, graph mapping contract, testing plan, POPIA/privacy contract, AI grounding contract, or release evidence index.
