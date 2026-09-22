# EduBoost V2 — Longitudinal Educational Validation Implementation TODO

**Authority:** PRD-4A / LEV  
**Generated:** 13 July 2026  
**Task count:** 222  
**Default status:** Not started

> This file is an execution register, not a claim that the tasks have been completed. Empirical studies, learner recruitment, independent review, consent/assent and longitudinal follow-up cannot be replaced by generated code or documentation.

## Status rules

- `[ ]` Not started or blocked
- `[-]` In progress
- `[?]` Candidate complete / awaiting evidence or independent review
- `[x]` Closed with verified evidence

## Required completion workflow

1. Read the task card and dependencies.
2. Assign an accountable owner and reviewer in the JSON register.
3. Update the evidence record before implementation begins.
4. Implement, test and capture the required evidence.
5. Set `candidate_complete`; do not set `closed` manually.
6. Run the verifier and obtain the required independent decision.

## Workstream index

- [LEV-WS01 — Define mastery claims precisely](docs/roadmap/production_readiness/lev/workstreams/LEV-WS01.md) — 14 tasks
- [LEV-WS02 — Independently review CAPS concepts and assessment items](docs/roadmap/production_readiness/lev/workstreams/LEV-WS02.md) — 16 tasks
- [LEV-WS03 — Make learner evidence and state changes fully traceable](docs/roadmap/production_readiness/lev/workstreams/LEV-WS03.md) — 14 tasks
- [LEV-WS04 — Calibrate mastery estimates against independent outcomes](docs/roadmap/production_readiness/lev/workstreams/LEV-WS04.md) — 15 tasks
- [LEV-WS05 — Quantify false-mastery and false-non-mastery risk](docs/roadmap/production_readiness/lev/workstreams/LEV-WS05.md) — 14 tasks
- [LEV-WS06 — Demonstrate delayed-retention validity](docs/roadmap/production_readiness/lev/workstreams/LEV-WS06.md) — 15 tasks
- [LEV-WS07 — Demonstrate transfer validity](docs/roadmap/production_readiness/lev/workstreams/LEV-WS07.md) — 15 tasks
- [LEV-WS08 — Validate educational plausibility of state transitions](docs/roadmap/production_readiness/lev/workstreams/LEV-WS08.md) — 15 tasks
- [LEV-WS09 — Establish validity across relevant learner contexts](docs/roadmap/production_readiness/lev/workstreams/LEV-WS09.md) — 15 tasks
- [LEV-WS10 — Demonstrate that mastery-informed recommendations improve learning](docs/roadmap/production_readiness/lev/workstreams/LEV-WS10.md) — 16 tasks
- [LEV-WS11 — Measure and control adverse educational effects](docs/roadmap/production_readiness/lev/workstreams/LEV-WS11.md) — 15 tasks
- [LEV-WS12 — Replicate findings in another cohort or academic year](docs/roadmap/production_readiness/lev/workstreams/LEV-WS12.md) — 14 tasks
- [LEV-WS13 — Operate drift detection and revalidation controls](docs/roadmap/production_readiness/lev/workstreams/LEV-WS13.md) — 15 tasks
- [LEV-WS14 — Obtain independent approval of intended uses](docs/roadmap/production_readiness/lev/workstreams/LEV-WS14.md) — 14 tasks
- [LEV-WS15 — Document unsupported uses and residual limitations](docs/roadmap/production_readiness/lev/workstreams/LEV-WS15.md) — 15 tasks

---

# LEV-WS01 — Define mastery claims precisely

**Definition of done:** Mastery claims are precisely defined.

**Objective:** Establish an authoritative, testable and uncertainty-qualified definition of every learner-state projection and every permitted use of the term mastery.

**Dependencies:** LEV-0 authority; curriculum scope; intended product uses; legal and ethical review.

## [ ] LEV-01.01 — Create a mastery-construct working group with psychometric, mathematics-education, teacher, product, data-science, privacy and runtime-KG representation.

- **Phase:** LEV-0  
- **Priority:** P0  
- **Type:** human_governance_or_research  
- **Depends on:** None  
- **Primary files:** `app/modules/progress/mastery_model.py`, `app/services/runtime_kg/schemas.py`, `app/services/runtime_kg/feature_flags.py`, `docs/research/longitudinal_validation/mastery_interpretation_and_use_specification.md`, `app/domain/educational_validation_schemas.py`  
- **Required evidence:** Approved charter, named decision rights and meeting cadence.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-01.01.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-01.01.json`  

## [ ] LEV-01.02 — Inventory every current mastery-related field, API response, dashboard label, recommendation rule, report statement and production-readiness claim.

- **Phase:** LEV-0  
- **Priority:** P0  
- **Type:** engineering  
- **Depends on:** 01.01  
- **Primary files:** `app/modules/progress/mastery_model.py`, `app/services/runtime_kg/schemas.py`, `app/services/runtime_kg/feature_flags.py`, `docs/research/longitudinal_validation/mastery_interpretation_and_use_specification.md`, `app/domain/educational_validation_schemas.py`  
- **Required evidence:** Complete mastery-usage inventory with source locations and owners.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-01.02.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-01.02.json`  

## [ ] LEV-01.03 — Separate the constructs of next-response probability, current independent proficiency, provisional mastery, durable mastery, retention and transfer.

- **Phase:** LEV-0  
- **Priority:** P0  
- **Type:** human_governance_or_research  
- **Depends on:** 01.02  
- **Primary files:** `app/modules/progress/mastery_model.py`, `app/services/runtime_kg/schemas.py`, `app/services/runtime_kg/feature_flags.py`, `docs/research/longitudinal_validation/mastery_interpretation_and_use_specification.md`, `app/domain/educational_validation_schemas.py`  
- **Required evidence:** Construct taxonomy approved by the educational measurement lead.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-01.03.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-01.03.json`  

## [ ] LEV-01.04 — Define the unit of inference for each construct: item, skill, CAPS topic, KG concept, prerequisite cluster, strand and grade-level outcome.

- **Phase:** LEV-0  
- **Priority:** P0  
- **Type:** governance_and_documentation  
- **Depends on:** 01.03  
- **Primary files:** `app/modules/progress/mastery_model.py`, `app/services/runtime_kg/schemas.py`, `app/services/runtime_kg/feature_flags.py`, `docs/research/longitudinal_validation/mastery_interpretation_and_use_specification.md`, `app/domain/educational_validation_schemas.py`  
- **Required evidence:** Inference-unit matrix with no ambiguous aggregation paths.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-01.04.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-01.04.json`  

## [ ] LEV-01.05 — Define the evidence conditions for each state, including minimum observations, independent items, assistance limits, recency and contradiction handling.

- **Phase:** LEV-0  
- **Priority:** P0  
- **Type:** human_governance_or_research  
- **Depends on:** 01.04  
- **Primary files:** `app/modules/progress/mastery_model.py`, `app/services/runtime_kg/schemas.py`, `app/services/runtime_kg/feature_flags.py`, `docs/research/longitudinal_validation/mastery_interpretation_and_use_specification.md`, `app/domain/educational_validation_schemas.py`  
- **Required evidence:** State-entry and state-exit rules documented and testable.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-01.05.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-01.05.json`  

## [ ] LEV-01.06 — Define required uncertainty outputs, confidence or credible intervals, evidence sufficiency indicators and stale-evidence behaviour.

- **Phase:** LEV-0  
- **Priority:** P0  
- **Type:** governance_and_documentation  
- **Depends on:** 01.05  
- **Primary files:** `app/modules/progress/mastery_model.py`, `app/services/runtime_kg/schemas.py`, `app/services/runtime_kg/feature_flags.py`, `docs/research/longitudinal_validation/mastery_interpretation_and_use_specification.md`, `app/domain/educational_validation_schemas.py`  
- **Required evidence:** Uncertainty policy linked to every mastery state.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-01.06.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-01.06.json`  

## [ ] LEV-01.07 — Define permitted instructional uses, teacher-facing uses, learner-facing wording, parent-facing wording and research-only uses.

- **Phase:** LEV-0  
- **Priority:** P0  
- **Type:** human_governance_or_research  
- **Depends on:** 01.06  
- **Primary files:** `app/modules/progress/mastery_model.py`, `app/services/runtime_kg/schemas.py`, `app/services/runtime_kg/feature_flags.py`, `docs/research/longitudinal_validation/mastery_interpretation_and_use_specification.md`, `app/domain/educational_validation_schemas.py`  
- **Required evidence:** Authorised-use register completed.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-01.07.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-01.07.json`  

## [ ] LEV-01.08 — Define prohibited uses, including high-stakes progression, formal marks, permanent labels and unsupported population extrapolation.

- **Phase:** LEV-0  
- **Priority:** P0  
- **Type:** governance_and_documentation  
- **Depends on:** 01.07  
- **Primary files:** `app/modules/progress/mastery_model.py`, `app/services/runtime_kg/schemas.py`, `app/services/runtime_kg/feature_flags.py`, `docs/research/longitudinal_validation/mastery_interpretation_and_use_specification.md`, `app/domain/educational_validation_schemas.py`  
- **Required evidence:** Prohibited-use register approved and enforced in product requirements.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-01.08.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-01.08.json`  

## [ ] LEV-01.09 — Write a validity-argument map linking each intended interpretation to evidence claims C1-C10 and required study outputs.

- **Phase:** LEV-0  
- **Priority:** P0  
- **Type:** governance_and_documentation  
- **Depends on:** 01.08  
- **Primary files:** `app/modules/progress/mastery_model.py`, `app/services/runtime_kg/schemas.py`, `app/services/runtime_kg/feature_flags.py`, `docs/research/longitudinal_validation/mastery_interpretation_and_use_specification.md`, `app/domain/educational_validation_schemas.py`  
- **Required evidence:** Validity argument reviewed by an independent psychometrician.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-01.09.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-01.09.json`  

## [ ] LEV-01.10 — Define mastery-state names and machine-readable enums, including insufficient evidence, emerging, provisional, retention unverified, durable, transfer demonstrated, stale and human review required.

- **Phase:** LEV-0  
- **Priority:** P0  
- **Type:** governance_and_documentation  
- **Depends on:** 01.09  
- **Primary files:** `app/modules/progress/mastery_model.py`, `app/services/runtime_kg/schemas.py`, `app/services/runtime_kg/feature_flags.py`, `docs/research/longitudinal_validation/mastery_interpretation_and_use_specification.md`, `app/domain/educational_validation_schemas.py`  
- **Required evidence:** Schema and terminology accepted by product, engineering and curriculum leads.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-01.10.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-01.10.json`  

## [ ] LEV-01.11 — Create age-appropriate explanations for learners and plain-language explanations for teachers and guardians.

- **Phase:** LEV-0  
- **Priority:** P0  
- **Type:** governance_and_documentation  
- **Depends on:** 01.10  
- **Primary files:** `app/modules/progress/mastery_model.py`, `app/services/runtime_kg/schemas.py`, `app/services/runtime_kg/feature_flags.py`, `docs/research/longitudinal_validation/mastery_interpretation_and_use_specification.md`, `app/domain/educational_validation_schemas.py`  
- **Required evidence:** User-language review shows no misleading certainty claims.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-01.11.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-01.11.json`  

## [ ] LEV-01.12 — Create a claims-change-control process requiring impact assessment whenever definitions, thresholds, graph structure or decision authority change.

- **Phase:** LEV-0  
- **Priority:** P0  
- **Type:** governance_and_documentation  
- **Depends on:** 01.11  
- **Primary files:** `app/modules/progress/mastery_model.py`, `app/services/runtime_kg/schemas.py`, `app/services/runtime_kg/feature_flags.py`, `docs/research/longitudinal_validation/mastery_interpretation_and_use_specification.md`, `app/domain/educational_validation_schemas.py`  
- **Required evidence:** Change-control workflow and approver matrix operational.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-01.12.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-01.12.json`  

## [ ] LEV-01.13 — Add automated documentation and API contract checks preventing unapproved mastery terminology from entering production surfaces.

- **Phase:** LEV-0  
- **Priority:** P0  
- **Type:** engineering  
- **Depends on:** 01.12  
- **Primary files:** `app/modules/progress/mastery_model.py`, `app/services/runtime_kg/schemas.py`, `app/services/runtime_kg/feature_flags.py`, `docs/research/longitudinal_validation/mastery_interpretation_and_use_specification.md`, `app/domain/educational_validation_schemas.py`  
- **Required evidence:** Terminology linter or contract tests pass across maintained interfaces.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-01.13.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-01.13.json`  

## [ ] LEV-01.14 — Approve and version the Mastery Interpretation and Use Specification.

- **Phase:** LEV-0  
- **Priority:** P0  
- **Type:** human_governance_or_research  
- **Depends on:** 01.13  
- **Primary files:** `app/modules/progress/mastery_model.py`, `app/services/runtime_kg/schemas.py`, `app/services/runtime_kg/feature_flags.py`, `docs/research/longitudinal_validation/mastery_interpretation_and_use_specification.md`, `app/domain/educational_validation_schemas.py`  
- **Required evidence:** Signed specification, version identifier and review date recorded.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-01.14.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-01.14.json`  

---

# LEV-WS02 — Independently review CAPS concepts and assessment items

**Definition of done:** CAPS concepts and items are independently reviewed.

**Objective:** Demonstrate that the knowledge graph, content mappings and validation instruments represent the intended Grade 4 Mathematics CAPS domain with adequate breadth, cognitive demand and fairness.

**Dependencies:** WS01 construct definitions; canonical CAPS corpus; item-bank governance; independent reviewers.

## [ ] LEV-02.01 — Freeze and hash the canonical CAPS source corpus, extraction outputs, graph version and curriculum mapping rules used for validation.

- **Phase:** LEV-0  
- **Priority:** P0  
- **Type:** operations  
- **Depends on:** 01.14  
- **Primary files:** `app/modules/diagnostics/item_bank_pipeline.py`, `app/modules/diagnostics/item_bank_service.py`, `app/repositories/item_bank_repository.py`, `docs/research/longitudinal_validation/caps_validation_blueprint.csv`, `docs/research/longitudinal_validation/validation_item_bank_manifest.json`  
- **Required evidence:** Immutable source and graph manifest.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-02.01.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-02.01.json`  

## [ ] LEV-02.02 — Create a CAPS coverage blueprint by strand, topic, subtopic, concept, cognitive demand, representation and expected instructional period.

- **Phase:** LEV-0  
- **Priority:** P0  
- **Type:** governance_and_documentation  
- **Depends on:** 02.01  
- **Primary files:** `app/modules/diagnostics/item_bank_pipeline.py`, `app/modules/diagnostics/item_bank_service.py`, `app/repositories/item_bank_repository.py`, `docs/research/longitudinal_validation/caps_validation_blueprint.csv`, `docs/research/longitudinal_validation/validation_item_bank_manifest.json`  
- **Required evidence:** Approved curriculum blueprint with explicit coverage targets.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-02.02.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-02.02.json`  

## [ ] LEV-02.03 — Map every KG concept to source pages, CAPS statements, prerequisite relationships, examples and assessment evidence requirements.

- **Phase:** LEV-0  
- **Priority:** P0  
- **Type:** governance_and_documentation  
- **Depends on:** 02.02  
- **Primary files:** `app/modules/diagnostics/item_bank_pipeline.py`, `app/modules/diagnostics/item_bank_service.py`, `app/repositories/item_bank_repository.py`, `docs/research/longitudinal_validation/caps_validation_blueprint.csv`, `docs/research/longitudinal_validation/validation_item_bank_manifest.json`  
- **Required evidence:** Complete provenance-linked concept map.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-02.03.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-02.03.json`  

## [ ] LEV-02.04 — Recruit independent Grade 4 mathematics teachers, curriculum specialists and a psychometric reviewer who did not author the mappings.

- **Phase:** LEV-0  
- **Priority:** P0  
- **Type:** human_governance_or_research  
- **Depends on:** 02.03  
- **Primary files:** `app/modules/diagnostics/item_bank_pipeline.py`, `app/modules/diagnostics/item_bank_service.py`, `app/repositories/item_bank_repository.py`, `docs/research/longitudinal_validation/caps_validation_blueprint.csv`, `docs/research/longitudinal_validation/validation_item_bank_manifest.json`  
- **Required evidence:** Conflict-of-interest declarations and reviewer roster.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-02.04.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-02.04.json`  

## [ ] LEV-02.05 — Conduct independent concept-level review for correctness, granularity, prerequisite logic, terminology and grade appropriateness.

- **Phase:** LEV-1  
- **Priority:** P0  
- **Type:** human_governance_or_research  
- **Depends on:** 02.04  
- **Primary files:** `app/modules/diagnostics/item_bank_pipeline.py`, `app/modules/diagnostics/item_bank_service.py`, `app/repositories/item_bank_repository.py`, `docs/research/longitudinal_validation/caps_validation_blueprint.csv`, `docs/research/longitudinal_validation/validation_item_bank_manifest.json`  
- **Required evidence:** Reviewer ratings, comments and adjudication record.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-02.05.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-02.05.json`  

## [ ] LEV-02.06 — Conduct graph-level review for missing concepts, duplicated concepts, circular prerequisites, overly broad nodes and invalid dependency paths.

- **Phase:** LEV-1  
- **Priority:** P0  
- **Type:** governance_and_documentation  
- **Depends on:** 02.05  
- **Primary files:** `app/modules/diagnostics/item_bank_pipeline.py`, `app/modules/diagnostics/item_bank_service.py`, `app/repositories/item_bank_repository.py`, `docs/research/longitudinal_validation/caps_validation_blueprint.csv`, `docs/research/longitudinal_validation/validation_item_bank_manifest.json`  
- **Required evidence:** Graph quality report and resolved issue register.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-02.06.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-02.06.json`  

## [ ] LEV-02.07 — Create an operational learning-item bank and a separately protected validation-item bank.

- **Phase:** LEV-1  
- **Priority:** P0  
- **Type:** governance_and_documentation  
- **Depends on:** 02.06  
- **Primary files:** `app/modules/diagnostics/item_bank_pipeline.py`, `app/modules/diagnostics/item_bank_service.py`, `app/repositories/item_bank_repository.py`, `docs/research/longitudinal_validation/caps_validation_blueprint.csv`, `docs/research/longitudinal_validation/validation_item_bank_manifest.json`  
- **Required evidence:** Physical/logical separation and exposure-control evidence.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-02.07.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-02.07.json`  

## [ ] LEV-02.08 — Tag every validation item with concept IDs, CAPS provenance, cognitive process, difficulty hypothesis, language load, representation, scoring rubric and misconception tags.

- **Phase:** LEV-1  
- **Priority:** P0  
- **Type:** governance_and_documentation  
- **Depends on:** 02.07  
- **Primary files:** `app/modules/diagnostics/item_bank_pipeline.py`, `app/modules/diagnostics/item_bank_service.py`, `app/repositories/item_bank_repository.py`, `docs/research/longitudinal_validation/caps_validation_blueprint.csv`, `docs/research/longitudinal_validation/validation_item_bank_manifest.json`  
- **Required evidence:** Item metadata completeness at the approved threshold.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-02.08.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-02.08.json`  

## [ ] LEV-02.09 — Perform independent content, language, accessibility, cultural-context and bias review of each validation item.

- **Phase:** LEV-1  
- **Priority:** P0  
- **Type:** human_governance_or_research  
- **Depends on:** 02.08  
- **Primary files:** `app/modules/diagnostics/item_bank_pipeline.py`, `app/modules/diagnostics/item_bank_service.py`, `app/repositories/item_bank_repository.py`, `docs/research/longitudinal_validation/caps_validation_blueprint.csv`, `docs/research/longitudinal_validation/validation_item_bank_manifest.json`  
- **Required evidence:** Item-review decision and remediation history.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-02.09.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-02.09.json`  

## [ ] LEV-02.10 — Run cognitive interviews or structured response-process sessions with a diverse pilot subsample.

- **Phase:** LEV-1  
- **Priority:** P0  
- **Type:** governance_and_documentation  
- **Depends on:** 02.09  
- **Primary files:** `app/modules/diagnostics/item_bank_pipeline.py`, `app/modules/diagnostics/item_bank_service.py`, `app/repositories/item_bank_repository.py`, `docs/research/longitudinal_validation/caps_validation_blueprint.csv`, `docs/research/longitudinal_validation/validation_item_bank_manifest.json`  
- **Required evidence:** Response-process report confirms intended reasoning is elicited.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-02.10.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-02.10.json`  

## [ ] LEV-02.11 — Pilot items and estimate difficulty, discrimination, information, local dependence, dimensionality and abnormal response patterns.

- **Phase:** LEV-2  
- **Priority:** P1  
- **Type:** analysis_and_validation  
- **Depends on:** 02.10  
- **Primary files:** `app/modules/diagnostics/item_bank_pipeline.py`, `app/modules/diagnostics/item_bank_service.py`, `app/repositories/item_bank_repository.py`, `docs/research/longitudinal_validation/caps_validation_blueprint.csv`, `docs/research/longitudinal_validation/validation_item_bank_manifest.json`  
- **Required evidence:** Pilot psychometric report and item disposition decisions.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-02.11.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-02.11.json`  

## [ ] LEV-02.12 — Test differential item functioning across approved comparison groups where sample sizes and lawful data collection permit.

- **Phase:** LEV-2  
- **Priority:** P1  
- **Type:** analysis_and_validation  
- **Depends on:** 02.11  
- **Primary files:** `app/modules/diagnostics/item_bank_pipeline.py`, `app/modules/diagnostics/item_bank_service.py`, `app/repositories/item_bank_repository.py`, `docs/research/longitudinal_validation/caps_validation_blueprint.csv`, `docs/research/longitudinal_validation/validation_item_bank_manifest.json`  
- **Required evidence:** DIF review with retained, revised or retired item decisions.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-02.12.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-02.12.json`  

## [ ] LEV-02.13 — Build parallel forms, common anchor sets and controlled exposure schedules for baseline, term, retention and transfer assessments.

- **Phase:** LEV-2  
- **Priority:** P1  
- **Type:** engineering  
- **Depends on:** 02.12  
- **Primary files:** `app/modules/diagnostics/item_bank_pipeline.py`, `app/modules/diagnostics/item_bank_service.py`, `app/repositories/item_bank_repository.py`, `docs/research/longitudinal_validation/caps_validation_blueprint.csv`, `docs/research/longitudinal_validation/validation_item_bank_manifest.json`  
- **Required evidence:** Form-equating plan and secure form manifests.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-02.13.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-02.13.json`  

## [ ] LEV-02.14 — Set approval, expiry, drift-review and retirement rules for concepts and items.

- **Phase:** LEV-2  
- **Priority:** P1  
- **Type:** human_governance_or_research  
- **Depends on:** 02.13  
- **Primary files:** `app/modules/diagnostics/item_bank_pipeline.py`, `app/modules/diagnostics/item_bank_service.py`, `app/repositories/item_bank_repository.py`, `docs/research/longitudinal_validation/caps_validation_blueprint.csv`, `docs/research/longitudinal_validation/validation_item_bank_manifest.json`  
- **Required evidence:** Lifecycle policy implemented in content governance.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-02.14.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-02.14.json`  

## [ ] LEV-02.15 — Obtain independent sign-off that the validation bank adequately represents the intended claims.

- **Phase:** LEV-2  
- **Priority:** P1  
- **Type:** human_governance_or_research  
- **Depends on:** 02.14  
- **Primary files:** `app/modules/diagnostics/item_bank_pipeline.py`, `app/modules/diagnostics/item_bank_service.py`, `app/repositories/item_bank_repository.py`, `docs/research/longitudinal_validation/caps_validation_blueprint.csv`, `docs/research/longitudinal_validation/validation_item_bank_manifest.json`  
- **Required evidence:** Signed curriculum and psychometric approval.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-02.15.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-02.15.json`  

## [ ] LEV-02.16 — Schedule annual CAPS, graph and item-bank re-review and event-triggered review after material changes.

- **Phase:** LEV-6  
- **Priority:** P2  
- **Type:** operations  
- **Depends on:** 02.15  
- **Primary files:** `app/modules/diagnostics/item_bank_pipeline.py`, `app/modules/diagnostics/item_bank_service.py`, `app/repositories/item_bank_repository.py`, `docs/research/longitudinal_validation/caps_validation_blueprint.csv`, `docs/research/longitudinal_validation/validation_item_bank_manifest.json`  
- **Required evidence:** Recurring review calendar and accountable owners.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-02.16.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-02.16.json`  

---

# LEV-WS03 — Make learner evidence and state changes fully traceable

**Definition of done:** Learner evidence and state changes are fully traceable.

**Objective:** Provide an immutable and reconstructable chain from learner interaction through model interpretation, state transition, recommendation, delivered action and later outcome.

**Dependencies:** WS01 state definitions; data architecture; event schemas; model registry; privacy design.

## [ ] LEV-03.01 — Specify the canonical learner-interaction event schema, including item, concept, content, assistance, timing, language, device and consent context.

- **Phase:** LEV-1  
- **Priority:** P0  
- **Type:** human_governance_or_research  
- **Depends on:** 01.10, 01.14  
- **Primary files:** `app/models/runtime_kg.py`, `app/services/runtime_kg/repository.py`, `app/services/runtime_kg/service.py`, `app/models/educational_validation.py`, `app/repositories/educational_validation_repository.py`  
- **Required evidence:** Versioned schema and data dictionary.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-03.01.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-03.01.json`  

## [ ] LEV-03.02 — Specify the canonical mastery-state-transition event with pre-state, post-state, uncertainty, evidence references, model version, graph version and update rationale.

- **Phase:** LEV-1  
- **Priority:** P0  
- **Type:** analysis_and_validation  
- **Depends on:** 03.01  
- **Primary files:** `app/models/runtime_kg.py`, `app/services/runtime_kg/repository.py`, `app/services/runtime_kg/service.py`, `app/models/educational_validation.py`, `app/repositories/educational_validation_repository.py`  
- **Required evidence:** Versioned transition schema.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-03.02.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-03.02.json`  

## [ ] LEV-03.03 — Implement append-only event persistence with stable event identifiers, ordering guarantees and tamper-evident integrity controls.

- **Phase:** LEV-1  
- **Priority:** P0  
- **Type:** engineering  
- **Depends on:** 03.02  
- **Primary files:** `app/models/runtime_kg.py`, `app/services/runtime_kg/repository.py`, `app/services/runtime_kg/service.py`, `app/models/educational_validation.py`, `app/repositories/educational_validation_repository.py`  
- **Required evidence:** Persistence tests and integrity verification pass.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-03.03.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-03.03.json`  

## [ ] LEV-03.04 — Create a model registry storing code commit, training data manifest, features, parameters, authorised population, limitations, expiry and rollback model.

- **Phase:** LEV-1  
- **Priority:** P0  
- **Type:** analysis_and_validation  
- **Depends on:** 03.03  
- **Primary files:** `app/models/runtime_kg.py`, `app/services/runtime_kg/repository.py`, `app/services/runtime_kg/service.py`, `app/models/educational_validation.py`, `app/repositories/educational_validation_repository.py`  
- **Required evidence:** Registry supports immutable model snapshots.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-03.04.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-03.04.json`  

## [ ] LEV-03.05 — Create a knowledge-graph snapshot registry and compatibility links between graph, item-bank and model versions.

- **Phase:** LEV-1  
- **Priority:** P0  
- **Type:** analysis_and_validation  
- **Depends on:** 03.04  
- **Primary files:** `app/models/runtime_kg.py`, `app/services/runtime_kg/repository.py`, `app/services/runtime_kg/service.py`, `app/models/educational_validation.py`, `app/repositories/educational_validation_repository.py`  
- **Required evidence:** Every projection resolves to a valid graph snapshot.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-03.05.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-03.05.json`  

## [ ] LEV-03.06 — Record recommendation decisions, policy version, accepted or overridden status, delivered content and subsequent learner outcome.

- **Phase:** LEV-1  
- **Priority:** P0  
- **Type:** human_governance_or_research  
- **Depends on:** 03.05  
- **Primary files:** `app/models/runtime_kg.py`, `app/services/runtime_kg/repository.py`, `app/services/runtime_kg/service.py`, `app/models/educational_validation.py`, `app/repositories/educational_validation_repository.py`  
- **Required evidence:** End-to-end recommendation provenance available.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-03.06.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-03.06.json`  

## [ ] LEV-03.07 — Implement trace-reconstruction APIs and internal tools for authorised reviewers.

- **Phase:** LEV-1  
- **Priority:** P0  
- **Type:** engineering  
- **Depends on:** 03.06  
- **Primary files:** `app/models/runtime_kg.py`, `app/services/runtime_kg/repository.py`, `app/services/runtime_kg/service.py`, `app/models/educational_validation.py`, `app/repositories/educational_validation_repository.py`  
- **Required evidence:** A sampled learner-concept history can be reconstructed deterministically.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-03.07.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-03.07.json`  

## [ ] LEV-03.08 — Implement idempotency, duplicate detection, late-event handling, clock-skew handling and correction-event semantics.

- **Phase:** LEV-1  
- **Priority:** P0  
- **Type:** engineering  
- **Depends on:** 03.07  
- **Primary files:** `app/models/runtime_kg.py`, `app/services/runtime_kg/repository.py`, `app/services/runtime_kg/service.py`, `app/models/educational_validation.py`, `app/repositories/educational_validation_repository.py`  
- **Required evidence:** Resilience and replay tests pass.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-03.08.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-03.08.json`  

## [ ] LEV-03.09 — Add event completeness, sequencing, orphan-reference and schema-version monitoring.

- **Phase:** LEV-1  
- **Priority:** P0  
- **Type:** engineering  
- **Depends on:** 03.08  
- **Primary files:** `app/models/runtime_kg.py`, `app/services/runtime_kg/repository.py`, `app/services/runtime_kg/service.py`, `app/models/educational_validation.py`, `app/repositories/educational_validation_repository.py`  
- **Required evidence:** Data-quality dashboards and alerts operational.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-03.09.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-03.09.json`  

## [ ] LEV-03.10 — Define lawful retention, pseudonymisation, de-identification, deletion and research-export rules for validation events.

- **Phase:** LEV-1  
- **Priority:** P0  
- **Type:** governance_and_documentation  
- **Depends on:** 03.09  
- **Primary files:** `app/models/runtime_kg.py`, `app/services/runtime_kg/repository.py`, `app/services/runtime_kg/service.py`, `app/models/educational_validation.py`, `app/repositories/educational_validation_repository.py`  
- **Required evidence:** Approved data-management plan and automated controls.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-03.10.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-03.10.json`  

## [ ] LEV-03.11 — Ensure erasure workflows preserve lawful aggregated evidence while removing or anonymising learner-identifiable data.

- **Phase:** LEV-1  
- **Priority:** P0  
- **Type:** human_governance_or_research  
- **Depends on:** 03.10  
- **Primary files:** `app/models/runtime_kg.py`, `app/services/runtime_kg/repository.py`, `app/services/runtime_kg/service.py`, `app/models/educational_validation.py`, `app/repositories/educational_validation_repository.py`  
- **Required evidence:** Erasure test suite and privacy review pass.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-03.11.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-03.11.json`  

## [ ] LEV-03.12 — Run replay validation comparing reconstructed states with production states across a representative sample.

- **Phase:** LEV-2  
- **Priority:** P1  
- **Type:** governance_and_documentation  
- **Depends on:** 03.11  
- **Primary files:** `app/models/runtime_kg.py`, `app/services/runtime_kg/repository.py`, `app/services/runtime_kg/service.py`, `app/models/educational_validation.py`, `app/repositories/educational_validation_repository.py`  
- **Required evidence:** No unexplained divergence above the approved tolerance.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-03.12.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-03.12.json`  

## [ ] LEV-03.13 — Run adversarial audit tests for event mutation, missing evidence, wrong model linkage and unauthorised access.

- **Phase:** LEV-2  
- **Priority:** P1  
- **Type:** analysis_and_validation  
- **Depends on:** 03.12  
- **Primary files:** `app/models/runtime_kg.py`, `app/services/runtime_kg/repository.py`, `app/services/runtime_kg/service.py`, `app/models/educational_validation.py`, `app/repositories/educational_validation_repository.py`  
- **Required evidence:** Security and audit findings resolved.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-03.13.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-03.13.json`  

## [ ] LEV-03.14 — Create a traceability evidence report and operating procedure for research, incidents and model challenges.

- **Phase:** LEV-2  
- **Priority:** P1  
- **Type:** analysis_and_validation  
- **Depends on:** 03.13  
- **Primary files:** `app/models/runtime_kg.py`, `app/services/runtime_kg/repository.py`, `app/services/runtime_kg/service.py`, `app/models/educational_validation.py`, `app/repositories/educational_validation_repository.py`  
- **Required evidence:** Operational runbook and approved evidence report.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-03.14.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-03.14.json`  

---

# LEV-WS04 — Calibrate mastery estimates against independent outcomes

**Definition of done:** Mastery estimates are calibrated against independent outcomes.

**Objective:** Show that predicted mastery probabilities correspond to observed success on independent, CAPS-aligned assessments not used to drive the learner's adaptive experience.

**Dependencies:** WS02 validation bank; WS03 traceability; prospective cohort; statistical analysis plan.

## [ ] LEV-04.01 — Pre-specify calibration estimands, time horizons, outcome definitions, minimum sample sizes and acceptable uncertainty.

- **Phase:** LEV-0  
- **Priority:** P0  
- **Type:** governance_and_documentation  
- **Depends on:** 02.15, 03.14  
- **Primary files:** `app/modules/diagnostics/irt_engine.py`, `app/modules/diagnostics/calibration_service.py`, `app/repositories/irt_repository.py`, `app/services/educational_validation/calibration.py`, `scripts/educational_validation/run_calibration_analysis.py`  
- **Required evidence:** Approved statistical analysis plan.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-04.01.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-04.01.json`  

## [ ] LEV-04.02 — Define independence rules preventing validation items, labels or later outcomes from leaking into training or adaptation.

- **Phase:** LEV-1  
- **Priority:** P0  
- **Type:** governance_and_documentation  
- **Depends on:** 04.01  
- **Primary files:** `app/modules/diagnostics/irt_engine.py`, `app/modules/diagnostics/calibration_service.py`, `app/repositories/irt_repository.py`, `app/services/educational_validation/calibration.py`, `scripts/educational_validation/run_calibration_analysis.py`  
- **Required evidence:** Leakage-control specification and tests.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-04.02.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-04.02.json`  

## [ ] LEV-04.03 — Build baseline, term and concept-level independent assessment administrations with standardised conditions.

- **Phase:** LEV-1  
- **Priority:** P0  
- **Type:** human_governance_or_research  
- **Depends on:** 04.02  
- **Primary files:** `app/modules/diagnostics/irt_engine.py`, `app/modules/diagnostics/calibration_service.py`, `app/repositories/irt_repository.py`, `app/services/educational_validation/calibration.py`, `scripts/educational_validation/run_calibration_analysis.py`  
- **Required evidence:** Administration manuals and secure form schedule.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-04.03.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-04.03.json`  

## [ ] LEV-04.04 — Collect shadow-mode predictions before independent outcomes are observed.

- **Phase:** LEV-2  
- **Priority:** P1  
- **Type:** human_governance_or_research  
- **Depends on:** 04.03  
- **Primary files:** `app/modules/diagnostics/irt_engine.py`, `app/modules/diagnostics/calibration_service.py`, `app/repositories/irt_repository.py`, `app/services/educational_validation/calibration.py`, `scripts/educational_validation/run_calibration_analysis.py`  
- **Required evidence:** Timestamped prediction snapshots with no retrospective replacement.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-04.04.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-04.04.json`  

## [ ] LEV-04.05 — Assess data completeness, representativeness, missingness and outcome quality before modelling.

- **Phase:** LEV-2  
- **Priority:** P1  
- **Type:** governance_and_documentation  
- **Depends on:** 04.04  
- **Primary files:** `app/modules/diagnostics/irt_engine.py`, `app/modules/diagnostics/calibration_service.py`, `app/repositories/irt_repository.py`, `app/services/educational_validation/calibration.py`, `scripts/educational_validation/run_calibration_analysis.py`  
- **Required evidence:** Data-quality gate passed.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-04.05.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-04.05.json`  

## [ ] LEV-04.06 — Compare the production model with simple baselines such as last response, rolling accuracy, IRT-only and non-temporal models.

- **Phase:** LEV-2  
- **Priority:** P1  
- **Type:** analysis_and_validation  
- **Depends on:** 04.05  
- **Primary files:** `app/modules/diagnostics/irt_engine.py`, `app/modules/diagnostics/calibration_service.py`, `app/repositories/irt_repository.py`, `app/services/educational_validation/calibration.py`, `scripts/educational_validation/run_calibration_analysis.py`  
- **Required evidence:** Benchmark report.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-04.06.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-04.06.json`  

## [ ] LEV-04.07 — Estimate calibration intercept, calibration slope, reliability curves, Brier score, log loss and uncertainty by concept.

- **Phase:** LEV-2  
- **Priority:** P1  
- **Type:** analysis_and_validation  
- **Depends on:** 04.06  
- **Primary files:** `app/modules/diagnostics/irt_engine.py`, `app/modules/diagnostics/calibration_service.py`, `app/repositories/irt_repository.py`, `app/services/educational_validation/calibration.py`, `scripts/educational_validation/run_calibration_analysis.py`  
- **Required evidence:** Calibration report with confidence intervals.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-04.07.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-04.07.json`  

## [ ] LEV-04.08 — Evaluate discrimination and ranking metrics without treating them as substitutes for calibration.

- **Phase:** LEV-2  
- **Priority:** P1  
- **Type:** analysis_and_validation  
- **Depends on:** 04.07  
- **Primary files:** `app/modules/diagnostics/irt_engine.py`, `app/modules/diagnostics/calibration_service.py`, `app/repositories/irt_repository.py`, `app/services/educational_validation/calibration.py`, `scripts/educational_validation/run_calibration_analysis.py`  
- **Required evidence:** AUC/PR results reported alongside calibration.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-04.08.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-04.08.json`  

## [ ] LEV-04.09 — Evaluate calibration by evidence count, item exposure, time since evidence, assistance level and concept difficulty.

- **Phase:** LEV-3  
- **Priority:** P1  
- **Type:** analysis_and_validation  
- **Depends on:** 04.08  
- **Primary files:** `app/modules/diagnostics/irt_engine.py`, `app/modules/diagnostics/calibration_service.py`, `app/repositories/irt_repository.py`, `app/services/educational_validation/calibration.py`, `scripts/educational_validation/run_calibration_analysis.py`  
- **Required evidence:** Conditional calibration analysis.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-04.09.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-04.09.json`  

## [ ] LEV-04.10 — Evaluate calibration on unseen learners, unseen items and later time windows.

- **Phase:** LEV-3  
- **Priority:** P1  
- **Type:** analysis_and_validation  
- **Depends on:** 04.09  
- **Primary files:** `app/modules/diagnostics/irt_engine.py`, `app/modules/diagnostics/calibration_service.py`, `app/repositories/irt_repository.py`, `app/services/educational_validation/calibration.py`, `scripts/educational_validation/run_calibration_analysis.py`  
- **Required evidence:** Out-of-sample report.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-04.10.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-04.10.json`  

## [ ] LEV-04.11 — Evaluate subgroup calibration and differential prediction for approved contexts.

- **Phase:** LEV-3  
- **Priority:** P1  
- **Type:** analysis_and_validation  
- **Depends on:** 04.10  
- **Primary files:** `app/modules/diagnostics/irt_engine.py`, `app/modules/diagnostics/calibration_service.py`, `app/repositories/irt_repository.py`, `app/services/educational_validation/calibration.py`, `scripts/educational_validation/run_calibration_analysis.py`  
- **Required evidence:** Fairness-calibration report.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-04.11.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-04.11.json`  

## [ ] LEV-04.12 — Develop and test recalibration methods without altering the underlying construct definition.

- **Phase:** LEV-3  
- **Priority:** P1  
- **Type:** governance_and_documentation  
- **Depends on:** 04.11  
- **Primary files:** `app/modules/diagnostics/irt_engine.py`, `app/modules/diagnostics/calibration_service.py`, `app/repositories/irt_repository.py`, `app/services/educational_validation/calibration.py`, `scripts/educational_validation/run_calibration_analysis.py`  
- **Required evidence:** Recalibration protocol and holdout results.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-04.12.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-04.12.json`  

## [ ] LEV-04.13 — Set model release thresholds, uncertainty displays and fallback behaviour when calibration fails.

- **Phase:** LEV-3  
- **Priority:** P1  
- **Type:** analysis_and_validation  
- **Depends on:** 04.12  
- **Primary files:** `app/modules/diagnostics/irt_engine.py`, `app/modules/diagnostics/calibration_service.py`, `app/repositories/irt_repository.py`, `app/services/educational_validation/calibration.py`, `scripts/educational_validation/run_calibration_analysis.py`  
- **Required evidence:** Operational gate configuration.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-04.13.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-04.13.json`  

## [ ] LEV-04.14 — Obtain independent psychometric review of the calibration evidence and limitations.

- **Phase:** LEV-3  
- **Priority:** P1  
- **Type:** human_governance_or_research  
- **Depends on:** 04.13  
- **Primary files:** `app/modules/diagnostics/irt_engine.py`, `app/modules/diagnostics/calibration_service.py`, `app/repositories/irt_repository.py`, `app/services/educational_validation/calibration.py`, `scripts/educational_validation/run_calibration_analysis.py`  
- **Required evidence:** Signed review decision.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-04.14.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-04.14.json`  

## [ ] LEV-04.15 — Automate recurring calibration monitoring against later independent outcomes.

- **Phase:** LEV-6  
- **Priority:** P2  
- **Type:** human_governance_or_research  
- **Depends on:** 04.14  
- **Primary files:** `app/modules/diagnostics/irt_engine.py`, `app/modules/diagnostics/calibration_service.py`, `app/repositories/irt_repository.py`, `app/services/educational_validation/calibration.py`, `scripts/educational_validation/run_calibration_analysis.py`  
- **Required evidence:** Production calibration dashboard and alerting.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-04.15.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-04.15.json`  

---

# LEV-WS05 — Quantify false-mastery and false-non-mastery risk

**Definition of done:** False-mastery and false-non-mastery rates are understood.

**Objective:** Measure classification error at every operational threshold, identify its causes and control the asymmetric educational risks of over- and under-estimating mastery.

**Dependencies:** WS01 thresholds; WS04 calibrated probabilities; delayed independent probes.

## [ ] LEV-05.01 — Define false mastery and false non-mastery for immediate, delayed and transfer outcomes.

- **Phase:** LEV-0  
- **Priority:** P0  
- **Type:** governance_and_documentation  
- **Depends on:** 01.05, 04.14  
- **Primary files:** `app/modules/progress/mastery_model.py`, `app/modules/diagnostics/irt_engine.py`, `app/services/runtime_kg/schemas.py`, `app/services/educational_validation/classification.py`, `scripts/educational_validation/run_classification_analysis.py`  
- **Required evidence:** Approved classification definitions.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-05.01.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-05.01.json`  

## [ ] LEV-05.02 — Document the educational cost of each error type for each intended decision.

- **Phase:** LEV-0  
- **Priority:** P0  
- **Type:** governance_and_documentation  
- **Depends on:** 05.01  
- **Primary files:** `app/modules/progress/mastery_model.py`, `app/modules/diagnostics/irt_engine.py`, `app/services/runtime_kg/schemas.py`, `app/services/educational_validation/classification.py`, `scripts/educational_validation/run_classification_analysis.py`  
- **Required evidence:** Decision-specific error-cost matrix.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-05.02.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-05.02.json`  

## [ ] LEV-05.03 — Set provisional safety ceilings and harm boundaries, subject to later evidence and independent approval.

- **Phase:** LEV-0  
- **Priority:** P0  
- **Type:** human_governance_or_research  
- **Depends on:** 05.02  
- **Primary files:** `app/modules/progress/mastery_model.py`, `app/modules/diagnostics/irt_engine.py`, `app/services/runtime_kg/schemas.py`, `app/services/educational_validation/classification.py`, `scripts/educational_validation/run_classification_analysis.py`  
- **Required evidence:** Threshold policy with rationale.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-05.03.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-05.03.json`  

## [ ] LEV-05.04 — Construct confusion matrices for each candidate mastery threshold and outcome horizon.

- **Phase:** LEV-2  
- **Priority:** P1  
- **Type:** governance_and_documentation  
- **Depends on:** 05.03  
- **Primary files:** `app/modules/progress/mastery_model.py`, `app/modules/diagnostics/irt_engine.py`, `app/services/runtime_kg/schemas.py`, `app/services/educational_validation/classification.py`, `scripts/educational_validation/run_classification_analysis.py`  
- **Required evidence:** Threshold-performance tables.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-05.04.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-05.04.json`  

## [ ] LEV-05.05 — Estimate sensitivity, specificity, predictive values, false discovery rate and false omission rate with uncertainty.

- **Phase:** LEV-2  
- **Priority:** P1  
- **Type:** analysis_and_validation  
- **Depends on:** 05.04  
- **Primary files:** `app/modules/progress/mastery_model.py`, `app/modules/diagnostics/irt_engine.py`, `app/services/runtime_kg/schemas.py`, `app/services/educational_validation/classification.py`, `scripts/educational_validation/run_classification_analysis.py`  
- **Required evidence:** Classification report.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-05.05.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-05.05.json`  

## [ ] LEV-05.06 — Estimate error by concept, difficulty, evidence count, hint use, response latency and time since learning.

- **Phase:** LEV-2  
- **Priority:** P1  
- **Type:** analysis_and_validation  
- **Depends on:** 05.05  
- **Primary files:** `app/modules/progress/mastery_model.py`, `app/modules/diagnostics/irt_engine.py`, `app/services/runtime_kg/schemas.py`, `app/services/educational_validation/classification.py`, `scripts/educational_validation/run_classification_analysis.py`  
- **Required evidence:** Error-source analysis.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-05.06.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-05.06.json`  

## [ ] LEV-05.07 — Investigate repeated-item exposure, guessing, copying, disengagement and assistance as causes of false mastery.

- **Phase:** LEV-2  
- **Priority:** P1  
- **Type:** governance_and_documentation  
- **Depends on:** 05.06  
- **Primary files:** `app/modules/progress/mastery_model.py`, `app/modules/diagnostics/irt_engine.py`, `app/services/runtime_kg/schemas.py`, `app/services/educational_validation/classification.py`, `scripts/educational_validation/run_classification_analysis.py`  
- **Required evidence:** Behavioural confound report.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-05.07.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-05.07.json`  

## [ ] LEV-05.08 — Investigate language load, poor item fit, missing opportunity to learn and interface problems as causes of false non-mastery.

- **Phase:** LEV-2  
- **Priority:** P1  
- **Type:** governance_and_documentation  
- **Depends on:** 05.07  
- **Primary files:** `app/modules/progress/mastery_model.py`, `app/modules/diagnostics/irt_engine.py`, `app/services/runtime_kg/schemas.py`, `app/services/educational_validation/classification.py`, `scripts/educational_validation/run_classification_analysis.py`  
- **Required evidence:** Measurement-confound report.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-05.08.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-05.08.json`  

## [ ] LEV-05.09 — Compare threshold policies: global, concept-specific, uncertainty-aware and cost-sensitive.

- **Phase:** LEV-3  
- **Priority:** P1  
- **Type:** analysis_and_validation  
- **Depends on:** 05.08  
- **Primary files:** `app/modules/progress/mastery_model.py`, `app/modules/diagnostics/irt_engine.py`, `app/services/runtime_kg/schemas.py`, `app/services/educational_validation/classification.py`, `scripts/educational_validation/run_classification_analysis.py`  
- **Required evidence:** Policy evaluation report.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-05.09.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-05.09.json`  

## [ ] LEV-05.10 — Introduce human-review and conservative fallback states for high-uncertainty classifications.

- **Phase:** LEV-3  
- **Priority:** P1  
- **Type:** governance_and_documentation  
- **Depends on:** 05.09  
- **Primary files:** `app/modules/progress/mastery_model.py`, `app/modules/diagnostics/irt_engine.py`, `app/services/runtime_kg/schemas.py`, `app/services/educational_validation/classification.py`, `scripts/educational_validation/run_classification_analysis.py`  
- **Required evidence:** Workflow and product behaviour verified.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-05.10.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-05.10.json`  

## [ ] LEV-05.11 — Evaluate error rates across approved learner contexts and identify unacceptable disparities.

- **Phase:** LEV-3  
- **Priority:** P1  
- **Type:** human_governance_or_research  
- **Depends on:** 05.10  
- **Primary files:** `app/modules/progress/mastery_model.py`, `app/modules/diagnostics/irt_engine.py`, `app/services/runtime_kg/schemas.py`, `app/services/educational_validation/classification.py`, `scripts/educational_validation/run_classification_analysis.py`  
- **Required evidence:** Subgroup error report.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-05.11.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-05.11.json`  

## [ ] LEV-05.12 — Run teacher adjudication studies on sampled disagreements between the model and independent outcomes.

- **Phase:** LEV-3  
- **Priority:** P1  
- **Type:** human_governance_or_research  
- **Depends on:** 05.11  
- **Primary files:** `app/modules/progress/mastery_model.py`, `app/modules/diagnostics/irt_engine.py`, `app/services/runtime_kg/schemas.py`, `app/services/educational_validation/classification.py`, `scripts/educational_validation/run_classification_analysis.py`  
- **Required evidence:** Disagreement taxonomy and adjudication evidence.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-05.12.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-05.12.json`  

## [ ] LEV-05.13 — Select and approve operational thresholds for each authorised use rather than one universal threshold.

- **Phase:** LEV-3  
- **Priority:** P1  
- **Type:** human_governance_or_research  
- **Depends on:** 05.12  
- **Primary files:** `app/modules/progress/mastery_model.py`, `app/modules/diagnostics/irt_engine.py`, `app/services/runtime_kg/schemas.py`, `app/services/educational_validation/classification.py`, `scripts/educational_validation/run_classification_analysis.py`  
- **Required evidence:** Use-specific threshold register.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-05.13.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-05.13.json`  

## [ ] LEV-05.14 — Monitor error rates continuously and automatically reduce decision authority when ceilings are exceeded.

- **Phase:** LEV-6  
- **Priority:** P2  
- **Type:** operations  
- **Depends on:** 05.13  
- **Primary files:** `app/modules/progress/mastery_model.py`, `app/modules/diagnostics/irt_engine.py`, `app/services/runtime_kg/schemas.py`, `app/services/educational_validation/classification.py`, `scripts/educational_validation/run_classification_analysis.py`  
- **Required evidence:** Alert, freeze and rollback controls tested.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-05.14.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-05.14.json`  

---

# LEV-WS06 — Demonstrate delayed-retention validity

**Definition of done:** Estimates predict delayed retention.

**Objective:** Show that mastery projections distinguish temporary success from knowledge retained after meaningful delays and reduced practice support.

**Dependencies:** WS02 parallel forms; WS03 timestamps; WS04 calibration; cohort follow-up.

## [ ] LEV-06.01 — Define retention horizons relevant to Grade 4 instruction, provisionally including 2-4 weeks, 8-12 weeks, end of term and cross-year follow-up.

- **Phase:** LEV-0  
- **Priority:** P0  
- **Type:** governance_and_documentation  
- **Depends on:** 02.15, 03.14, 04.14, 05.13  
- **Primary files:** `app/modules/progress/mastery_model.py`, `app/services/runtime_kg/service.py`, `app/modules/study_plans/runtime_kg_planner.py`, `app/services/educational_validation/retention.py`, `scripts/educational_validation/run_retention_analysis.py`  
- **Required evidence:** Approved retention framework.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-06.01.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-06.01.json`  

## [ ] LEV-06.02 — Create independent retention probes with parallel items and controlled overlap with instruction.

- **Phase:** LEV-1  
- **Priority:** P0  
- **Type:** human_governance_or_research  
- **Depends on:** 06.01  
- **Primary files:** `app/modules/progress/mastery_model.py`, `app/services/runtime_kg/service.py`, `app/modules/study_plans/runtime_kg_planner.py`, `app/services/educational_validation/retention.py`, `scripts/educational_validation/run_retention_analysis.py`  
- **Required evidence:** Retention-form manifests.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-06.02.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-06.02.json`  

## [ ] LEV-06.03 — Define when a mastery declaration becomes eligible for a retention probe and how re-practice affects interpretation.

- **Phase:** LEV-1  
- **Priority:** P0  
- **Type:** governance_and_documentation  
- **Depends on:** 06.02  
- **Primary files:** `app/modules/progress/mastery_model.py`, `app/services/runtime_kg/service.py`, `app/modules/study_plans/runtime_kg_planner.py`, `app/services/educational_validation/retention.py`, `scripts/educational_validation/run_retention_analysis.py`  
- **Required evidence:** Eligibility and censoring rules.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-06.03.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-06.03.json`  

## [ ] LEV-06.04 — Instrument exposure history, spacing, cumulative review and intervening instruction.

- **Phase:** LEV-1  
- **Priority:** P0  
- **Type:** engineering  
- **Depends on:** 06.03  
- **Primary files:** `app/modules/progress/mastery_model.py`, `app/services/runtime_kg/service.py`, `app/modules/study_plans/runtime_kg_planner.py`, `app/services/educational_validation/retention.py`, `scripts/educational_validation/run_retention_analysis.py`  
- **Required evidence:** Complete exposure timeline.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-06.04.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-06.04.json`  

## [ ] LEV-06.05 — Schedule and administer short-, medium- and long-delay assessments using standardised procedures.

- **Phase:** LEV-3  
- **Priority:** P1  
- **Type:** human_governance_or_research  
- **Depends on:** 06.04  
- **Primary files:** `app/modules/progress/mastery_model.py`, `app/services/runtime_kg/service.py`, `app/modules/study_plans/runtime_kg_planner.py`, `app/services/educational_validation/retention.py`, `scripts/educational_validation/run_retention_analysis.py`  
- **Required evidence:** Administration completion report.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-06.05.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-06.05.json`  

## [ ] LEV-06.06 — Model retention probability as a function of mastery estimate, uncertainty, evidence history and elapsed time.

- **Phase:** LEV-3  
- **Priority:** P1  
- **Type:** analysis_and_validation  
- **Depends on:** 06.05  
- **Primary files:** `app/modules/progress/mastery_model.py`, `app/services/runtime_kg/service.py`, `app/modules/study_plans/runtime_kg_planner.py`, `app/services/educational_validation/retention.py`, `scripts/educational_validation/run_retention_analysis.py`  
- **Required evidence:** Retention model report.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-06.06.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-06.06.json`  

## [ ] LEV-06.07 — Compare predictive value of mastery estimates with immediate correctness alone and other baselines.

- **Phase:** LEV-3  
- **Priority:** P1  
- **Type:** analysis_and_validation  
- **Depends on:** 06.06  
- **Primary files:** `app/modules/progress/mastery_model.py`, `app/services/runtime_kg/service.py`, `app/modules/study_plans/runtime_kg_planner.py`, `app/services/educational_validation/retention.py`, `scripts/educational_validation/run_retention_analysis.py`  
- **Required evidence:** Incremental-validity evidence.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-06.07.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-06.07.json`  

## [ ] LEV-06.08 — Estimate forgetting curves by concept and learner context, with appropriate multilevel uncertainty.

- **Phase:** LEV-3  
- **Priority:** P1  
- **Type:** human_governance_or_research  
- **Depends on:** 06.07  
- **Primary files:** `app/modules/progress/mastery_model.py`, `app/services/runtime_kg/service.py`, `app/modules/study_plans/runtime_kg_planner.py`, `app/services/educational_validation/retention.py`, `scripts/educational_validation/run_retention_analysis.py`  
- **Required evidence:** Forgetting-curve report.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-06.08.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-06.08.json`  

## [ ] LEV-06.09 — Test whether assisted success and repeated exposure produce weaker retention than independent success.

- **Phase:** LEV-3  
- **Priority:** P1  
- **Type:** human_governance_or_research  
- **Depends on:** 06.08  
- **Primary files:** `app/modules/progress/mastery_model.py`, `app/services/runtime_kg/service.py`, `app/modules/study_plans/runtime_kg_planner.py`, `app/services/educational_validation/retention.py`, `scripts/educational_validation/run_retention_analysis.py`  
- **Required evidence:** Assistance and exposure analysis.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-06.09.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-06.09.json`  

## [ ] LEV-06.10 — Evaluate whether uncertainty and staleness indicators correctly identify retention risk.

- **Phase:** LEV-3  
- **Priority:** P1  
- **Type:** analysis_and_validation  
- **Depends on:** 06.09  
- **Primary files:** `app/modules/progress/mastery_model.py`, `app/services/runtime_kg/service.py`, `app/modules/study_plans/runtime_kg_planner.py`, `app/services/educational_validation/retention.py`, `scripts/educational_validation/run_retention_analysis.py`  
- **Required evidence:** Staleness-validation report.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-06.10.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-06.10.json`  

## [ ] LEV-06.11 — Identify concept-specific retention thresholds and review schedules where justified.

- **Phase:** LEV-3  
- **Priority:** P1  
- **Type:** governance_and_documentation  
- **Depends on:** 06.10  
- **Primary files:** `app/modules/progress/mastery_model.py`, `app/services/runtime_kg/service.py`, `app/modules/study_plans/runtime_kg_planner.py`, `app/services/educational_validation/retention.py`, `scripts/educational_validation/run_retention_analysis.py`  
- **Required evidence:** Retention-aware policy proposal.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-06.11.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-06.11.json`  

## [ ] LEV-06.12 — Update the runtime KG state model to represent retention unverified, retained, stale and contradictory evidence states.

- **Phase:** LEV-3  
- **Priority:** P1  
- **Type:** analysis_and_validation  
- **Depends on:** 06.11  
- **Primary files:** `app/modules/progress/mastery_model.py`, `app/services/runtime_kg/service.py`, `app/modules/study_plans/runtime_kg_planner.py`, `app/services/educational_validation/retention.py`, `scripts/educational_validation/run_retention_analysis.py`  
- **Required evidence:** Schema, migration and behavioural tests.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-06.12.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-06.12.json`  

## [ ] LEV-06.13 — Test whether retention-aware review scheduling improves later independent outcomes.

- **Phase:** LEV-4  
- **Priority:** P2  
- **Type:** human_governance_or_research  
- **Depends on:** 06.12  
- **Primary files:** `app/modules/progress/mastery_model.py`, `app/services/runtime_kg/service.py`, `app/modules/study_plans/runtime_kg_planner.py`, `app/services/educational_validation/retention.py`, `scripts/educational_validation/run_retention_analysis.py`  
- **Required evidence:** Controlled policy evaluation.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-06.13.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-06.13.json`  

## [ ] LEV-06.14 — Repeat retention analyses in a later cohort or academic year.

- **Phase:** LEV-5  
- **Priority:** P2  
- **Type:** governance_and_documentation  
- **Depends on:** 06.13  
- **Primary files:** `app/modules/progress/mastery_model.py`, `app/services/runtime_kg/service.py`, `app/modules/study_plans/runtime_kg_planner.py`, `app/services/educational_validation/retention.py`, `scripts/educational_validation/run_retention_analysis.py`  
- **Required evidence:** Replication evidence.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-06.14.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-06.14.json`  

## [ ] LEV-06.15 — Monitor retention failure and recalibrate forgetting assumptions over time.

- **Phase:** LEV-6  
- **Priority:** P2  
- **Type:** operations  
- **Depends on:** 06.14  
- **Primary files:** `app/modules/progress/mastery_model.py`, `app/services/runtime_kg/service.py`, `app/modules/study_plans/runtime_kg_planner.py`, `app/services/educational_validation/retention.py`, `scripts/educational_validation/run_retention_analysis.py`  
- **Required evidence:** Operational retention dashboard.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-06.15.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-06.15.json`  

---

# LEV-WS07 — Demonstrate transfer validity

**Definition of done:** Estimates predict transfer to unfamiliar tasks.

**Objective:** Establish that learner-state projections predict application of knowledge to unfamiliar representations and related problems rather than memorisation of exposed items.

**Dependencies:** WS02 transfer bank; WS06 retention design; curriculum expert review.

## [ ] LEV-07.01 — Define near transfer, far transfer and unsupported extrapolation for each CAPS concept family.

- **Phase:** LEV-0  
- **Priority:** P0  
- **Type:** governance_and_documentation  
- **Depends on:** 02.15, 03.14, 06.03  
- **Primary files:** `app/services/runtime_kg/service.py`, `app/services/runtime_kg/schemas.py`, `app/modules/lessons/adaptive_remediation.py`, `app/services/educational_validation/transfer.py`, `scripts/educational_validation/run_transfer_analysis.py`  
- **Required evidence:** Transfer taxonomy.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-07.01.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-07.01.json`  

## [ ] LEV-07.02 — Create a protected transfer-item bank using unfamiliar wording, representation and problem contexts.

- **Phase:** LEV-1  
- **Priority:** P0  
- **Type:** governance_and_documentation  
- **Depends on:** 07.01  
- **Primary files:** `app/services/runtime_kg/service.py`, `app/services/runtime_kg/schemas.py`, `app/modules/lessons/adaptive_remediation.py`, `app/services/educational_validation/transfer.py`, `scripts/educational_validation/run_transfer_analysis.py`  
- **Required evidence:** Transfer-bank manifest.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-07.02.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-07.02.json`  

## [ ] LEV-07.03 — Ensure transfer items preserve the target mathematical construct while changing superficial features.

- **Phase:** LEV-1  
- **Priority:** P0  
- **Type:** governance_and_documentation  
- **Depends on:** 07.02  
- **Primary files:** `app/services/runtime_kg/service.py`, `app/services/runtime_kg/schemas.py`, `app/modules/lessons/adaptive_remediation.py`, `app/services/educational_validation/transfer.py`, `scripts/educational_validation/run_transfer_analysis.py`  
- **Required evidence:** Independent expert review.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-07.03.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-07.03.json`  

## [ ] LEV-07.04 — Map expected transfer relationships and prerequisite paths in the KG without using outcome data.

- **Phase:** LEV-1  
- **Priority:** P0  
- **Type:** governance_and_documentation  
- **Depends on:** 07.03  
- **Primary files:** `app/services/runtime_kg/service.py`, `app/services/runtime_kg/schemas.py`, `app/modules/lessons/adaptive_remediation.py`, `app/services/educational_validation/transfer.py`, `scripts/educational_validation/run_transfer_analysis.py`  
- **Required evidence:** Pre-registered transfer graph.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-07.04.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-07.04.json`  

## [ ] LEV-07.05 — Pilot transfer items for difficulty, discrimination, language load and unintended strategy requirements.

- **Phase:** LEV-2  
- **Priority:** P1  
- **Type:** governance_and_documentation  
- **Depends on:** 07.04  
- **Primary files:** `app/services/runtime_kg/service.py`, `app/services/runtime_kg/schemas.py`, `app/modules/lessons/adaptive_remediation.py`, `app/services/educational_validation/transfer.py`, `scripts/educational_validation/run_transfer_analysis.py`  
- **Required evidence:** Pilot item report.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-07.05.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-07.05.json`  

## [ ] LEV-07.06 — Collect transfer outcomes after mastery projections are frozen.

- **Phase:** LEV-3  
- **Priority:** P1  
- **Type:** human_governance_or_research  
- **Depends on:** 07.05  
- **Primary files:** `app/services/runtime_kg/service.py`, `app/services/runtime_kg/schemas.py`, `app/modules/lessons/adaptive_remediation.py`, `app/services/educational_validation/transfer.py`, `scripts/educational_validation/run_transfer_analysis.py`  
- **Required evidence:** Prospective transfer dataset.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-07.06.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-07.06.json`  

## [ ] LEV-07.07 — Estimate the relationship between concept mastery and near-transfer performance.

- **Phase:** LEV-3  
- **Priority:** P1  
- **Type:** analysis_and_validation  
- **Depends on:** 07.06  
- **Primary files:** `app/services/runtime_kg/service.py`, `app/services/runtime_kg/schemas.py`, `app/modules/lessons/adaptive_remediation.py`, `app/services/educational_validation/transfer.py`, `scripts/educational_validation/run_transfer_analysis.py`  
- **Required evidence:** Near-transfer validity report.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-07.07.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-07.07.json`  

## [ ] LEV-07.08 — Estimate far-transfer performance where curriculum and sample size support the claim.

- **Phase:** LEV-3  
- **Priority:** P1  
- **Type:** analysis_and_validation  
- **Depends on:** 07.07  
- **Primary files:** `app/services/runtime_kg/service.py`, `app/services/runtime_kg/schemas.py`, `app/modules/lessons/adaptive_remediation.py`, `app/services/educational_validation/transfer.py`, `scripts/educational_validation/run_transfer_analysis.py`  
- **Required evidence:** Far-transfer report with cautious scope.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-07.08.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-07.08.json`  

## [ ] LEV-07.09 — Compare graph-informed transfer predictions with flat skill and item-level baselines.

- **Phase:** LEV-3  
- **Priority:** P1  
- **Type:** analysis_and_validation  
- **Depends on:** 07.08  
- **Primary files:** `app/services/runtime_kg/service.py`, `app/services/runtime_kg/schemas.py`, `app/modules/lessons/adaptive_remediation.py`, `app/services/educational_validation/transfer.py`, `scripts/educational_validation/run_transfer_analysis.py`  
- **Required evidence:** Comparative model evidence.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-07.09.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-07.09.json`  

## [ ] LEV-07.10 — Test whether prerequisite mastery patterns predict successful transfer.

- **Phase:** LEV-3  
- **Priority:** P1  
- **Type:** analysis_and_validation  
- **Depends on:** 07.09  
- **Primary files:** `app/services/runtime_kg/service.py`, `app/services/runtime_kg/schemas.py`, `app/modules/lessons/adaptive_remediation.py`, `app/services/educational_validation/transfer.py`, `scripts/educational_validation/run_transfer_analysis.py`  
- **Required evidence:** Prerequisite-path analysis.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-07.10.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-07.10.json`  

## [ ] LEV-07.11 — Analyse transfer error by representation, language, context and learner subgroup.

- **Phase:** LEV-3  
- **Priority:** P1  
- **Type:** human_governance_or_research  
- **Depends on:** 07.10  
- **Primary files:** `app/services/runtime_kg/service.py`, `app/services/runtime_kg/schemas.py`, `app/modules/lessons/adaptive_remediation.py`, `app/services/educational_validation/transfer.py`, `scripts/educational_validation/run_transfer_analysis.py`  
- **Required evidence:** Transfer fairness report.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-07.11.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-07.11.json`  

## [ ] LEV-07.12 — Identify concepts for which the system must not infer transfer without direct evidence.

- **Phase:** LEV-3  
- **Priority:** P1  
- **Type:** governance_and_documentation  
- **Depends on:** 07.11  
- **Primary files:** `app/services/runtime_kg/service.py`, `app/services/runtime_kg/schemas.py`, `app/modules/lessons/adaptive_remediation.py`, `app/services/educational_validation/transfer.py`, `scripts/educational_validation/run_transfer_analysis.py`  
- **Required evidence:** Restricted-inference register.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-07.12.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-07.12.json`  

## [ ] LEV-07.13 — Test whether transfer-targeted recommendations improve unfamiliar-task performance.

- **Phase:** LEV-4  
- **Priority:** P2  
- **Type:** analysis_and_validation  
- **Depends on:** 07.12  
- **Primary files:** `app/services/runtime_kg/service.py`, `app/services/runtime_kg/schemas.py`, `app/modules/lessons/adaptive_remediation.py`, `app/services/educational_validation/transfer.py`, `scripts/educational_validation/run_transfer_analysis.py`  
- **Required evidence:** Impact-study transfer outcome.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-07.13.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-07.13.json`  

## [ ] LEV-07.14 — Replicate transfer findings using new items and a later cohort.

- **Phase:** LEV-5  
- **Priority:** P2  
- **Type:** governance_and_documentation  
- **Depends on:** 07.13  
- **Primary files:** `app/services/runtime_kg/service.py`, `app/services/runtime_kg/schemas.py`, `app/modules/lessons/adaptive_remediation.py`, `app/services/educational_validation/transfer.py`, `scripts/educational_validation/run_transfer_analysis.py`  
- **Required evidence:** Replication report.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-07.14.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-07.14.json`  

## [ ] LEV-07.15 — Maintain item-exposure controls and periodically refresh transfer instruments.

- **Phase:** LEV-6  
- **Priority:** P2  
- **Type:** governance_and_documentation  
- **Depends on:** 07.14  
- **Primary files:** `app/services/runtime_kg/service.py`, `app/services/runtime_kg/schemas.py`, `app/modules/lessons/adaptive_remediation.py`, `app/services/educational_validation/transfer.py`, `scripts/educational_validation/run_transfer_analysis.py`  
- **Required evidence:** Operational exposure and renewal controls.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-07.15.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-07.15.json`  

---

# LEV-WS08 — Validate educational plausibility of state transitions

**Definition of done:** State transitions are educationally plausible.

**Objective:** Demonstrate that mastery changes follow defensible learning, prerequisite, assistance, contradiction and forgetting logic rather than opaque predictive shortcuts.

**Dependencies:** WS01 state definitions; WS03 transition ledger; teacher and expert review.

## [ ] LEV-08.01 — Define invariants and reasonableness rules for mastery increases, decreases, uncertainty and prerequisite propagation.

- **Phase:** LEV-0  
- **Priority:** P0  
- **Type:** governance_and_documentation  
- **Depends on:** 01.14, 03.14  
- **Primary files:** `app/modules/progress/mastery_model.py`, `app/services/runtime_kg/integration.py`, `app/services/runtime_kg/service.py`, `app/services/educational_validation/state_reasonableness.py`, `tests/unit/educational_validation/test_state_reasonableness.py`  
- **Required evidence:** State-transition rule catalogue.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-08.01.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-08.01.json`  

## [ ] LEV-08.02 — Create synthetic and curated learner histories representing expected learning, guessing, assistance, contradiction, forgetting and recovery.

- **Phase:** LEV-1  
- **Priority:** P0  
- **Type:** human_governance_or_research  
- **Depends on:** 08.01  
- **Primary files:** `app/modules/progress/mastery_model.py`, `app/services/runtime_kg/integration.py`, `app/services/runtime_kg/service.py`, `app/services/educational_validation/state_reasonableness.py`, `tests/unit/educational_validation/test_state_reasonableness.py`  
- **Required evidence:** Golden transition fixtures.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-08.02.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-08.02.json`  

## [ ] LEV-08.03 — Implement automated tests for unrelated-concept leakage, impossible jumps and unsupported certainty.

- **Phase:** LEV-1  
- **Priority:** P0  
- **Type:** engineering  
- **Depends on:** 08.02  
- **Primary files:** `app/modules/progress/mastery_model.py`, `app/services/runtime_kg/integration.py`, `app/services/runtime_kg/service.py`, `app/services/educational_validation/state_reasonableness.py`, `tests/unit/educational_validation/test_state_reasonableness.py`  
- **Required evidence:** Transition invariant test suite.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-08.03.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-08.03.json`  

## [ ] LEV-08.04 — Implement tests ensuring assisted and repeated responses do not automatically equal independent mastery.

- **Phase:** LEV-1  
- **Priority:** P0  
- **Type:** human_governance_or_research  
- **Depends on:** 08.03  
- **Primary files:** `app/modules/progress/mastery_model.py`, `app/services/runtime_kg/integration.py`, `app/services/runtime_kg/service.py`, `app/services/educational_validation/state_reasonableness.py`, `tests/unit/educational_validation/test_state_reasonableness.py`  
- **Required evidence:** Assistance-aware test evidence.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-08.04.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-08.04.json`  

## [ ] LEV-08.05 — Implement tests for staleness and increased uncertainty after long evidence gaps.

- **Phase:** LEV-1  
- **Priority:** P0  
- **Type:** engineering  
- **Depends on:** 08.04  
- **Primary files:** `app/modules/progress/mastery_model.py`, `app/services/runtime_kg/integration.py`, `app/services/runtime_kg/service.py`, `app/services/educational_validation/state_reasonableness.py`, `tests/unit/educational_validation/test_state_reasonableness.py`  
- **Required evidence:** Staleness test evidence.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-08.05.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-08.05.json`  

## [ ] LEV-08.06 — Sample real transitions and have teachers and curriculum experts rate their plausibility using a standard rubric.

- **Phase:** LEV-2  
- **Priority:** P1  
- **Type:** governance_and_documentation  
- **Depends on:** 08.05  
- **Primary files:** `app/modules/progress/mastery_model.py`, `app/services/runtime_kg/integration.py`, `app/services/runtime_kg/service.py`, `app/services/educational_validation/state_reasonableness.py`, `tests/unit/educational_validation/test_state_reasonableness.py`  
- **Required evidence:** Expert-rating dataset.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-08.06.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-08.06.json`  

## [ ] LEV-08.07 — Measure inter-rater agreement and adjudicate systematic disagreement.

- **Phase:** LEV-2  
- **Priority:** P1  
- **Type:** analysis_and_validation  
- **Depends on:** 08.06  
- **Primary files:** `app/modules/progress/mastery_model.py`, `app/services/runtime_kg/integration.py`, `app/services/runtime_kg/service.py`, `app/services/educational_validation/state_reasonableness.py`, `tests/unit/educational_validation/test_state_reasonableness.py`  
- **Required evidence:** Agreement and adjudication report.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-08.07.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-08.07.json`  

## [ ] LEV-08.08 — Identify model features or graph relationships causing implausible transitions.

- **Phase:** LEV-2  
- **Priority:** P1  
- **Type:** analysis_and_validation  
- **Depends on:** 08.07  
- **Primary files:** `app/modules/progress/mastery_model.py`, `app/services/runtime_kg/integration.py`, `app/services/runtime_kg/service.py`, `app/services/educational_validation/state_reasonableness.py`, `tests/unit/educational_validation/test_state_reasonableness.py`  
- **Required evidence:** Root-cause analysis.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-08.08.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-08.08.json`  

## [ ] LEV-08.09 — Compare state trajectories with alternative models and simple baselines.

- **Phase:** LEV-2  
- **Priority:** P1  
- **Type:** analysis_and_validation  
- **Depends on:** 08.08  
- **Primary files:** `app/modules/progress/mastery_model.py`, `app/services/runtime_kg/integration.py`, `app/services/runtime_kg/service.py`, `app/services/educational_validation/state_reasonableness.py`, `tests/unit/educational_validation/test_state_reasonableness.py`  
- **Required evidence:** Trajectory comparison report.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-08.09.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-08.09.json`  

## [ ] LEV-08.10 — Test whether prerequisite propagation improves prediction without creating unsupported mastery changes.

- **Phase:** LEV-3  
- **Priority:** P1  
- **Type:** analysis_and_validation  
- **Depends on:** 08.09  
- **Primary files:** `app/modules/progress/mastery_model.py`, `app/services/runtime_kg/integration.py`, `app/services/runtime_kg/service.py`, `app/services/educational_validation/state_reasonableness.py`, `tests/unit/educational_validation/test_state_reasonableness.py`  
- **Required evidence:** Prerequisite propagation evaluation.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-08.10.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-08.10.json`  

## [ ] LEV-08.11 — Require explanation payloads naming the evidence and rules responsible for each material change.

- **Phase:** LEV-3  
- **Priority:** P1  
- **Type:** governance_and_documentation  
- **Depends on:** 08.10  
- **Primary files:** `app/modules/progress/mastery_model.py`, `app/services/runtime_kg/integration.py`, `app/services/runtime_kg/service.py`, `app/services/educational_validation/state_reasonableness.py`, `tests/unit/educational_validation/test_state_reasonableness.py`  
- **Required evidence:** Explanation contract tests.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-08.11.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-08.11.json`  

## [ ] LEV-08.12 — Introduce human-review queues for contradictory or high-impact transitions.

- **Phase:** LEV-3  
- **Priority:** P1  
- **Type:** governance_and_documentation  
- **Depends on:** 08.11  
- **Primary files:** `app/modules/progress/mastery_model.py`, `app/services/runtime_kg/integration.py`, `app/services/runtime_kg/service.py`, `app/services/educational_validation/state_reasonableness.py`, `tests/unit/educational_validation/test_state_reasonableness.py`  
- **Required evidence:** Operational review workflow.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-08.12.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-08.12.json`  

## [ ] LEV-08.13 — Set quantitative alert thresholds for unexplained jumps, reversals and cross-concept spill-over.

- **Phase:** LEV-3  
- **Priority:** P1  
- **Type:** operations  
- **Depends on:** 08.12  
- **Primary files:** `app/modules/progress/mastery_model.py`, `app/services/runtime_kg/integration.py`, `app/services/runtime_kg/service.py`, `app/services/educational_validation/state_reasonableness.py`, `tests/unit/educational_validation/test_state_reasonableness.py`  
- **Required evidence:** Monitoring policy.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-08.13.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-08.13.json`  

## [ ] LEV-08.14 — Run continuous transition-reasonableness surveillance after model, KG or content changes.

- **Phase:** LEV-6  
- **Priority:** P2  
- **Type:** analysis_and_validation  
- **Depends on:** 08.13  
- **Primary files:** `app/modules/progress/mastery_model.py`, `app/services/runtime_kg/integration.py`, `app/services/runtime_kg/service.py`, `app/services/educational_validation/state_reasonableness.py`, `tests/unit/educational_validation/test_state_reasonableness.py`  
- **Required evidence:** Production dashboard and regression gate.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-08.14.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-08.14.json`  

## [ ] LEV-08.15 — Maintain a public-facing limitations explanation and internal known-anomaly register.

- **Phase:** LEV-6  
- **Priority:** P2  
- **Type:** governance_and_documentation  
- **Depends on:** 08.14  
- **Primary files:** `app/modules/progress/mastery_model.py`, `app/services/runtime_kg/integration.py`, `app/services/runtime_kg/service.py`, `app/services/educational_validation/state_reasonableness.py`, `tests/unit/educational_validation/test_state_reasonableness.py`  
- **Required evidence:** Current limitations and anomaly records.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-08.15.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-08.15.json`  

---

# LEV-WS09 — Establish validity across relevant learner contexts

**Definition of done:** Results remain valid across relevant learner contexts.

**Objective:** Determine where the model is sufficiently valid across language, school, device, connectivity, attainment and support contexts, and constrain use outside supported contexts.

**Dependencies:** Lawful context data; adequate samples; WS04-WS08 metrics; fairness governance.

## [ ] LEV-09.01 — Define the intended learner population and every context dimension material to the model's use.

- **Phase:** LEV-0  
- **Priority:** P0  
- **Type:** human_governance_or_research  
- **Depends on:** 04.14, 05.13, 08.13  
- **Primary files:** `docs/diagnostics/assessment_quality_fairness_contract.md`, `app/modules/diagnostics/bias_review_router.py`, `app/modules/diagnostics/quality_scorer.py`, `app/services/educational_validation/fairness.py`, `scripts/educational_validation/run_fairness_analysis.py`  
- **Required evidence:** Population and context specification.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-09.01.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-09.01.json`  

## [ ] LEV-09.02 — Determine which context variables may lawfully and ethically be collected, for what purpose and for how long.

- **Phase:** LEV-0  
- **Priority:** P0  
- **Type:** governance_and_documentation  
- **Depends on:** 09.01  
- **Primary files:** `docs/diagnostics/assessment_quality_fairness_contract.md`, `app/modules/diagnostics/bias_review_router.py`, `app/modules/diagnostics/quality_scorer.py`, `app/services/educational_validation/fairness.py`, `scripts/educational_validation/run_fairness_analysis.py`  
- **Required evidence:** Approved data-minimisation and lawful-basis record.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-09.02.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-09.02.json`  

## [ ] LEV-09.03 — Define minimum subgroup sample requirements and rules for suppressing unstable estimates.

- **Phase:** LEV-0  
- **Priority:** P0  
- **Type:** governance_and_documentation  
- **Depends on:** 09.02  
- **Primary files:** `docs/diagnostics/assessment_quality_fairness_contract.md`, `app/modules/diagnostics/bias_review_router.py`, `app/modules/diagnostics/quality_scorer.py`, `app/services/educational_validation/fairness.py`, `scripts/educational_validation/run_fairness_analysis.py`  
- **Required evidence:** Analysis sufficiency policy.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-09.03.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-09.03.json`  

## [ ] LEV-09.04 — Design recruitment to include varied school contexts, baseline attainment, language, device and connectivity conditions.

- **Phase:** LEV-1  
- **Priority:** P0  
- **Type:** human_governance_or_research  
- **Depends on:** 09.03  
- **Primary files:** `docs/diagnostics/assessment_quality_fairness_contract.md`, `app/modules/diagnostics/bias_review_router.py`, `app/modules/diagnostics/quality_scorer.py`, `app/services/educational_validation/fairness.py`, `scripts/educational_validation/run_fairness_analysis.py`  
- **Required evidence:** Sampling and recruitment plan.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-09.04.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-09.04.json`  

## [ ] LEV-09.05 — Implement accessibility and accommodation metadata without conflating support with ability.

- **Phase:** LEV-1  
- **Priority:** P0  
- **Type:** engineering  
- **Depends on:** 09.04  
- **Primary files:** `docs/diagnostics/assessment_quality_fairness_contract.md`, `app/modules/diagnostics/bias_review_router.py`, `app/modules/diagnostics/quality_scorer.py`, `app/services/educational_validation/fairness.py`, `scripts/educational_validation/run_fairness_analysis.py`  
- **Required evidence:** Accessible assessment protocol.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-09.05.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-09.05.json`  

## [ ] LEV-09.06 — Measure representation, missingness, data quality and platform exposure by context.

- **Phase:** LEV-2  
- **Priority:** P1  
- **Type:** analysis_and_validation  
- **Depends on:** 09.05  
- **Primary files:** `docs/diagnostics/assessment_quality_fairness_contract.md`, `app/modules/diagnostics/bias_review_router.py`, `app/modules/diagnostics/quality_scorer.py`, `app/services/educational_validation/fairness.py`, `scripts/educational_validation/run_fairness_analysis.py`  
- **Required evidence:** Context data-quality report.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-09.06.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-09.06.json`  

## [ ] LEV-09.07 — Test differential item functioning and differential test functioning where estimable.

- **Phase:** LEV-2  
- **Priority:** P1  
- **Type:** analysis_and_validation  
- **Depends on:** 09.06  
- **Primary files:** `docs/diagnostics/assessment_quality_fairness_contract.md`, `app/modules/diagnostics/bias_review_router.py`, `app/modules/diagnostics/quality_scorer.py`, `app/services/educational_validation/fairness.py`, `scripts/educational_validation/run_fairness_analysis.py`  
- **Required evidence:** Measurement fairness report.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-09.07.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-09.07.json`  

## [ ] LEV-09.08 — Test subgroup calibration, discrimination, false mastery, false non-mastery, retention and transfer.

- **Phase:** LEV-3  
- **Priority:** P1  
- **Type:** governance_and_documentation  
- **Depends on:** 09.07  
- **Primary files:** `docs/diagnostics/assessment_quality_fairness_contract.md`, `app/modules/diagnostics/bias_review_router.py`, `app/modules/diagnostics/quality_scorer.py`, `app/services/educational_validation/fairness.py`, `scripts/educational_validation/run_fairness_analysis.py`  
- **Required evidence:** Context validity report.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-09.08.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-09.08.json`  

## [ ] LEV-09.09 — Analyse interaction effects for device, connectivity, language and opportunity to learn.

- **Phase:** LEV-3  
- **Priority:** P1  
- **Type:** analysis_and_validation  
- **Depends on:** 09.08  
- **Primary files:** `docs/diagnostics/assessment_quality_fairness_contract.md`, `app/modules/diagnostics/bias_review_router.py`, `app/modules/diagnostics/quality_scorer.py`, `app/services/educational_validation/fairness.py`, `scripts/educational_validation/run_fairness_analysis.py`  
- **Required evidence:** Context-interaction analysis.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-09.09.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-09.09.json`  

## [ ] LEV-09.10 — Conduct qualitative investigation with teachers and learners where quantitative differences appear.

- **Phase:** LEV-3  
- **Priority:** P1  
- **Type:** governance_and_documentation  
- **Depends on:** 09.09  
- **Primary files:** `docs/diagnostics/assessment_quality_fairness_contract.md`, `app/modules/diagnostics/bias_review_router.py`, `app/modules/diagnostics/quality_scorer.py`, `app/services/educational_validation/fairness.py`, `scripts/educational_validation/run_fairness_analysis.py`  
- **Required evidence:** Mixed-methods explanation report.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-09.10.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-09.10.json`  

## [ ] LEV-09.11 — Identify unsupported or weakly supported contexts and impose conservative product behaviour.

- **Phase:** LEV-3  
- **Priority:** P1  
- **Type:** governance_and_documentation  
- **Depends on:** 09.10  
- **Primary files:** `docs/diagnostics/assessment_quality_fairness_contract.md`, `app/modules/diagnostics/bias_review_router.py`, `app/modules/diagnostics/quality_scorer.py`, `app/services/educational_validation/fairness.py`, `scripts/educational_validation/run_fairness_analysis.py`  
- **Required evidence:** Supported-context matrix and feature restrictions.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-09.11.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-09.11.json`  

## [ ] LEV-09.12 — Remediate item, interface, content, model or access causes and re-test affected groups.

- **Phase:** LEV-3  
- **Priority:** P1  
- **Type:** analysis_and_validation  
- **Depends on:** 09.11  
- **Primary files:** `docs/diagnostics/assessment_quality_fairness_contract.md`, `app/modules/diagnostics/bias_review_router.py`, `app/modules/diagnostics/quality_scorer.py`, `app/services/educational_validation/fairness.py`, `scripts/educational_validation/run_fairness_analysis.py`  
- **Required evidence:** Remediation and revalidation evidence.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-09.12.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-09.12.json`  

## [ ] LEV-09.13 — Pre-register impact-study subgroup analyses and harm boundaries.

- **Phase:** LEV-4  
- **Priority:** P2  
- **Type:** governance_and_documentation  
- **Depends on:** 09.12  
- **Primary files:** `docs/diagnostics/assessment_quality_fairness_contract.md`, `app/modules/diagnostics/bias_review_router.py`, `app/modules/diagnostics/quality_scorer.py`, `app/services/educational_validation/fairness.py`, `scripts/educational_validation/run_fairness_analysis.py`  
- **Required evidence:** Approved subgroup analysis plan.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-09.13.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-09.13.json`  

## [ ] LEV-09.14 — Confirm generalisability in an additional school, region, language or delivery context where feasible.

- **Phase:** LEV-5  
- **Priority:** P2  
- **Type:** human_governance_or_research  
- **Depends on:** 09.13  
- **Primary files:** `docs/diagnostics/assessment_quality_fairness_contract.md`, `app/modules/diagnostics/bias_review_router.py`, `app/modules/diagnostics/quality_scorer.py`, `app/services/educational_validation/fairness.py`, `scripts/educational_validation/run_fairness_analysis.py`  
- **Required evidence:** External-context replication evidence.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-09.14.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-09.14.json`  

## [ ] LEV-09.15 — Monitor context mix and automatically flag population shift beyond the authorised envelope.

- **Phase:** LEV-6  
- **Priority:** P2  
- **Type:** operations  
- **Depends on:** 09.14  
- **Primary files:** `docs/diagnostics/assessment_quality_fairness_contract.md`, `app/modules/diagnostics/bias_review_router.py`, `app/modules/diagnostics/quality_scorer.py`, `app/services/educational_validation/fairness.py`, `scripts/educational_validation/run_fairness_analysis.py`  
- **Required evidence:** Population-drift dashboard and response runbook.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-09.15.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-09.15.json`  

---

# LEV-WS10 — Demonstrate that mastery-informed recommendations improve learning

**Definition of done:** Recommendations improve independent learning outcomes.

**Objective:** Establish through a controlled study that decisions based on the learner-state model produce better independent educational outcomes than an appropriate comparison condition.

**Dependencies:** Provisional completion of WS01-WS09; intervention stability; school partnerships; independent outcomes.

## [ ] LEV-10.01 — Define the intervention precisely: which recommendations use the KG, when, for whom and with what teacher authority.

- **Phase:** LEV-0  
- **Priority:** P0  
- **Type:** human_governance_or_research  
- **Depends on:** 01.14, 02.15, 03.14, 04.14, 05.13, 06.13, 07.13, 08.13, 09.13  
- **Primary files:** `app/modules/study_plans/runtime_kg_planner.py`, `app/modules/lessons/adaptive_remediation.py`, `app/services/study_plan_service_v2.py`, `docs/research/longitudinal_validation/impact_study_protocol.md`, `scripts/educational_validation/run_impact_analysis.py`  
- **Required evidence:** Intervention specification.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-10.01.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-10.01.json`  

## [ ] LEV-10.02 — Select the comparison condition, such as non-adaptive CAPS sequence or appropriate business-as-usual provision.

- **Phase:** LEV-0  
- **Priority:** P0  
- **Type:** governance_and_documentation  
- **Depends on:** 10.01  
- **Primary files:** `app/modules/study_plans/runtime_kg_planner.py`, `app/modules/lessons/adaptive_remediation.py`, `app/services/study_plan_service_v2.py`, `docs/research/longitudinal_validation/impact_study_protocol.md`, `scripts/educational_validation/run_impact_analysis.py`  
- **Required evidence:** Comparison-condition specification.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-10.02.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-10.02.json`  

## [ ] LEV-10.03 — Choose the experimental design, preferably cluster randomisation where feasible, and pre-specify the estimand.

- **Phase:** LEV-0  
- **Priority:** P0  
- **Type:** governance_and_documentation  
- **Depends on:** 10.02  
- **Primary files:** `app/modules/study_plans/runtime_kg_planner.py`, `app/modules/lessons/adaptive_remediation.py`, `app/services/study_plan_service_v2.py`, `docs/research/longitudinal_validation/impact_study_protocol.md`, `scripts/educational_validation/run_impact_analysis.py`  
- **Required evidence:** Approved trial protocol.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-10.03.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-10.03.json`  

## [ ] LEV-10.04 — Perform statistical power and precision calculations accounting for clustering, expected attrition and multiple outcomes.

- **Phase:** LEV-0  
- **Priority:** P0  
- **Type:** governance_and_documentation  
- **Depends on:** 10.03  
- **Primary files:** `app/modules/study_plans/runtime_kg_planner.py`, `app/modules/lessons/adaptive_remediation.py`, `app/services/study_plan_service_v2.py`, `docs/research/longitudinal_validation/impact_study_protocol.md`, `scripts/educational_validation/run_impact_analysis.py`  
- **Required evidence:** Power analysis.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-10.04.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-10.04.json`  

## [ ] LEV-10.05 — Pre-register primary and secondary outcomes, subgroup analyses, mediation analyses and harm boundaries.

- **Phase:** LEV-0  
- **Priority:** P0  
- **Type:** governance_and_documentation  
- **Depends on:** 10.04  
- **Primary files:** `app/modules/study_plans/runtime_kg_planner.py`, `app/modules/lessons/adaptive_remediation.py`, `app/services/study_plan_service_v2.py`, `docs/research/longitudinal_validation/impact_study_protocol.md`, `scripts/educational_validation/run_impact_analysis.py`  
- **Required evidence:** Public or controlled pre-registration record.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-10.05.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-10.05.json`  

## [ ] LEV-10.06 — Obtain ethics, privacy, school, guardian and learner approvals and establish complaint and withdrawal procedures.

- **Phase:** LEV-0  
- **Priority:** P0  
- **Type:** human_governance_or_research  
- **Depends on:** 10.05  
- **Primary files:** `app/modules/study_plans/runtime_kg_planner.py`, `app/modules/lessons/adaptive_remediation.py`, `app/services/study_plan_service_v2.py`, `docs/research/longitudinal_validation/impact_study_protocol.md`, `scripts/educational_validation/run_impact_analysis.py`  
- **Required evidence:** Complete governance approvals.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-10.06.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-10.06.json`  

## [ ] LEV-10.07 — Build randomisation, allocation concealment, contamination tracking and study-condition enforcement.

- **Phase:** LEV-1  
- **Priority:** P0  
- **Type:** engineering  
- **Depends on:** 10.06  
- **Primary files:** `app/modules/study_plans/runtime_kg_planner.py`, `app/modules/lessons/adaptive_remediation.py`, `app/services/study_plan_service_v2.py`, `docs/research/longitudinal_validation/impact_study_protocol.md`, `scripts/educational_validation/run_impact_analysis.py`  
- **Required evidence:** Validated trial operations tooling.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-10.07.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-10.07.json`  

## [ ] LEV-10.08 — Create independent baseline and outcome assessments and assessor procedures.

- **Phase:** LEV-1  
- **Priority:** P0  
- **Type:** human_governance_or_research  
- **Depends on:** 10.07  
- **Primary files:** `app/modules/study_plans/runtime_kg_planner.py`, `app/modules/lessons/adaptive_remediation.py`, `app/services/study_plan_service_v2.py`, `docs/research/longitudinal_validation/impact_study_protocol.md`, `scripts/educational_validation/run_impact_analysis.py`  
- **Required evidence:** Assessment operations package.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-10.08.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-10.08.json`  

## [ ] LEV-10.09 — Recruit schools/classes, establish baseline equivalence and document the participant flow.

- **Phase:** LEV-4  
- **Priority:** P2  
- **Type:** human_governance_or_research  
- **Depends on:** 10.08  
- **Primary files:** `app/modules/study_plans/runtime_kg_planner.py`, `app/modules/lessons/adaptive_remediation.py`, `app/services/study_plan_service_v2.py`, `docs/research/longitudinal_validation/impact_study_protocol.md`, `scripts/educational_validation/run_impact_analysis.py`  
- **Required evidence:** Recruitment and baseline report.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-10.09.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-10.09.json`  

## [ ] LEV-10.10 — Deliver the intervention while measuring fidelity, actual exposure, teacher use and cross-condition contamination.

- **Phase:** LEV-4  
- **Priority:** P2  
- **Type:** human_governance_or_research  
- **Depends on:** 10.09  
- **Primary files:** `app/modules/study_plans/runtime_kg_planner.py`, `app/modules/lessons/adaptive_remediation.py`, `app/services/study_plan_service_v2.py`, `docs/research/longitudinal_validation/impact_study_protocol.md`, `scripts/educational_validation/run_impact_analysis.py`  
- **Required evidence:** Implementation-fidelity dashboard.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-10.10.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-10.10.json`  

## [ ] LEV-10.11 — Measure independent achievement, retention, transfer, time to durable mastery and opportunity to learn.

- **Phase:** LEV-4  
- **Priority:** P2  
- **Type:** human_governance_or_research  
- **Depends on:** 10.10  
- **Primary files:** `app/modules/study_plans/runtime_kg_planner.py`, `app/modules/lessons/adaptive_remediation.py`, `app/services/study_plan_service_v2.py`, `docs/research/longitudinal_validation/impact_study_protocol.md`, `scripts/educational_validation/run_impact_analysis.py`  
- **Required evidence:** Complete outcome dataset.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-10.11.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-10.11.json`  

## [ ] LEV-10.12 — Conduct intention-to-treat analysis with clustering, missing-data and attrition handling.

- **Phase:** LEV-4  
- **Priority:** P2  
- **Type:** governance_and_documentation  
- **Depends on:** 10.11  
- **Primary files:** `app/modules/study_plans/runtime_kg_planner.py`, `app/modules/lessons/adaptive_remediation.py`, `app/services/study_plan_service_v2.py`, `docs/research/longitudinal_validation/impact_study_protocol.md`, `scripts/educational_validation/run_impact_analysis.py`  
- **Required evidence:** Primary impact report.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-10.12.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-10.12.json`  

## [ ] LEV-10.13 — Conduct pre-specified per-protocol, exposure, mediation, sensitivity and subgroup analyses without replacing the primary result.

- **Phase:** LEV-4  
- **Priority:** P2  
- **Type:** analysis_and_validation  
- **Depends on:** 10.12  
- **Primary files:** `app/modules/study_plans/runtime_kg_planner.py`, `app/modules/lessons/adaptive_remediation.py`, `app/services/study_plan_service_v2.py`, `docs/research/longitudinal_validation/impact_study_protocol.md`, `scripts/educational_validation/run_impact_analysis.py`  
- **Required evidence:** Secondary analysis report.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-10.13.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-10.13.json`  

## [ ] LEV-10.14 — Determine whether any benefit is explained only by additional time on task or narrower content exposure.

- **Phase:** LEV-4  
- **Priority:** P2  
- **Type:** governance_and_documentation  
- **Depends on:** 10.13  
- **Primary files:** `app/modules/study_plans/runtime_kg_planner.py`, `app/modules/lessons/adaptive_remediation.py`, `app/services/study_plan_service_v2.py`, `docs/research/longitudinal_validation/impact_study_protocol.md`, `scripts/educational_validation/run_impact_analysis.py`  
- **Required evidence:** Mechanism and curriculum-breadth analysis.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-10.14.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-10.14.json`  

## [ ] LEV-10.15 — Obtain independent methodological review and produce a transparent limitations statement.

- **Phase:** LEV-4  
- **Priority:** P2  
- **Type:** human_governance_or_research  
- **Depends on:** 10.14  
- **Primary files:** `app/modules/study_plans/runtime_kg_planner.py`, `app/modules/lessons/adaptive_remediation.py`, `app/services/study_plan_service_v2.py`, `docs/research/longitudinal_validation/impact_study_protocol.md`, `scripts/educational_validation/run_impact_analysis.py`  
- **Required evidence:** Independent review and final study report.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-10.15.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-10.15.json`  

## [ ] LEV-10.16 — Repeat or extend the impact test before broad educational-effectiveness claims.

- **Phase:** LEV-5  
- **Priority:** P2  
- **Type:** governance_and_documentation  
- **Depends on:** 10.15  
- **Primary files:** `app/modules/study_plans/runtime_kg_planner.py`, `app/modules/lessons/adaptive_remediation.py`, `app/services/study_plan_service_v2.py`, `docs/research/longitudinal_validation/impact_study_protocol.md`, `scripts/educational_validation/run_impact_analysis.py`  
- **Required evidence:** Replication or confirmatory study evidence.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-10.16.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-10.16.json`  

---

# LEV-WS11 — Measure and control adverse educational effects

**Definition of done:** Adverse effects are measured and acceptably controlled.

**Objective:** Identify, quantify and mitigate unintended effects such as curriculum narrowing, excessive remediation, frustration, inequitable opportunity, over-reliance and privacy harm.

**Dependencies:** Consequence theory; instrumentation; teacher/learner feedback; safety governance.

## [ ] LEV-11.01 — Create an adverse-consequence taxonomy covering educational, psychological, operational, fairness, privacy and teacher-workflow harms.

- **Phase:** LEV-0  
- **Priority:** P0  
- **Type:** human_governance_or_research  
- **Depends on:** 01.08, 03.09  
- **Primary files:** `app/services/runtime_kg/feature_flags.py`, `app/services/consent_service.py`, `app/services/audit_service.py`, `app/services/educational_validation/safety.py`, `docs/research/longitudinal_validation/adverse_consequence_monitoring_plan.md`  
- **Required evidence:** Approved harm taxonomy.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-11.01.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-11.01.json`  

## [ ] LEV-11.02 — Define severity, likelihood, detectability, escalation and stop-work criteria.

- **Phase:** LEV-0  
- **Priority:** P0  
- **Type:** governance_and_documentation  
- **Depends on:** 11.01  
- **Primary files:** `app/services/runtime_kg/feature_flags.py`, `app/services/consent_service.py`, `app/services/audit_service.py`, `app/services/educational_validation/safety.py`, `docs/research/longitudinal_validation/adverse_consequence_monitoring_plan.md`  
- **Required evidence:** Risk-scoring and escalation policy.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-11.02.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-11.02.json`  

## [ ] LEV-11.03 — Define leading and lagging indicators for each major harm.

- **Phase:** LEV-0  
- **Priority:** P0  
- **Type:** governance_and_documentation  
- **Depends on:** 11.02  
- **Primary files:** `app/services/runtime_kg/feature_flags.py`, `app/services/consent_service.py`, `app/services/audit_service.py`, `app/services/educational_validation/safety.py`, `docs/research/longitudinal_validation/adverse_consequence_monitoring_plan.md`  
- **Required evidence:** Harm indicator catalogue.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-11.03.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-11.03.json`  

## [ ] LEV-11.04 — Instrument curriculum breadth, grade-level exposure, repetition burden, remediation duration, abandonment, help requests and overrides.

- **Phase:** LEV-1  
- **Priority:** P0  
- **Type:** engineering  
- **Depends on:** 11.03  
- **Primary files:** `app/services/runtime_kg/feature_flags.py`, `app/services/consent_service.py`, `app/services/audit_service.py`, `app/services/educational_validation/safety.py`, `docs/research/longitudinal_validation/adverse_consequence_monitoring_plan.md`  
- **Required evidence:** Consequence event coverage verified.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-11.04.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-11.04.json`  

## [ ] LEV-11.05 — Implement learner-, guardian- and teacher-facing feedback and complaint channels.

- **Phase:** LEV-1  
- **Priority:** P0  
- **Type:** human_governance_or_research  
- **Depends on:** 11.04  
- **Primary files:** `app/services/runtime_kg/feature_flags.py`, `app/services/consent_service.py`, `app/services/audit_service.py`, `app/services/educational_validation/safety.py`, `docs/research/longitudinal_validation/adverse_consequence_monitoring_plan.md`  
- **Required evidence:** Accessible feedback channels and response SLA.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-11.05.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-11.05.json`  

## [ ] LEV-11.06 — Establish baseline rates before high-impact adaptation is enabled.

- **Phase:** LEV-2  
- **Priority:** P1  
- **Type:** governance_and_documentation  
- **Depends on:** 11.05  
- **Primary files:** `app/services/runtime_kg/feature_flags.py`, `app/services/consent_service.py`, `app/services/audit_service.py`, `app/services/educational_validation/safety.py`, `docs/research/longitudinal_validation/adverse_consequence_monitoring_plan.md`  
- **Required evidence:** Baseline consequence report.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-11.06.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-11.06.json`  

## [ ] LEV-11.07 — Review sampled learner pathways for over-remediation, skipped content, lock-in and feedback-loop behaviour.

- **Phase:** LEV-2  
- **Priority:** P1  
- **Type:** human_governance_or_research  
- **Depends on:** 11.06  
- **Primary files:** `app/services/runtime_kg/feature_flags.py`, `app/services/consent_service.py`, `app/services/audit_service.py`, `app/services/educational_validation/safety.py`, `docs/research/longitudinal_validation/adverse_consequence_monitoring_plan.md`  
- **Required evidence:** Pathway audit report.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-11.07.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-11.07.json`  

## [ ] LEV-11.08 — Analyse adverse indicators by learner context and model error type.

- **Phase:** LEV-3  
- **Priority:** P1  
- **Type:** human_governance_or_research  
- **Depends on:** 11.07  
- **Primary files:** `app/services/runtime_kg/feature_flags.py`, `app/services/consent_service.py`, `app/services/audit_service.py`, `app/services/educational_validation/safety.py`, `docs/research/longitudinal_validation/adverse_consequence_monitoring_plan.md`  
- **Required evidence:** Differential consequence report.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-11.08.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-11.08.json`  

## [ ] LEV-11.09 — Run qualitative interviews or focus groups on frustration, trust, understanding and teacher workload.

- **Phase:** LEV-3  
- **Priority:** P1  
- **Type:** human_governance_or_research  
- **Depends on:** 11.08  
- **Primary files:** `app/services/runtime_kg/feature_flags.py`, `app/services/consent_service.py`, `app/services/audit_service.py`, `app/services/educational_validation/safety.py`, `docs/research/longitudinal_validation/adverse_consequence_monitoring_plan.md`  
- **Required evidence:** Qualitative safety report.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-11.09.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-11.09.json`  

## [ ] LEV-11.10 — Define and implement mitigations such as content floors, maximum remediation windows, teacher override and mandatory grade-level exposure.

- **Phase:** LEV-3  
- **Priority:** P1  
- **Type:** human_governance_or_research  
- **Depends on:** 11.09  
- **Primary files:** `app/services/runtime_kg/feature_flags.py`, `app/services/consent_service.py`, `app/services/audit_service.py`, `app/services/educational_validation/safety.py`, `docs/research/longitudinal_validation/adverse_consequence_monitoring_plan.md`  
- **Required evidence:** Mitigation controls and tests.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-11.10.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-11.10.json`  

## [ ] LEV-11.11 — Implement automated freeze, rollback or authority-reduction behaviour for breached harm thresholds.

- **Phase:** LEV-3  
- **Priority:** P1  
- **Type:** engineering  
- **Depends on:** 11.10  
- **Primary files:** `app/services/runtime_kg/feature_flags.py`, `app/services/consent_service.py`, `app/services/audit_service.py`, `app/services/educational_validation/safety.py`, `docs/research/longitudinal_validation/adverse_consequence_monitoring_plan.md`  
- **Required evidence:** Safety automation rehearsal.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-11.11.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-11.11.json`  

## [ ] LEV-11.12 — Include adverse outcomes and curriculum-breadth measures in the controlled impact study.

- **Phase:** LEV-4  
- **Priority:** P2  
- **Type:** governance_and_documentation  
- **Depends on:** 11.11  
- **Primary files:** `app/services/runtime_kg/feature_flags.py`, `app/services/consent_service.py`, `app/services/audit_service.py`, `app/services/educational_validation/safety.py`, `docs/research/longitudinal_validation/adverse_consequence_monitoring_plan.md`  
- **Required evidence:** Trial consequence results.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-11.12.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-11.12.json`  

## [ ] LEV-11.13 — Convene an independent safety review before expanding model authority.

- **Phase:** LEV-4  
- **Priority:** P2  
- **Type:** human_governance_or_research  
- **Depends on:** 11.12  
- **Primary files:** `app/services/runtime_kg/feature_flags.py`, `app/services/consent_service.py`, `app/services/audit_service.py`, `app/services/educational_validation/safety.py`, `docs/research/longitudinal_validation/adverse_consequence_monitoring_plan.md`  
- **Required evidence:** Safety approval decision.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-11.13.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-11.13.json`  

## [ ] LEV-11.14 — Operate a recurring educational-safety review board and publish internal trend reports.

- **Phase:** LEV-6  
- **Priority:** P2  
- **Type:** operations  
- **Depends on:** 11.13  
- **Primary files:** `app/services/runtime_kg/feature_flags.py`, `app/services/consent_service.py`, `app/services/audit_service.py`, `app/services/educational_validation/safety.py`, `docs/research/longitudinal_validation/adverse_consequence_monitoring_plan.md`  
- **Required evidence:** Meeting records and action register.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-11.14.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-11.14.json`  

## [ ] LEV-11.15 — Maintain post-incident learning, corrective-action verification and reauthorisation requirements.

- **Phase:** LEV-6  
- **Priority:** P2  
- **Type:** operations  
- **Depends on:** 11.14  
- **Primary files:** `app/services/runtime_kg/feature_flags.py`, `app/services/consent_service.py`, `app/services/audit_service.py`, `app/services/educational_validation/safety.py`, `docs/research/longitudinal_validation/adverse_consequence_monitoring_plan.md`  
- **Required evidence:** Closed-loop incident governance.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-11.15.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-11.15.json`  

---

# LEV-WS12 — Replicate findings in another cohort or academic year

**Definition of done:** Findings replicate in another cohort or academic year.

**Objective:** Show that measurement and impact findings are not artefacts of one cohort, calendar period, school set, item form or model snapshot.

**Dependencies:** Completed initial longitudinal cohort; frozen replication protocol; new cohort access.

## [ ] LEV-12.01 — Identify the primary claims requiring replication and rank them by decision importance.

- **Phase:** LEV-3  
- **Priority:** P1  
- **Type:** governance_and_documentation  
- **Depends on:** 10.15, 11.13  
- **Primary files:** `docs/research/mastery_model`, `scripts/mastery_research`, `docs/release-evidence/roadmap-reconciliation/rr-013-advanced-mastery-model-research`, `docs/research/longitudinal_validation/replication_protocol.md`, `scripts/educational_validation/run_replication_analysis.py`  
- **Required evidence:** Replication claim register.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-12.01.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-12.01.json`  

## [ ] LEV-12.02 — Freeze the original protocol, analysis code, model, graph, item and outcome definitions.

- **Phase:** LEV-3  
- **Priority:** P1  
- **Type:** analysis_and_validation  
- **Depends on:** 12.01  
- **Primary files:** `docs/research/mastery_model`, `scripts/mastery_research`, `docs/release-evidence/roadmap-reconciliation/rr-013-advanced-mastery-model-research`, `docs/research/longitudinal_validation/replication_protocol.md`, `scripts/educational_validation/run_replication_analysis.py`  
- **Required evidence:** Primary-study reproducibility package.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-12.02.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-12.02.json`  

## [ ] LEV-12.03 — Pre-specify what will remain identical and what will intentionally vary in the replication.

- **Phase:** LEV-3  
- **Priority:** P1  
- **Type:** governance_and_documentation  
- **Depends on:** 12.02  
- **Primary files:** `docs/research/mastery_model`, `scripts/mastery_research`, `docs/release-evidence/roadmap-reconciliation/rr-013-advanced-mastery-model-research`, `docs/research/longitudinal_validation/replication_protocol.md`, `scripts/educational_validation/run_replication_analysis.py`  
- **Required evidence:** Replication design specification.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-12.03.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-12.03.json`  

## [ ] LEV-12.04 — Select a later cohort or academic year and, where possible, additional schools or contexts.

- **Phase:** LEV-3  
- **Priority:** P1  
- **Type:** governance_and_documentation  
- **Depends on:** 12.03  
- **Primary files:** `docs/research/mastery_model`, `scripts/mastery_research`, `docs/release-evidence/roadmap-reconciliation/rr-013-advanced-mastery-model-research`, `docs/research/longitudinal_validation/replication_protocol.md`, `scripts/educational_validation/run_replication_analysis.py`  
- **Required evidence:** Replication sampling plan.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-12.04.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-12.04.json`  

## [ ] LEV-12.05 — Refresh only items required for exposure control while preserving scale linkage through anchors.

- **Phase:** LEV-3  
- **Priority:** P1  
- **Type:** governance_and_documentation  
- **Depends on:** 12.04  
- **Primary files:** `docs/research/mastery_model`, `scripts/mastery_research`, `docs/release-evidence/roadmap-reconciliation/rr-013-advanced-mastery-model-research`, `docs/research/longitudinal_validation/replication_protocol.md`, `scripts/educational_validation/run_replication_analysis.py`  
- **Required evidence:** Linked replication assessment forms.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-12.05.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-12.05.json`  

## [ ] LEV-12.06 — Prospectively capture predictions using the authorised model or explicitly versioned successor.

- **Phase:** LEV-5  
- **Priority:** P2  
- **Type:** analysis_and_validation  
- **Depends on:** 12.05  
- **Primary files:** `docs/research/mastery_model`, `scripts/mastery_research`, `docs/release-evidence/roadmap-reconciliation/rr-013-advanced-mastery-model-research`, `docs/research/longitudinal_validation/replication_protocol.md`, `scripts/educational_validation/run_replication_analysis.py`  
- **Required evidence:** Frozen replication predictions.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-12.06.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-12.06.json`  

## [ ] LEV-12.07 — Repeat calibration, classification, retention, transfer and state-reasonableness analyses.

- **Phase:** LEV-5  
- **Priority:** P2  
- **Type:** governance_and_documentation  
- **Depends on:** 12.06  
- **Primary files:** `docs/research/mastery_model`, `scripts/mastery_research`, `docs/release-evidence/roadmap-reconciliation/rr-013-advanced-mastery-model-research`, `docs/research/longitudinal_validation/replication_protocol.md`, `scripts/educational_validation/run_replication_analysis.py`  
- **Required evidence:** Replication measurement report.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-12.07.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-12.07.json`  

## [ ] LEV-12.08 — Repeat the impact analysis or a confirmatory effectiveness design where feasible.

- **Phase:** LEV-5  
- **Priority:** P2  
- **Type:** governance_and_documentation  
- **Depends on:** 12.07  
- **Primary files:** `docs/research/mastery_model`, `scripts/mastery_research`, `docs/release-evidence/roadmap-reconciliation/rr-013-advanced-mastery-model-research`, `docs/research/longitudinal_validation/replication_protocol.md`, `scripts/educational_validation/run_replication_analysis.py`  
- **Required evidence:** Replication impact report.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-12.08.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-12.08.json`  

## [ ] LEV-12.09 — Compare effect direction, magnitude, uncertainty, calibration and subgroup patterns with the original.

- **Phase:** LEV-5  
- **Priority:** P2  
- **Type:** analysis_and_validation  
- **Depends on:** 12.08  
- **Primary files:** `docs/research/mastery_model`, `scripts/mastery_research`, `docs/release-evidence/roadmap-reconciliation/rr-013-advanced-mastery-model-research`, `docs/research/longitudinal_validation/replication_protocol.md`, `scripts/educational_validation/run_replication_analysis.py`  
- **Required evidence:** Cross-study synthesis.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-12.09.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-12.09.json`  

## [ ] LEV-12.10 — Investigate non-replication through population, curriculum, item, teacher-use, platform and model-change analyses.

- **Phase:** LEV-5  
- **Priority:** P2  
- **Type:** human_governance_or_research  
- **Depends on:** 12.09  
- **Primary files:** `docs/research/mastery_model`, `scripts/mastery_research`, `docs/release-evidence/roadmap-reconciliation/rr-013-advanced-mastery-model-research`, `docs/research/longitudinal_validation/replication_protocol.md`, `scripts/educational_validation/run_replication_analysis.py`  
- **Required evidence:** Non-replication root-cause report.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-12.10.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-12.10.json`  

## [ ] LEV-12.11 — Run sensitivity analyses using the original and updated model versions on comparable data.

- **Phase:** LEV-5  
- **Priority:** P2  
- **Type:** analysis_and_validation  
- **Depends on:** 12.10  
- **Primary files:** `docs/research/mastery_model`, `scripts/mastery_research`, `docs/release-evidence/roadmap-reconciliation/rr-013-advanced-mastery-model-research`, `docs/research/longitudinal_validation/replication_protocol.md`, `scripts/educational_validation/run_replication_analysis.py`  
- **Required evidence:** Version-comparison evidence.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-12.11.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-12.11.json`  

## [ ] LEV-12.12 — Define which claims generalise, which require narrower scope and which must be withdrawn.

- **Phase:** LEV-5  
- **Priority:** P2  
- **Type:** governance_and_documentation  
- **Depends on:** 12.11  
- **Primary files:** `docs/research/mastery_model`, `scripts/mastery_research`, `docs/release-evidence/roadmap-reconciliation/rr-013-advanced-mastery-model-research`, `docs/research/longitudinal_validation/replication_protocol.md`, `scripts/educational_validation/run_replication_analysis.py`  
- **Required evidence:** Revised authorised-use register.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-12.12.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-12.12.json`  

## [ ] LEV-12.13 — Obtain independent review of replication strength and residual uncertainty.

- **Phase:** LEV-5  
- **Priority:** P2  
- **Type:** human_governance_or_research  
- **Depends on:** 12.12  
- **Primary files:** `docs/research/mastery_model`, `scripts/mastery_research`, `docs/release-evidence/roadmap-reconciliation/rr-013-advanced-mastery-model-research`, `docs/research/longitudinal_validation/replication_protocol.md`, `scripts/educational_validation/run_replication_analysis.py`  
- **Required evidence:** Independent replication decision.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-12.13.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-12.13.json`  

## [ ] LEV-12.14 — Set future replication cadence for major model families and high-impact uses.

- **Phase:** LEV-6  
- **Priority:** P2  
- **Type:** analysis_and_validation  
- **Depends on:** 12.13  
- **Primary files:** `docs/research/mastery_model`, `scripts/mastery_research`, `docs/release-evidence/roadmap-reconciliation/rr-013-advanced-mastery-model-research`, `docs/research/longitudinal_validation/replication_protocol.md`, `scripts/educational_validation/run_replication_analysis.py`  
- **Required evidence:** Ongoing replication policy.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-12.14.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-12.14.json`  

---

# LEV-WS13 — Operate drift detection and revalidation controls

**Definition of done:** Drift and revalidation controls operate in production.

**Objective:** Ensure the validated model remains within its authorised evidence envelope as learners, items, content, graph structure, interaction design and software evolve.

**Dependencies:** Production telemetry; model/graph registry; reference metrics; SRE integration.

## [ ] LEV-13.01 — Define drift types: population, concept prevalence, item parameter, calibration, performance, feature, label, graph, content and policy drift.

- **Phase:** LEV-3  
- **Priority:** P1  
- **Type:** governance_and_documentation  
- **Depends on:** 03.14, 04.14, 05.14, 08.14, 09.15, 11.14, 12.13  
- **Primary files:** `app/services/runtime_kg/feature_flags.py`, `app/services/runtime_kg/acceptance.py`, `prometheus`, `app/services/educational_validation/drift.py`, `scripts/educational_validation/check_educational_model_drift.py`  
- **Required evidence:** Drift taxonomy.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-13.01.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-13.01.json`  

## [ ] LEV-13.02 — Create authorised reference distributions and validation baselines for each production model.

- **Phase:** LEV-3  
- **Priority:** P1  
- **Type:** analysis_and_validation  
- **Depends on:** 13.01  
- **Primary files:** `app/services/runtime_kg/feature_flags.py`, `app/services/runtime_kg/acceptance.py`, `prometheus`, `app/services/educational_validation/drift.py`, `scripts/educational_validation/check_educational_model_drift.py`  
- **Required evidence:** Baseline registry.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-13.02.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-13.02.json`  

## [ ] LEV-13.03 — Define warning, intervention and freeze thresholds with statistical and educational rationale.

- **Phase:** LEV-3  
- **Priority:** P1  
- **Type:** operations  
- **Depends on:** 13.02  
- **Primary files:** `app/services/runtime_kg/feature_flags.py`, `app/services/runtime_kg/acceptance.py`, `prometheus`, `app/services/educational_validation/drift.py`, `scripts/educational_validation/check_educational_model_drift.py`  
- **Required evidence:** Drift-threshold policy.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-13.03.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-13.03.json`  

## [ ] LEV-13.04 — Implement dashboards for calibration, error, retention, transfer, state reasonableness and context mix.

- **Phase:** LEV-3  
- **Priority:** P1  
- **Type:** engineering  
- **Depends on:** 13.03  
- **Primary files:** `app/services/runtime_kg/feature_flags.py`, `app/services/runtime_kg/acceptance.py`, `prometheus`, `app/services/educational_validation/drift.py`, `scripts/educational_validation/check_educational_model_drift.py`  
- **Required evidence:** Monitoring dashboards.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-13.04.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-13.04.json`  

## [ ] LEV-13.05 — Implement item and anchor drift monitoring and automatic quarantine of suspect items.

- **Phase:** LEV-3  
- **Priority:** P1  
- **Type:** engineering  
- **Depends on:** 13.04  
- **Primary files:** `app/services/runtime_kg/feature_flags.py`, `app/services/runtime_kg/acceptance.py`, `prometheus`, `app/services/educational_validation/drift.py`, `scripts/educational_validation/check_educational_model_drift.py`  
- **Required evidence:** Item-drift controls.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-13.05.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-13.05.json`  

## [ ] LEV-13.06 — Implement graph-change impact analysis covering renamed, merged, split, added and removed concepts.

- **Phase:** LEV-3  
- **Priority:** P1  
- **Type:** engineering  
- **Depends on:** 13.05  
- **Primary files:** `app/services/runtime_kg/feature_flags.py`, `app/services/runtime_kg/acceptance.py`, `prometheus`, `app/services/educational_validation/drift.py`, `scripts/educational_validation/check_educational_model_drift.py`  
- **Required evidence:** Graph compatibility checker.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-13.06.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-13.06.json`  

## [ ] LEV-13.07 — Implement shadow evaluation for candidate models and policies before promotion.

- **Phase:** LEV-3  
- **Priority:** P1  
- **Type:** engineering  
- **Depends on:** 13.06  
- **Primary files:** `app/services/runtime_kg/feature_flags.py`, `app/services/runtime_kg/acceptance.py`, `prometheus`, `app/services/educational_validation/drift.py`, `scripts/educational_validation/check_educational_model_drift.py`  
- **Required evidence:** Shadow-deployment evidence.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-13.07.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-13.07.json`  

## [ ] LEV-13.08 — Define model expiry dates, revalidation intervals and mandatory triggers after material change.

- **Phase:** LEV-3  
- **Priority:** P1  
- **Type:** analysis_and_validation  
- **Depends on:** 13.07  
- **Primary files:** `app/services/runtime_kg/feature_flags.py`, `app/services/runtime_kg/acceptance.py`, `prometheus`, `app/services/educational_validation/drift.py`, `scripts/educational_validation/check_educational_model_drift.py`  
- **Required evidence:** Model lifecycle policy.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-13.08.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-13.08.json`  

## [ ] LEV-13.09 — Test alerts, authority reduction, feature flags, rollback and last-validated-model recovery.

- **Phase:** LEV-4  
- **Priority:** P2  
- **Type:** analysis_and_validation  
- **Depends on:** 13.08  
- **Primary files:** `app/services/runtime_kg/feature_flags.py`, `app/services/runtime_kg/acceptance.py`, `prometheus`, `app/services/educational_validation/drift.py`, `scripts/educational_validation/check_educational_model_drift.py`  
- **Required evidence:** Operational game-day evidence.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-13.09.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-13.09.json`  

## [ ] LEV-13.10 — Validate monitoring sensitivity using known perturbations and historical back-testing.

- **Phase:** LEV-5  
- **Priority:** P2  
- **Type:** analysis_and_validation  
- **Depends on:** 13.09  
- **Primary files:** `app/services/runtime_kg/feature_flags.py`, `app/services/runtime_kg/acceptance.py`, `prometheus`, `app/services/educational_validation/drift.py`, `scripts/educational_validation/check_educational_model_drift.py`  
- **Required evidence:** Monitoring validation report.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-13.10.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-13.10.json`  

## [ ] LEV-13.11 — Create recurring educational model review meetings combining SRE, psychometrics, curriculum and fairness evidence.

- **Phase:** LEV-6  
- **Priority:** P2  
- **Type:** analysis_and_validation  
- **Depends on:** 13.10  
- **Primary files:** `app/services/runtime_kg/feature_flags.py`, `app/services/runtime_kg/acceptance.py`, `prometheus`, `app/services/educational_validation/drift.py`, `scripts/educational_validation/check_educational_model_drift.py`  
- **Required evidence:** Review cadence and minutes.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-13.11.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-13.11.json`  

## [ ] LEV-13.12 — Automate evidence capture for every model promotion, recalibration, threshold change and rollback.

- **Phase:** LEV-6  
- **Priority:** P2  
- **Type:** analysis_and_validation  
- **Depends on:** 13.11  
- **Primary files:** `app/services/runtime_kg/feature_flags.py`, `app/services/runtime_kg/acceptance.py`, `prometheus`, `app/services/educational_validation/drift.py`, `scripts/educational_validation/check_educational_model_drift.py`  
- **Required evidence:** Release evidence bundle.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-13.12.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-13.12.json`  

## [ ] LEV-13.13 — Require revalidation before extending the model to a new grade, subject, language or high-impact use.

- **Phase:** LEV-6  
- **Priority:** P2  
- **Type:** analysis_and_validation  
- **Depends on:** 13.12  
- **Primary files:** `app/services/runtime_kg/feature_flags.py`, `app/services/runtime_kg/acceptance.py`, `prometheus`, `app/services/educational_validation/drift.py`, `scripts/educational_validation/check_educational_model_drift.py`  
- **Required evidence:** Enforced expansion gate.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-13.13.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-13.13.json`  

## [ ] LEV-13.14 — Audit monitoring coverage, alert response and unresolved drift at least annually.

- **Phase:** LEV-6  
- **Priority:** P2  
- **Type:** operations  
- **Depends on:** 13.13  
- **Primary files:** `app/services/runtime_kg/feature_flags.py`, `app/services/runtime_kg/acceptance.py`, `prometheus`, `app/services/educational_validation/drift.py`, `scripts/educational_validation/check_educational_model_drift.py`  
- **Required evidence:** Annual operational assurance report.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-13.14.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-13.14.json`  

## [ ] LEV-13.15 — Maintain disaster-recovery procedures for telemetry loss, registry corruption and invalid model deployment.

- **Phase:** LEV-6  
- **Priority:** P2  
- **Type:** analysis_and_validation  
- **Depends on:** 13.14  
- **Primary files:** `app/services/runtime_kg/feature_flags.py`, `app/services/runtime_kg/acceptance.py`, `prometheus`, `app/services/educational_validation/drift.py`, `scripts/educational_validation/check_educational_model_drift.py`  
- **Required evidence:** Recovery runbook and rehearsal.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-13.15.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-13.15.json`  

---

# LEV-WS14 — Obtain independent approval of intended uses

**Definition of done:** An independent reviewer approves the intended uses.

**Objective:** Subject the complete validity argument, study evidence, fairness evidence, consequence evidence and operational controls to review independent of the implementation team.

**Dependencies:** Substantial completion of WS01-WS13; complete evidence package; conflict-free reviewers.

## [ ] LEV-14.01 — Define independence requirements, conflicts of interest, panel competencies and decision authority.

- **Phase:** LEV-0  
- **Priority:** P0  
- **Type:** human_governance_or_research  
- **Depends on:** 01.14, 02.16, 03.14, 04.15, 05.14, 06.15, 07.15, 08.15, 09.15, 10.16, 11.15, 12.14, 13.14  
- **Primary files:** `docs/research/mastery_model`, `docs/release-evidence`, `docs/roadmap/production_readiness/production_readiness_register.json`, `docs/research/longitudinal_validation/independent_review_dossier.md`, `docs/research/longitudinal_validation/independent_review_decision.md`  
- **Required evidence:** Independent-review charter.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-14.01.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-14.01.json`  

## [ ] LEV-14.02 — Recruit reviewers covering psychometrics, mathematics education, classroom practice, ethics/privacy, fairness and educational technology.

- **Phase:** LEV-0  
- **Priority:** P0  
- **Type:** human_governance_or_research  
- **Depends on:** 14.01  
- **Primary files:** `docs/research/mastery_model`, `docs/release-evidence`, `docs/roadmap/production_readiness/production_readiness_register.json`, `docs/research/longitudinal_validation/independent_review_dossier.md`, `docs/research/longitudinal_validation/independent_review_decision.md`  
- **Required evidence:** Panel appointments and declarations.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-14.02.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-14.02.json`  

## [ ] LEV-14.03 — Create a standard evidence dossier structure aligned to claims C1-C10 and the 15 definition-of-done conditions.

- **Phase:** LEV-3  
- **Priority:** P1  
- **Type:** governance_and_documentation  
- **Depends on:** 14.02  
- **Primary files:** `docs/research/mastery_model`, `docs/release-evidence`, `docs/roadmap/production_readiness/production_readiness_register.json`, `docs/research/longitudinal_validation/independent_review_dossier.md`, `docs/research/longitudinal_validation/independent_review_decision.md`  
- **Required evidence:** Dossier template.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-14.03.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-14.03.json`  

## [ ] LEV-14.04 — Maintain a live limitations, deviations, protocol-amendment and unresolved-finding register.

- **Phase:** LEV-3  
- **Priority:** P1  
- **Type:** governance_and_documentation  
- **Depends on:** 14.03  
- **Primary files:** `docs/research/mastery_model`, `docs/release-evidence`, `docs/roadmap/production_readiness/production_readiness_register.json`, `docs/research/longitudinal_validation/independent_review_dossier.md`, `docs/research/longitudinal_validation/independent_review_decision.md`  
- **Required evidence:** Current exceptions register.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-14.04.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-14.04.json`  

## [ ] LEV-14.05 — Freeze the review candidate: model, graph, item bank, code commit, data manifests, analyses and intended-use list.

- **Phase:** LEV-5  
- **Priority:** P2  
- **Type:** analysis_and_validation  
- **Depends on:** 14.04, 12.13, 13.10  
- **Primary files:** `docs/research/mastery_model`, `docs/release-evidence`, `docs/roadmap/production_readiness/production_readiness_register.json`, `docs/research/longitudinal_validation/independent_review_dossier.md`, `docs/research/longitudinal_validation/independent_review_decision.md`  
- **Required evidence:** Review-candidate manifest.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-14.05.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-14.05.json`  

## [ ] LEV-14.06 — Provide reproducible analysis packages, aggregated results and controlled access to necessary de-identified evidence.

- **Phase:** LEV-5  
- **Priority:** P2  
- **Type:** governance_and_documentation  
- **Depends on:** 14.05  
- **Primary files:** `docs/research/mastery_model`, `docs/release-evidence`, `docs/roadmap/production_readiness/production_readiness_register.json`, `docs/research/longitudinal_validation/independent_review_dossier.md`, `docs/research/longitudinal_validation/independent_review_decision.md`  
- **Required evidence:** Reviewer access and reproducibility evidence.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-14.06.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-14.06.json`  

## [ ] LEV-14.07 — Require reviewers to evaluate construct representation, measurement, temporal validity, impact, fairness, consequences and operations separately.

- **Phase:** LEV-5  
- **Priority:** P2  
- **Type:** analysis_and_validation  
- **Depends on:** 14.06  
- **Primary files:** `docs/research/mastery_model`, `docs/release-evidence`, `docs/roadmap/production_readiness/production_readiness_register.json`, `docs/research/longitudinal_validation/independent_review_dossier.md`, `docs/research/longitudinal_validation/independent_review_decision.md`  
- **Required evidence:** Completed structured review rubrics.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-14.07.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-14.07.json`  

## [ ] LEV-14.08 — Hold challenge sessions where reviewers can question assumptions, inspect traces and request sensitivity analyses.

- **Phase:** LEV-5  
- **Priority:** P2  
- **Type:** analysis_and_validation  
- **Depends on:** 14.07  
- **Primary files:** `docs/research/mastery_model`, `docs/release-evidence`, `docs/roadmap/production_readiness/production_readiness_register.json`, `docs/research/longitudinal_validation/independent_review_dossier.md`, `docs/research/longitudinal_validation/independent_review_decision.md`  
- **Required evidence:** Challenge-session record.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-14.08.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-14.08.json`  

## [ ] LEV-14.09 — Resolve critical findings or explicitly narrow the intended use; do not close by documentation alone.

- **Phase:** LEV-5  
- **Priority:** P2  
- **Type:** governance_and_documentation  
- **Depends on:** 14.08  
- **Primary files:** `docs/research/mastery_model`, `docs/release-evidence`, `docs/roadmap/production_readiness/production_readiness_register.json`, `docs/research/longitudinal_validation/independent_review_dossier.md`, `docs/research/longitudinal_validation/independent_review_decision.md`  
- **Required evidence:** Finding-resolution evidence.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-14.09.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-14.09.json`  

## [ ] LEV-14.10 — Obtain one of four decisions: approved, approved with restrictions, further evidence required or rejected.

- **Phase:** LEV-5  
- **Priority:** P2  
- **Type:** governance_and_documentation  
- **Depends on:** 14.09  
- **Primary files:** `docs/research/mastery_model`, `docs/release-evidence`, `docs/roadmap/production_readiness/production_readiness_register.json`, `docs/research/longitudinal_validation/independent_review_dossier.md`, `docs/research/longitudinal_validation/independent_review_decision.md`  
- **Required evidence:** Signed decision record.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-14.10.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-14.10.json`  

## [ ] LEV-14.11 — Translate restrictions into enforceable feature flags, product wording, population limits and expiry dates.

- **Phase:** LEV-5  
- **Priority:** P2  
- **Type:** governance_and_documentation  
- **Depends on:** 14.10  
- **Primary files:** `docs/research/mastery_model`, `docs/release-evidence`, `docs/roadmap/production_readiness/production_readiness_register.json`, `docs/research/longitudinal_validation/independent_review_dossier.md`, `docs/research/longitudinal_validation/independent_review_decision.md`  
- **Required evidence:** Restriction implementation verification.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-14.11.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-14.11.json`  

## [ ] LEV-14.12 — Publish an internal validation summary and an appropriate external transparency statement.

- **Phase:** LEV-5  
- **Priority:** P2  
- **Type:** governance_and_documentation  
- **Depends on:** 14.11  
- **Primary files:** `docs/research/mastery_model`, `docs/release-evidence`, `docs/roadmap/production_readiness/production_readiness_register.json`, `docs/research/longitudinal_validation/independent_review_dossier.md`, `docs/research/longitudinal_validation/independent_review_decision.md`  
- **Required evidence:** Approved communications.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-14.12.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-14.12.json`  

## [ ] LEV-14.13 — Schedule renewal review and define events requiring early re-review.

- **Phase:** LEV-6  
- **Priority:** P2  
- **Type:** operations  
- **Depends on:** 14.12  
- **Primary files:** `docs/research/mastery_model`, `docs/release-evidence`, `docs/roadmap/production_readiness/production_readiness_register.json`, `docs/research/longitudinal_validation/independent_review_dossier.md`, `docs/research/longitudinal_validation/independent_review_decision.md`  
- **Required evidence:** Review renewal policy.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-14.13.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-14.13.json`  

## [ ] LEV-14.14 — Preserve reviewer independence for future model families and material changes.

- **Phase:** LEV-6  
- **Priority:** P2  
- **Type:** human_governance_or_research  
- **Depends on:** 14.13  
- **Primary files:** `docs/research/mastery_model`, `docs/release-evidence`, `docs/roadmap/production_readiness/production_readiness_register.json`, `docs/research/longitudinal_validation/independent_review_dossier.md`, `docs/research/longitudinal_validation/independent_review_decision.md`  
- **Required evidence:** Governance audit evidence.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-14.14.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-14.14.json`  

---

# LEV-WS15 — Document unsupported uses and residual limitations

**Definition of done:** EduBoost clearly documents which uses remain unsupported.

**Objective:** Prevent valid evidence for one context or use from being overstated as universal support, and make every residual limitation operationally visible and enforceable.

**Dependencies:** Outputs and decisions from all prior workstreams; product and release governance.

## [ ] LEV-15.01 — Create a limitations taxonomy covering construct, population, content, time horizon, language, delivery context, model, data and consequence limitations.

- **Phase:** LEV-0  
- **Priority:** P0  
- **Type:** analysis_and_validation  
- **Depends on:** 01.08  
- **Primary files:** `app/services/runtime_kg/feature_flags.py`, `app/services/runtime_kg/schemas.py`, `docs/learning_science/mastery_model.md`, `docs/research/longitudinal_validation/unsupported_use_register.json`, `app/services/educational_validation/use_authorization.py`  
- **Required evidence:** Limitations taxonomy.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-15.01.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-15.01.json`  

## [ ] LEV-15.02 — Create an unsupported-use register linked to mastery claims, model versions, grades, subjects, populations and decisions.

- **Phase:** LEV-0  
- **Priority:** P0  
- **Type:** analysis_and_validation  
- **Depends on:** 15.01  
- **Primary files:** `app/services/runtime_kg/feature_flags.py`, `app/services/runtime_kg/schemas.py`, `docs/learning_science/mastery_model.md`, `docs/research/longitudinal_validation/unsupported_use_register.json`, `app/services/educational_validation/use_authorization.py`  
- **Required evidence:** Machine-readable unsupported-use register.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-15.02.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-15.02.json`  

## [ ] LEV-15.03 — Map each unsupported use to the missing evidence, known risk and evidence needed for future authorisation.

- **Phase:** LEV-0  
- **Priority:** P0  
- **Type:** governance_and_documentation  
- **Depends on:** 15.02  
- **Primary files:** `app/services/runtime_kg/feature_flags.py`, `app/services/runtime_kg/schemas.py`, `docs/learning_science/mastery_model.md`, `docs/research/longitudinal_validation/unsupported_use_register.json`, `app/services/educational_validation/use_authorization.py`  
- **Required evidence:** Evidence-gap matrix.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-15.03.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-15.03.json`  

## [ ] LEV-15.04 — Define mandatory wording for internal documents, API descriptions, dashboards, reports, marketing and school agreements.

- **Phase:** LEV-0  
- **Priority:** P0  
- **Type:** human_governance_or_research  
- **Depends on:** 15.03  
- **Primary files:** `app/services/runtime_kg/feature_flags.py`, `app/services/runtime_kg/schemas.py`, `docs/learning_science/mastery_model.md`, `docs/research/longitudinal_validation/unsupported_use_register.json`, `app/services/educational_validation/use_authorization.py`  
- **Required evidence:** Claims and wording standard.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-15.04.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-15.04.json`  

## [ ] LEV-15.05 — Expose validation status, authorised population, expiry and limitation codes in the model registry and internal APIs.

- **Phase:** LEV-1  
- **Priority:** P0  
- **Type:** analysis_and_validation  
- **Depends on:** 15.04  
- **Primary files:** `app/services/runtime_kg/feature_flags.py`, `app/services/runtime_kg/schemas.py`, `docs/learning_science/mastery_model.md`, `docs/research/longitudinal_validation/unsupported_use_register.json`, `app/services/educational_validation/use_authorization.py`  
- **Required evidence:** Registry and API contract tests.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-15.05.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-15.05.json`  

## [ ] LEV-15.06 — Implement feature flags and policy checks preventing unsupported high-impact uses.

- **Phase:** LEV-1  
- **Priority:** P0  
- **Type:** engineering  
- **Depends on:** 15.05  
- **Primary files:** `app/services/runtime_kg/feature_flags.py`, `app/services/runtime_kg/schemas.py`, `docs/learning_science/mastery_model.md`, `docs/research/longitudinal_validation/unsupported_use_register.json`, `app/services/educational_validation/use_authorization.py`  
- **Required evidence:** Enforcement tests pass.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-15.06.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-15.06.json`  

## [ ] LEV-15.07 — Add teacher- and administrator-facing explanations when a projection has insufficient evidence, stale evidence or unsupported context.

- **Phase:** LEV-2  
- **Priority:** P1  
- **Type:** human_governance_or_research  
- **Depends on:** 15.06  
- **Primary files:** `app/services/runtime_kg/feature_flags.py`, `app/services/runtime_kg/schemas.py`, `docs/learning_science/mastery_model.md`, `docs/research/longitudinal_validation/unsupported_use_register.json`, `app/services/educational_validation/use_authorization.py`  
- **Required evidence:** Product usability review.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-15.07.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-15.07.json`  

## [ ] LEV-15.08 — Add developer documentation describing where mastery values may and may not be consumed.

- **Phase:** LEV-2  
- **Priority:** P1  
- **Type:** engineering  
- **Depends on:** 15.07  
- **Primary files:** `app/services/runtime_kg/feature_flags.py`, `app/services/runtime_kg/schemas.py`, `docs/learning_science/mastery_model.md`, `docs/research/longitudinal_validation/unsupported_use_register.json`, `app/services/educational_validation/use_authorization.py`  
- **Required evidence:** Developer reference updated.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-15.08.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-15.08.json`  

## [ ] LEV-15.09 — Review all generated reports and analytics for misleading certainty or unsupported aggregation.

- **Phase:** LEV-3  
- **Priority:** P1  
- **Type:** governance_and_documentation  
- **Depends on:** 15.08  
- **Primary files:** `app/services/runtime_kg/feature_flags.py`, `app/services/runtime_kg/schemas.py`, `docs/learning_science/mastery_model.md`, `docs/research/longitudinal_validation/unsupported_use_register.json`, `app/services/educational_validation/use_authorization.py`  
- **Required evidence:** Report language audit.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-15.09.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-15.09.json`  

## [ ] LEV-15.10 — Review contractual, privacy and consent materials to ensure research and operational uses are accurately distinguished.

- **Phase:** LEV-3  
- **Priority:** P1  
- **Type:** human_governance_or_research  
- **Depends on:** 15.09  
- **Primary files:** `app/services/runtime_kg/feature_flags.py`, `app/services/runtime_kg/schemas.py`, `docs/learning_science/mastery_model.md`, `docs/research/longitudinal_validation/unsupported_use_register.json`, `app/services/educational_validation/use_authorization.py`  
- **Required evidence:** Legal/privacy consistency review.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-15.10.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-15.10.json`  

## [ ] LEV-15.11 — Update limitations based on impact-study findings, subgroup results and adverse-consequence evidence.

- **Phase:** LEV-4  
- **Priority:** P2  
- **Type:** governance_and_documentation  
- **Depends on:** 15.10  
- **Primary files:** `app/services/runtime_kg/feature_flags.py`, `app/services/runtime_kg/schemas.py`, `docs/learning_science/mastery_model.md`, `docs/research/longitudinal_validation/unsupported_use_register.json`, `app/services/educational_validation/use_authorization.py`  
- **Required evidence:** Post-study limitations revision.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-15.11.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-15.11.json`  

## [ ] LEV-15.12 — Update authorised and unsupported uses after replication and independent review.

- **Phase:** LEV-5  
- **Priority:** P2  
- **Type:** human_governance_or_research  
- **Depends on:** 15.11, 12.13, 14.10  
- **Primary files:** `app/services/runtime_kg/feature_flags.py`, `app/services/runtime_kg/schemas.py`, `docs/learning_science/mastery_model.md`, `docs/research/longitudinal_validation/unsupported_use_register.json`, `app/services/educational_validation/use_authorization.py`  
- **Required evidence:** Final use-status register.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-15.12.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-15.12.json`  

## [ ] LEV-15.13 — Add CI or release-gate checks requiring current limitation records for every promoted model.

- **Phase:** LEV-6  
- **Priority:** P2  
- **Type:** analysis_and_validation  
- **Depends on:** 15.12, 13.12  
- **Primary files:** `app/services/runtime_kg/feature_flags.py`, `app/services/runtime_kg/schemas.py`, `docs/learning_science/mastery_model.md`, `docs/research/longitudinal_validation/unsupported_use_register.json`, `app/services/educational_validation/use_authorization.py`  
- **Required evidence:** Release control operational.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-15.13.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-15.13.json`  

## [ ] LEV-15.14 — Establish a public correction process for inaccurate claims and an internal incident process for unsupported use.

- **Phase:** LEV-6  
- **Priority:** P2  
- **Type:** operations  
- **Depends on:** 15.13  
- **Primary files:** `app/services/runtime_kg/feature_flags.py`, `app/services/runtime_kg/schemas.py`, `docs/learning_science/mastery_model.md`, `docs/research/longitudinal_validation/unsupported_use_register.json`, `app/services/educational_validation/use_authorization.py`  
- **Required evidence:** Correction and incident runbooks.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-15.14.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-15.14.json`  

## [ ] LEV-15.15 — Review limitations at least quarterly and after every material model, graph, item-bank or policy change.

- **Phase:** LEV-6  
- **Priority:** P2  
- **Type:** analysis_and_validation  
- **Depends on:** 15.14  
- **Primary files:** `app/services/runtime_kg/feature_flags.py`, `app/services/runtime_kg/schemas.py`, `docs/learning_science/mastery_model.md`, `docs/research/longitudinal_validation/unsupported_use_register.json`, `app/services/educational_validation/use_authorization.py`  
- **Required evidence:** Review records and no expired limitation entries.  
- **Task card:** `docs/roadmap/production_readiness/lev/tasks/LEV-15.15.md`  
- **Evidence record:** `docs/roadmap/production_readiness/lev/evidence/LEV-15.15.json`  

---
