# LEV-WS01 — Define mastery claims precisely

**Definition of done:** Mastery claims are precisely defined.

**Objective:** Establish an authoritative, testable and uncertainty-qualified definition of every learner-state projection and every permitted use of the term mastery.

**Dependencies:** LEV-0 authority; curriculum scope; intended product uses; legal and ethical review.

**Accountability:** Educational Measurement Lead (A); Mathematics Curriculum Lead, Product Lead, Runtime KG Lead, Privacy Lead (R/C).

**Indicative duration:** 6-8 weeks

## Repository implementation boundary

- `EXISTING: app/modules/progress/mastery_model.py`
- `EXISTING: app/services/runtime_kg/schemas.py`
- `EXISTING: app/services/runtime_kg/feature_flags.py`
- `EXISTING: app/services/runtime_kg/acceptance.py`
- `EXISTING: app/repositories/mastery_repository.py`
- `EXISTING: docs/learning_science/mastery_model.md`
- `EXISTING: docs/diagnostics/mastery_model_assessment_contract.md`
- `EXISTING: docs/research/mastery_model/rr013_mastery_model_research_policy.md`
- `NEW: docs/research/longitudinal_validation/mastery_interpretation_and_use_specification.md`
- `NEW: app/domain/educational_validation_schemas.py`

## Task execution order

1. [LEV-01.01](../tasks/LEV-01.01.md) — Create a mastery-construct working group with psychometric, mathematics-education, teacher, product, data-science, privacy and runtime-KG representation.
1. [LEV-01.02](../tasks/LEV-01.02.md) — Inventory every current mastery-related field, API response, dashboard label, recommendation rule, report statement and production-readiness claim.
1. [LEV-01.03](../tasks/LEV-01.03.md) — Separate the constructs of next-response probability, current independent proficiency, provisional mastery, durable mastery, retention and transfer.
1. [LEV-01.04](../tasks/LEV-01.04.md) — Define the unit of inference for each construct: item, skill, CAPS topic, KG concept, prerequisite cluster, strand and grade-level outcome.
1. [LEV-01.05](../tasks/LEV-01.05.md) — Define the evidence conditions for each state, including minimum observations, independent items, assistance limits, recency and contradiction handling.
1. [LEV-01.06](../tasks/LEV-01.06.md) — Define required uncertainty outputs, confidence or credible intervals, evidence sufficiency indicators and stale-evidence behaviour.
1. [LEV-01.07](../tasks/LEV-01.07.md) — Define permitted instructional uses, teacher-facing uses, learner-facing wording, parent-facing wording and research-only uses.
1. [LEV-01.08](../tasks/LEV-01.08.md) — Define prohibited uses, including high-stakes progression, formal marks, permanent labels and unsupported population extrapolation.
1. [LEV-01.09](../tasks/LEV-01.09.md) — Write a validity-argument map linking each intended interpretation to evidence claims C1-C10 and required study outputs.
1. [LEV-01.10](../tasks/LEV-01.10.md) — Define mastery-state names and machine-readable enums, including insufficient evidence, emerging, provisional, retention unverified, durable, transfer demonstrated, stale and human review required.
1. [LEV-01.11](../tasks/LEV-01.11.md) — Create age-appropriate explanations for learners and plain-language explanations for teachers and guardians.
1. [LEV-01.12](../tasks/LEV-01.12.md) — Create a claims-change-control process requiring impact assessment whenever definitions, thresholds, graph structure or decision authority change.
1. [LEV-01.13](../tasks/LEV-01.13.md) — Add automated documentation and API contract checks preventing unapproved mastery terminology from entering production surfaces.
1. [LEV-01.14](../tasks/LEV-01.14.md) — Approve and version the Mastery Interpretation and Use Specification.

## Closure rule

The workstream may close only when every task is closed or independently waived and the following condition is supported: **Mastery claims are precisely defined.**
