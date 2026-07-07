---
title: "EduBoost Knowledge Graph Implementation Roadmap"
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

# EduBoost Knowledge Graph Implementation Roadmap

**Source package reviewed:** `eduboost_knowledge_graph_pivot_formalization_package_v2.zip`  
**Roadmap type:** New approved roadmap proposal after closure of the reconciled RR-001 to RR-018 register  
**Boundary:** This roadmap does not authorise production release, public beta expansion, deployment, live billing, or runtime KG authority switch by itself.

---

## 1. Executive summary

The uploaded package correctly frames the knowledge graph pivot as a core architecture change, not a feature addition. It defines EduBoost’s future learning model around three graph layers:

1. **CAPS Graph** — source-grounded curriculum/domain graph.
2. **Target Graph** — expected learner state by grade, subject, term, scope, and pacing.
3. **Learner Graph** — dynamic, evidence-backed learner state.

Diagnostics, IRT, lesson generation, study plans, tutor flows, gamification, and parent reporting become tools that observe, compare, explain, or move the learner graph toward the target graph.

The implementation should proceed through controlled KG gates. The safest path is shadow-mode first, then advisory recommendations, then graph-grounded generation, then product-surface alignment, and only then authority switch.

---

## 2. Non-negotiable implementation rules

1. **No runtime KG authority switch before shadow-mode evidence.** Existing diagnostics, progress, lessons, and parent flows remain authoritative until graph state is proven.
2. **No graph node without source provenance.** CAPS-derived graph nodes and edges must reference approved extraction/source evidence.
3. **No learner graph update without evidence event.** Learner graph state is derived personal information and must be auditable.
4. **No AI-generated lesson approval without graph grounding.** Generated lessons must cite graph node IDs and approved source evidence.
5. **No parallel retrieval system.** Graph-grounded generation must reuse the existing approved retrieval layer rather than inventing a second definition of source evidence.
6. **POPIA workflows must include graph data before learner graph authority.** Export, correction, restriction, retention, and erasure must include learner graph and evidence-event data.
7. **The KG roadmap must be explicitly approved as new work.** The previous RR roadmap is closed; KG work should start only after KG-0 is approved and merged.

---

## 3. Roadmap overview

| Gate | Name | Purpose | Authority level |
|---|---|---|---|
| KG-0 | Formal KG roadmap approval | Land and approve pivot docs, ADR, roadmap, verification/risk controls | Documentation/governance only |
| KG-1 | CAPS graph foundation | Create source-grounded CAPS graph schema, loaders, review workflow, verifier | Curriculum graph read model |
| KG-2 | Target graph generation | Generate Grade 4 Mathematics expected-state graph from approved CAPS graph | Target graph read model |
| KG-3 | Learner graph shadow mode | Capture evidence events and build learner graph without replacing existing progress | Shadow learner graph only |
| KG-4 | Gap engine and intervention planner | Compare learner graph to target graph and produce explainable recommendations | Advisory recommendations only |
| KG-5 | Graph-grounded lesson and assessment generation | Require graph gaps and source evidence for generated lessons/assessments | Generation grounding, not full authority |
| KG-6 | Tutor, study plan, gamification, and parent alignment | Reframe user-facing experiences around graph state | Graph-backed surfaces, existing authority preserved |
| KG-7 | Authority switch and legacy cleanup | Make graph state authoritative after all verification gates pass | Controlled authority switch |
| KG-8 | Post-switch optimisation and scale review | Measure performance, decide if graph DB/closure-table/analytics expansion is needed | Optimisation only |

---

## 4. KG-0 — Formal KG roadmap approval

### Goal

Land the uploaded formalisation package as the approved KG roadmap/governance baseline.

### Main deliverables

- `ADR-036-knowledge-graph-learning-state-core.md`
- KG architecture docs
- KG data model docs
- KG transition plan
- KG CAPS mapping contract
- KG AI grounding contract
- KG POPIA/privacy contract
- KG verification plan
- KG risk register
- KG roadmap
- documentation verifier
- apply script and manifest/hash verification

### Implementation work

1. Apply the package into the current clean `master`.
2. Confirm no ADR number collision with existing ADRs.
3. Confirm package docs do not conflict with final roadmap closure docs.
4. Patch indexes using the package markers.
5. Run package verifier with manifest.
6. Add a KG-0 evidence record under a new KG roadmap evidence path.

### Exit criteria

- KG package docs are merged.
- Package verifier passes.
- Manifest verification passes.
- Final closure boundary remains intact:
  - `production_release_authorised: false`
  - `deployment_authorised: false`
  - `public_beta_authorised: false`
  - `runtime_kg_implementation_claimed: false`

### Recommended branch

`codex/kg-0-formal-pivot-approval`

---

## 5. KG-1 — CAPS graph foundation

### Goal

Create the first source-grounded CAPS graph for Grade 4 Mathematics beta scope.

### Main deliverables

- Alembic migration for `kg_nodes`, `kg_edges`, review statuses, source provenance, supersession fields, and indexes.
- Domain models for CAPS graph nodes and edges.
- Repository and service layer for CAPS graph reads/writes.
- Loader from approved CAPS extraction outputs.
- Mapping review manifest.
- CAPS graph verifier.
- Compatibility projection strategy for the existing Content Factory registry.

### Suggested implementation modules

```text
app/domain/knowledge_graph.py
app/repositories/knowledge_graph_repository.py
app/services/knowledge_graph/caps_graph_builder.py
app/services/knowledge_graph/caps_graph_verifier.py
app/api_v2_routers/knowledge_graphs.py
alembic/versions/*_knowledge_graph_foundation.py
scripts/knowledge_graph/load_caps_graph.py
scripts/knowledge_graph/verify_caps_graph.py
```

### Data model focus

- `kg_nodes`
- `kg_edges`
- node/edge review statuses
- source references and checksums
- `version`
- `superseded_by_node_id`
- `superseded_by_edge_id`
- indexes for node type, grade, subject, term, and approved edges

### Exit criteria

- Grade 4 Mathematics CAPS graph exists.
- Every CAPS-derived node has source reference and checksum.
- Every production-eligible node/edge is `approved`.
- No duplicate graph keys.
- No orphaned edges.
- Existing Content Factory registry is either reconciled or explicitly treated as a projection.

### Recommended branch

`codex/kg-1-caps-graph-foundation`

---

## 6. KG-2 — Target graph generation

### Goal

Generate the expected Grade 4 Mathematics learner state from the approved CAPS graph.

### Main deliverables

- `kg_target_states` migration/model.
- Target graph builder.
- Grade/subject/term/scope policy file.
- Mastery threshold policy.
- Confidence threshold policy.
- Pacing-window policy.
- Priority weighting policy.
- Target graph read API.
- Target graph verifier.

### Suggested implementation modules

```text
app/services/knowledge_graph/target_graph_builder.py
app/services/knowledge_graph/target_graph_policy.py
app/api_v2_routers/knowledge_graph_targets.py
scripts/knowledge_graph/build_target_graph.py
scripts/knowledge_graph/verify_target_graph.py
```

### Exit criteria

- Target graph references only approved CAPS nodes.
- Target graph is scoped to Grade 4 Mathematics beta scope.
- Required mastery/confidence thresholds are present.
- Target state is explainable by topic, term, and priority.
- OpenAPI includes target graph read endpoints.

### Recommended branch

`codex/kg-2-target-graph-generation`

---

## 7. KG-3 — Learner graph shadow mode

### Goal

Start recording graph evidence and learner graph state in shadow mode, while existing progress/mastery flows remain authoritative.

### Main deliverables

- `kg_learner_states` migration/model.
- `kg_evidence_events` migration/model.
- Evidence event schema.
- Diagnostic-to-evidence adapter.
- IRT-to-evidence adapter.
- Practice/lesson/assessment-to-evidence adapters.
- Shadow learner graph updater.
- Comparison report between existing progress and learner graph state.
- POPIA export/erasure test fixtures for graph data.

### Suggested implementation modules

```text
app/services/knowledge_graph/evidence_event_service.py
app/services/knowledge_graph/learner_graph_updater.py
app/services/knowledge_graph/shadow_state_comparator.py
app/services/knowledge_graph/adapters/diagnostic_adapter.py
app/services/knowledge_graph/adapters/irt_adapter.py
app/services/knowledge_graph/adapters/lesson_adapter.py
scripts/knowledge_graph/verify_learner_graph_shadow.py
```

### Exit criteria

- Learner graph state can be computed for test learners.
- Every learner graph state update has an evidence event.
- Existing progress remains authoritative.
- Shadow graph differences are explainable.
- POPIA export includes learner graph/evidence event data in fixtures.
- Erasure/restriction/correction boundaries are tested.

### Recommended branch

`codex/kg-3-learner-graph-shadow-mode`

---

## 8. KG-4 — Gap engine and intervention planner

### Goal

Compare learner graph state with target graph state and produce explainable next-action recommendations.

### Main deliverables

- Gap profile service.
- Prerequisite blocker detection.
- Weak/ready/unknown node classification.
- Misconception-aware recommendation path.
- Intervention planner.
- Recommendation explanation API.
- Deterministic fixture suite.

### Suggested implementation modules

```text
app/services/knowledge_graph/gap_engine.py
app/services/knowledge_graph/prerequisite_traversal.py
app/services/knowledge_graph/intervention_planner.py
app/api_v2_routers/knowledge_graph_recommendations.py
scripts/knowledge_graph/verify_gap_engine.py
```

### Exit criteria

- Fixture learner with prerequisite blocker gets blocker-first recommendation.
- Fixture learner with weak node gets remediation recommendation.
- Fixture learner with insufficient evidence gets diagnostic recommendation.
- Every recommendation includes human-readable reason and graph node references.
- Recommendations remain advisory; no authority switch yet.

### Recommended branch

`codex/kg-4-gap-engine-intervention-planner`

---

## 9. KG-5 — Graph-grounded lesson and assessment generation

### Goal

Make generated lessons and assessments depend on graph gaps and approved source evidence.

### Main deliverables

- Graph-grounded lesson request contract.
- Graph-grounded assessment request contract.
- Generation validation rules.
- Retrieval service integration using graph node constraints.
- Source-evidence citation enforcement.
- Generated-content approval metadata tied to graph nodes.
- Expected evidence-event output contract.

### Suggested implementation modules

```text
app/services/knowledge_graph/grounded_generation_context.py
app/services/knowledge_graph/generation_grounding_validator.py
app/services/ai/graph_grounded_lesson_service.py
app/services/ai/graph_grounded_assessment_service.py
scripts/knowledge_graph/verify_generation_grounding.py
```

### Exit criteria

- Generation fails closed when graph context or approved source evidence is missing.
- No approved generated lesson lacks graph node references.
- Generated assessment declares expected evidence event.
- Grounding uses existing retrieval service, not a parallel retrieval path.
- AI output cannot create authoritative graph nodes or mastery claims.

### Recommended branch

`codex/kg-5-graph-grounded-generation`

---

## 10. KG-6 — Tutor, study plan, gamification, and parent alignment

### Goal

Align product surfaces to explain and use graph state, without yet making graph state universally authoritative.

### Main deliverables

- Tutor uses graph gap profile for next action.
- Study plans become graph traversal plans.
- Parent portal shows current state, target state, gaps, evidence, and next action.
- Gamification rewards verified graph progress, not just activity volume.
- Educator/curriculum review surface for mappings and generated content.
- UX copy for non-technical graph explanations.

### Suggested implementation areas

```text
app/frontend/src/components/eduboost/GraphProgressSummary.tsx
app/frontend/src/components/eduboost/GraphGapExplanation.tsx
app/frontend/src/components/eduboost/ParentGraphReport.tsx
app/frontend/src/components/eduboost/StudyPlanGraphPath.tsx
app/services/study_plans/graph_study_plan_service.py
app/services/gamification/graph_progress_awards.py
```

### Exit criteria

- Parent can see graph-derived progress in understandable language.
- Study plans explain why each step was selected.
- Tutor can cite graph gap reason.
- Gamification requires verified graph-state transition.
- Existing non-graph views remain available as fallback.

### Recommended branch

`codex/kg-6-product-surfaces-alignment`

---

## 11. KG-7 — Authority switch and legacy cleanup

### Goal

Make graph state authoritative for adaptive-learning decisions after all verifiers pass.

### Main deliverables

- Graph authority feature flag.
- Authority-switch approval manifest.
- Legacy compatibility projections.
- Migration evidence report.
- Runtime performance report.
- OpenAPI/client updates.
- POPIA final evidence.
- E2E learner/parent/tutor/study-plan evidence.
- Legacy progress/mastery cleanup plan.

### Required preconditions

All of the following must be green:

- documentation verifier
- migration graph verifier
- schema integrity verifier
- CAPS graph verifier
- target graph verifier
- learner graph verifier
- gap engine verifier
- generation grounding verifier
- POPIA export/erasure/correction fixtures
- OpenAPI/client contract check
- backend fast gate
- frontend gates
- E2E learner/parent/tutor journeys
- release evidence

### Exit criteria

- Graph state is authoritative for diagnostics, tutor, lesson selection, study plans, and parent reporting.
- Legacy logic is removed, archived, or explicitly derived from graph state.
- Rollback plan remains available.
- Release/deployment/public beta boundaries remain separately controlled.

### Recommended branch

`codex/kg-7-authority-switch-legacy-cleanup`

---

## 12. KG-8 — Post-switch optimisation and scale review

### Goal

Measure the graph implementation and decide whether deeper graph infrastructure is justified.

### Main deliverables

- Query performance report.
- Prerequisite traversal latency report.
- Tutor-facing latency report.
- Closure-table evaluation.
- Graph database evaluation memo, if justified.
- Caching and invalidation review.
- Operational dashboard updates.

### Exit criteria

- PostgreSQL graph queries meet latency targets, or a measured case exists for closure-table or graph-database work.
- No new datastore is introduced without ADR approval.
- Dashboard/SLO coverage exists for KG flows.

### Recommended branch

`codex/kg-8-graph-scale-optimisation-review`

---

## 13. Evidence and verifier plan

Each KG gate should follow the same pattern used in the closed RR stream:

1. Authority PR with code/docs/verifier.
2. Final docs/config/data PR if needed.
3. Evidence PR after clean-master capture.
4. Verifier proves the gate state.
5. Boundaries remain explicitly false unless a later approval authorises them.

Minimum verifier set:

```text
verify_kg0_pivot_docs.py
verify_kg1_caps_graph_foundation.py
verify_kg2_target_graph.py
verify_kg3_learner_graph_shadow.py
verify_kg4_gap_engine.py
verify_kg5_generation_grounding.py
verify_kg6_product_surfaces.py
verify_kg7_authority_switch.py
verify_kg8_scale_review.py
```

---

## 14. Recommended immediate next implementation slice

The next slice should be:

```text
KG-0 — Formal KG roadmap approval
```

Purpose:

```text
- land the formal KG package into the repo
- confirm ADR/index compatibility
- add/verify KG documentation controls
- explicitly open a new approved KG roadmap after RR closure
- preserve all release/public-beta/runtime-KG authority boundaries
```

Do not begin KG-1 runtime implementation until KG-0 is merged and evidenced.

---

## 15. Suggested KG-0 command flow

```bash
git checkout master
git pull --ff-only origin master
git checkout -b codex/kg-0-formal-kg-roadmap-approval

unzip eduboost_knowledge_graph_pivot_formalization_package_v2.zip -d /tmp/kg-pivot-package
bash /tmp/kg-pivot-package/scripts/phase02r/apply_phase02r_knowledge_graph_pivot_docs.sh .

python3 /tmp/kg-pivot-package/scripts/phase02r/verify_phase02r_knowledge_graph_pivot_docs.py \
  --root . \
  --manifest /tmp/kg-pivot-package/MANIFEST.json

python3 -m compileall -q scripts

git diff --check
```

Recommended commit:

```bash
git add README.md docs scripts/phase02r
git commit -m "docs(architecture): approve knowledge graph pivot roadmap"
git push origin codex/kg-0-formal-kg-roadmap-approval
```

---

## 16. Final recommendation

Proceed with KG work only by opening a new approved KG roadmap stream. The package is strong as a design/governance baseline, but it should not be mistaken for runtime implementation evidence. The safest implementation order is:

```text
KG-0 docs/governance approval
KG-1 CAPS graph foundation
KG-2 target graph
KG-3 learner graph shadow mode
KG-4 gap engine
KG-5 graph-grounded generation
KG-6 product surface alignment
KG-7 authority switch
KG-8 optimisation review
```

This keeps the knowledge graph monster as the architectural north star while preserving the disciplined evidence model that closed the RR register.
