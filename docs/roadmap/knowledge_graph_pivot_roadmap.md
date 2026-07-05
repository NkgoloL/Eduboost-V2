---
title: "Knowledge Graph Pivot Roadmap"
status: active
owner: roadmap-governance
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

# Knowledge Graph Pivot Roadmap

## Purpose

This roadmap defines the controlled implementation path for making knowledge graphs the core EduBoost learning architecture.

## Roadmap rule

This roadmap does not replace urgent release blockers. Current audit blockers around Content Factory registry availability, POPIA route/auth drift, CI package-manager drift, OpenAPI drift, and frontend scripts must remain on the critical path because the knowledge graph model depends on those foundations.

## Phase KG-0: Formal pivot decision and documentation alignment

**Goal:** Establish the pivot as an approved architectural direction.

Deliverables: ADR-030 accepted; architecture index updated; README and docs index updated; product brief added; roadmap and risk register added; verification plan added; documentation verifier added.

Exit criteria: `verify_phase02r_knowledge_graph_pivot_docs.py` passes and docs are committed separately from runtime implementation.

## Phase KG-1: Source-of-truth repair and CAPS graph foundation

**Goal:** Resolve existing source-of-truth drift and build reviewed CAPS graph foundations.

Deliverables: Content Factory registry source-of-truth decision; deterministic registry bootstrap or committed registry files; CAPS graph schema migration; CAPS node/edge loaders from approved extraction outputs; mapping review manifest; CAPS graph verifier.

Exit criteria: Grade 4 Mathematics beta-scope CAPS graph exists, nodes and edges are source-provenanced and reviewable, and existing fast gate no longer fails due to missing registry artifacts.

## Phase KG-2: Target graph generation

**Goal:** Generate expected learner state for Grade 4 Mathematics beta scope.

Deliverables: target graph builder, Grade/subject/term target thresholds, pacing/priority policy, target graph API read endpoint, and target graph verifier.

Exit criteria: target graph references only approved CAPS graph nodes and can explain expected state by topic and term.

## Phase KG-3: Learner graph shadow mode

**Goal:** Capture learner-state evidence without disrupting existing product flows.

Deliverables: evidence event schema, learner graph state schema, diagnostic-to-evidence adapter, IRT-to-evidence adapter, lesson/practice/assessment event adapters, shadow graph state updater, and POPIA export/erasure fixture coverage.

Exit criteria: test learners produce learner graph states, existing progress remains authoritative, and shadow graph differences are reported and explainable.

## Phase KG-4: Gap engine and intervention planner

**Goal:** Compare learner graph to target graph and recommend next actions.

Deliverables: gap profile service, prerequisite blocker detection, misconception-aware recommendations, intervention planner, and recommendation explanation API.

Exit criteria: fixtures produce deterministic next-action recommendations and a human-readable reason is available for each recommendation.

## Phase KG-5: Grounded lesson and assessment generation

**Goal:** Make generation use graph gaps and source evidence.

Deliverables: graph-grounded lesson request contract, graph-grounded assessment request contract, generation validation rules, source-evidence citations in generated outputs, and lesson approval metadata tied to graph nodes.

Exit criteria: no production generated lesson can be approved without graph node references and source evidence; generated assessments produce expected evidence events.

## Phase KG-6: Tutor, study plan, gamification, and parent portal alignment

**Goal:** Reframe user-facing adaptive experiences around graph state.

Deliverables: tutor uses graph gap profile; study plans become graph traversal plans; parent portal explains learner graph vs target graph; badges/points require verified graph progress; educator/curriculum review surface for mappings and generated content.

Exit criteria: parent can see current state, expected state, gap, evidence, and next action; gamification rewards verified educational transitions.

## Phase KG-7: Authority switch and legacy cleanup

**Goal:** Make graph state authoritative for adaptive-learning decisions.

Deliverables: feature flag for graph authority, legacy mastery/progress compatibility projections, migration evidence report, runtime performance report, release evidence, and approval manifest.

Exit criteria: graph state is authoritative for diagnostics, tutor, lesson selection, study plans, and parent reporting; legacy logic is removed, archived, or derived from graph state; full backend, frontend, migration, OpenAPI, POPIA, and E2E verification gates pass.

## Dependency map

| Dependency | Required before |
|---|---|
| Content Factory registry repair | KG-1 exit |
| POPIA data-rights repair | KG-3 exit |
| OpenAPI/client drift repair | KG-4 and graph API exposure |
| CI/package-manager repair | Any release claim |
| CAPS extraction/review gates | KG-1 to KG-5 |
| IRT engine calibration | KG-3 and KG-4 |
| Gap engine and intervention planner (KG-4) | KG-5, since generation requests require a learner graph gap profile |
| Grounded lesson and assessment generation (KG-5) | KG-6, since tutor and study-plan selection use generated, graph-grounded content |

## Recommended branch strategy

- `feature/kg-pivot-docs` for KG-0.
- `feature/kg-caps-graph-foundation` for KG-1.
- `feature/kg-target-learner-shadow` for KG-2/KG-3.
- `feature/kg-gap-planner-generation` for KG-4/KG-5.
- `feature/kg-product-surfaces-authority` for KG-6/KG-7.

Each branch should preserve the existing evidence discipline: apply, verify, collect evidence, approval manifest, separate commits.
