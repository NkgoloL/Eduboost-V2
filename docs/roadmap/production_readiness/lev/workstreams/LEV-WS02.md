# LEV-WS02 — Independently review CAPS concepts and assessment items

**Definition of done:** CAPS concepts and items are independently reviewed.

**Objective:** Demonstrate that the knowledge graph, content mappings and validation instruments represent the intended Grade 4 Mathematics CAPS domain with adequate breadth, cognitive demand and fairness.

**Dependencies:** WS01 construct definitions; canonical CAPS corpus; item-bank governance; independent reviewers.

**Accountability:** Mathematics Curriculum Lead (A); Independent Curriculum Review Panel, Psychometric Lead, Content Governance Lead (R).

**Indicative duration:** 4-6 months, followed by recurring review

## Repository implementation boundary

- `EXISTING: app/modules/diagnostics/item_bank_pipeline.py`
- `EXISTING: app/modules/diagnostics/item_bank_service.py`
- `EXISTING: app/repositories/item_bank_repository.py`
- `EXISTING: app/services/curriculum/claim_validation.py`
- `EXISTING: docs/architecture/diagnostic_item_bank_canonicality.yml`
- `EXISTING: docs/diagnostics/assessment_quality_fairness_contract.md`
- `EXISTING: scripts/curriculum/build_launch_item_bank.py`
- `EXISTING: scripts/validate_item_bank.py`
- `NEW: docs/research/longitudinal_validation/caps_validation_blueprint.csv`
- `NEW: docs/research/longitudinal_validation/validation_item_bank_manifest.json`

## Task execution order

1. [LEV-02.01](../tasks/LEV-02.01.md) — Freeze and hash the canonical CAPS source corpus, extraction outputs, graph version and curriculum mapping rules used for validation.
1. [LEV-02.02](../tasks/LEV-02.02.md) — Create a CAPS coverage blueprint by strand, topic, subtopic, concept, cognitive demand, representation and expected instructional period.
1. [LEV-02.03](../tasks/LEV-02.03.md) — Map every KG concept to source pages, CAPS statements, prerequisite relationships, examples and assessment evidence requirements.
1. [LEV-02.04](../tasks/LEV-02.04.md) — Recruit independent Grade 4 mathematics teachers, curriculum specialists and a psychometric reviewer who did not author the mappings.
1. [LEV-02.05](../tasks/LEV-02.05.md) — Conduct independent concept-level review for correctness, granularity, prerequisite logic, terminology and grade appropriateness.
1. [LEV-02.06](../tasks/LEV-02.06.md) — Conduct graph-level review for missing concepts, duplicated concepts, circular prerequisites, overly broad nodes and invalid dependency paths.
1. [LEV-02.07](../tasks/LEV-02.07.md) — Create an operational learning-item bank and a separately protected validation-item bank.
1. [LEV-02.08](../tasks/LEV-02.08.md) — Tag every validation item with concept IDs, CAPS provenance, cognitive process, difficulty hypothesis, language load, representation, scoring rubric and misconception tags.
1. [LEV-02.09](../tasks/LEV-02.09.md) — Perform independent content, language, accessibility, cultural-context and bias review of each validation item.
1. [LEV-02.10](../tasks/LEV-02.10.md) — Run cognitive interviews or structured response-process sessions with a diverse pilot subsample.
1. [LEV-02.11](../tasks/LEV-02.11.md) — Pilot items and estimate difficulty, discrimination, information, local dependence, dimensionality and abnormal response patterns.
1. [LEV-02.12](../tasks/LEV-02.12.md) — Test differential item functioning across approved comparison groups where sample sizes and lawful data collection permit.
1. [LEV-02.13](../tasks/LEV-02.13.md) — Build parallel forms, common anchor sets and controlled exposure schedules for baseline, term, retention and transfer assessments.
1. [LEV-02.14](../tasks/LEV-02.14.md) — Set approval, expiry, drift-review and retirement rules for concepts and items.
1. [LEV-02.15](../tasks/LEV-02.15.md) — Obtain independent sign-off that the validation bank adequately represents the intended claims.
1. [LEV-02.16](../tasks/LEV-02.16.md) — Schedule annual CAPS, graph and item-bank re-review and event-triggered review after material changes.

## Closure rule

The workstream may close only when every task is closed or independently waived and the following condition is supported: **CAPS concepts and items are independently reviewed.**
