# EduBoost V2 Curriculum, CAPS Knowledge Graph, and Runtime KG

Maps authoritative CAPS acquisition, extraction, graph construction, target and learner graphs, gap planning, grounded generation, persistence, and route projections.

## Scope and ownership

This codemap is the primary architecture owner for:
- `app/services/curriculum`
- `app/domain/knowledge_graph_*.py`
- `app/services/runtime_kg`
- `app/models/runtime_kg.py`

It describes current implementation paths in repository-relative form. Related cross-cutting behaviour may be referenced from other codemaps, but every maintained source file has one primary owner in `codemap_coverage_manifest.json`.

## Architectural position

This area participates in the wider EduBoost request, data, evidence, and release architecture. Read it together with `00_application_bootstrap_and_request_lifecycle.md`, `17_testing_ci_coverage_security_and_quality_gates.md`, and `18_production_readiness_release_evidence_and_live_traffic.md` when changing runtime or release-critical behaviour.

## Trace ID: 1
**Title:** Authoritative CAPS acquisition, extraction, corpus, and graph construction

**Description:** Follows approved curriculum sources from immutable acquisition through page-level extraction, corpus approval, mapping, and graph creation.

**Motivation:**
The curriculum graph is the grounding authority for diagnostics, lessons, tutor actions, and study plans.

**Details:**

**Execution path**

1. Acquire an approved CAPS source and record rights metadata.
2. Freeze content hash and source identity.
3. Extract pages and chunks with provenance.
4. Validate claims, answers, and curriculum scope.
5. Build reviewed concepts, prerequisites, outcomes, and mappings.
6. Publish an approved corpus and graph version.

**State and ownership boundaries**

Source documents, extraction artefacts, corpus releases, and graph versions are immutable or versioned authorities.

**Failure, privacy, and control points**

Only rights-compatible approved sources enter generation; every graph assertion retains source and review evidence.

**Verification signals**

Run Phase 02R acquisition, extraction, corpus, graph, rights, and closure verifiers.

**Trace text diagram:**
```text
1. Acquire an approved CAPS source and record rights metadata [1a]
   |
   v
2. Freeze content hash and source identity [1b]
   |
   v
3. Extract pages and chunks with provenance [1c]
   |
   v
4. Validate claims, answers, and curriculum scope [1d]
   |
   v
5. Build reviewed concepts, prerequisites, outcomes, and mappings [1d]
   |
   v
6. Publish an approved corpus and graph version [1d]
```

**Location ID: 1a**
- **Title:** Curriculum acquisition
- **Description:** Immutable source intake.
- **Path:LineNumber:** app/services/curriculum/acquisition.py:19

**Location ID: 1b**
- **Title:** Structured extraction
- **Description:** Page and chunk provenance.
- **Path:LineNumber:** app/services/curriculum/extraction.py:25

**Location ID: 1c**
- **Title:** Approved corpus
- **Description:** Curated semantic source authority.
- **Path:LineNumber:** app/services/curriculum/corpus.py:22

**Location ID: 1d**
- **Title:** Curriculum graph builder
- **Description:** Concept and relationship construction.
- **Path:LineNumber:** app/services/curriculum/graph.py:21

### AI Guide: Authoritative CAPS acquisition, extraction, corpus, and graph construction

**Motivation:**
The curriculum graph is the grounding authority for diagnostics, lessons, tutor actions, and study plans.

**Details:**

**Reasoning through the execution path.** Start at [1a] and follow the ordered state transition rather than jumping directly to a downstream repository or generated artefact. The trace is designed to show which layer owns transport, orchestration, persistence, and evidence. [1a] anchors curriculum acquisition. [1b] anchors structured extraction. [1c] anchors approved corpus. [1d] anchors curriculum graph builder.

**Safe change boundary.** Source documents, extraction artefacts, corpus releases, and graph versions are immutable or versioned authorities. A change that moves responsibility across these boundaries should update the owning codemap, tests, and any affected ADR or release verifier in the same change.

**Controls to preserve.** Only rights-compatible approved sources enter generation; every graph assertion retains source and review evidence.

**How to verify the change.** Run Phase 02R acquisition, extraction, corpus, graph, rights, and closure verifiers. Use the cited locations as navigation anchors, then inspect call sites and tests before modifying behaviour.

## Trace ID: 2
**Title:** Target graph, learner shadow, gap engine, and grounded intervention

**Description:** Maps the three-graph model from curriculum authority to grade target, learner knowledge state, and gap-driven intervention planning.

**Motivation:**
The graph architecture makes desired knowledge, observed mastery, and curriculum evidence explicit rather than embedding them in opaque prompts.

**Details:**

**Execution path**

1. Load the canonical CAPS concept graph.
2. Derive the grade/subject target graph.
3. Project diagnostic and completion evidence into the learner shadow.
4. Compare learner state with target prerequisites and outcomes.
5. Rank gaps and select an intervention.
6. Ground lesson, assessment, tutor, or plan generation in the selected graph evidence.

**State and ownership boundaries**

CAPS graph, target graph, learner shadow, and intervention plan are separate versioned projections.

**Failure, privacy, and control points**

Projection never overwrites source evidence, gap ranking is deterministic under the same snapshot, and legacy fallbacks remain controlled.

**Verification signals**

Run KG001-KG006 domain tests and graph product-alignment verifiers.

**Trace text diagram:**
```text
1. Load the canonical CAPS concept graph [2a]
   |
   v
2. Derive the grade/subject target graph [2b]
   |
   v
3. Project diagnostic and completion evidence into the learner shadow [2c]
   |
   v
4. Compare learner state with target prerequisites and outcomes [2d]
   |
   v
5. Rank gaps and select an intervention [2d]
   |
   v
6. Ground lesson, assessment, tutor, or plan generation in the selected graph evidence [2d]
```

**Location ID: 2a**
- **Title:** CAPS graph
- **Description:** Canonical curriculum graph model.
- **Path:LineNumber:** app/domain/knowledge_graph_caps.py:21

**Location ID: 2b**
- **Title:** Target graph
- **Description:** Expected grade/subject state.
- **Path:LineNumber:** app/domain/knowledge_graph_target.py:25

**Location ID: 2c**
- **Title:** Learner shadow
- **Description:** Observed learner knowledge projection.
- **Path:LineNumber:** app/domain/knowledge_graph_learner_shadow.py:23

**Location ID: 2d**
- **Title:** Gap engine
- **Description:** Intervention prioritization.
- **Path:LineNumber:** app/domain/knowledge_graph_gap_engine.py:24

### AI Guide: Target graph, learner shadow, gap engine, and grounded intervention

**Motivation:**
The graph architecture makes desired knowledge, observed mastery, and curriculum evidence explicit rather than embedding them in opaque prompts.

**Details:**

**Reasoning through the execution path.** Start at [2a] and follow the ordered state transition rather than jumping directly to a downstream repository or generated artefact. The trace is designed to show which layer owns transport, orchestration, persistence, and evidence. [2a] anchors caps graph. [2b] anchors target graph. [2c] anchors learner shadow. [2d] anchors gap engine.

**Safe change boundary.** CAPS graph, target graph, learner shadow, and intervention plan are separate versioned projections. A change that moves responsibility across these boundaries should update the owning codemap, tests, and any affected ADR or release verifier in the same change.

**Controls to preserve.** Projection never overwrites source evidence, gap ranking is deterministic under the same snapshot, and legacy fallbacks remain controlled.

**How to verify the change.** Run KG001-KG006 domain tests and graph product-alignment verifiers. Use the cited locations as navigation anchors, then inspect call sites and tests before modifying behaviour.

## Trace ID: 3
**Title:** Runtime KG persistence, loading, acceptance, and route projections

**Description:** Shows how approved graph artefacts become runtime records and are consumed by diagnostics, lessons, study plans, and vertical journeys.

**Motivation:**
Formal graph designs become product architecture only when persistence, migration, feature flags, and route behaviour are verified.

**Details:**

**Execution path**

1. Load approved graph artefacts into runtime schemas.
2. Persist graph nodes, edges, snapshots, and learner projections.
3. Resolve active graph versions through feature flags.
4. Serve queries through the runtime KG service.
5. Integrate projections into diagnostic, lesson, study-plan, and journey routes.
6. Run acceptance checks and preserve fallback evidence.

**State and ownership boundaries**

Runtime tables and snapshots are operational copies of versioned graph authority; feature flags control activation, not correctness.

**Failure, privacy, and control points**

Migration is reversible, missing graph data degrades explicitly, route projections preserve compatibility, and acceptance proves persistence plus behaviour.

**Verification signals**

Run PRD-2 persistence, route integration, acceptance, migration, and vertical journey tests.

**Trace text diagram:**
```text
1. Load approved graph artefacts into runtime schemas [3a]
   |
   v
2. Persist graph nodes, edges, snapshots, and learner projections [3b]
   |
   v
3. Resolve active graph versions through feature flags [3c]
   |
   v
4. Serve queries through the runtime KG service [3d]
   |
   v
5. Integrate projections into diagnostic, lesson, study-plan, and journey routes [3d]
   |
   v
6. Run acceptance checks and preserve fallback evidence [3d]
```

**Location ID: 3a**
- **Title:** Runtime KG loader
- **Description:** Approved artefact ingestion.
- **Path:LineNumber:** app/services/runtime_kg/loader.py:9

**Location ID: 3b**
- **Title:** Runtime KG repository
- **Description:** Graph persistence queries.
- **Path:LineNumber:** app/services/runtime_kg/repository.py:12

**Location ID: 3c**
- **Title:** Runtime KG service
- **Description:** Runtime graph access.
- **Path:LineNumber:** app/services/runtime_kg/service.py:10

**Location ID: 3d**
- **Title:** Runtime KG acceptance
- **Description:** Behavioural handoff checks.
- **Path:LineNumber:** app/services/runtime_kg/acceptance.py:18

### AI Guide: Runtime KG persistence, loading, acceptance, and route projections

**Motivation:**
Formal graph designs become product architecture only when persistence, migration, feature flags, and route behaviour are verified.

**Details:**

**Reasoning through the execution path.** Start at [3a] and follow the ordered state transition rather than jumping directly to a downstream repository or generated artefact. The trace is designed to show which layer owns transport, orchestration, persistence, and evidence. [3a] anchors runtime kg loader. [3b] anchors runtime kg repository. [3c] anchors runtime kg service. [3d] anchors runtime kg acceptance.

**Safe change boundary.** Runtime tables and snapshots are operational copies of versioned graph authority; feature flags control activation, not correctness. A change that moves responsibility across these boundaries should update the owning codemap, tests, and any affected ADR or release verifier in the same change.

**Controls to preserve.** Migration is reversible, missing graph data degrades explicitly, route projections preserve compatibility, and acceptance proves persistence plus behaviour.

**How to verify the change.** Run PRD-2 persistence, route integration, acceptance, migration, and vertical journey tests. Use the cited locations as navigation anchors, then inspect call sites and tests before modifying behaviour.

## Change checklist

- Update this codemap when an entry point, major dependency, persistence owner, or control flow changes.
- Keep all `Path:LineNumber` references repository-relative and line-valid.
- Update `codemap_coverage_manifest.json` when files move between architecture owners.
- Run `python scripts/maintenance/verify_codemaps.py --repo-root .` before merging.
