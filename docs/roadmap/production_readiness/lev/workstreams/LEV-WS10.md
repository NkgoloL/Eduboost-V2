# LEV-WS10 — Demonstrate that mastery-informed recommendations improve learning

**Definition of done:** Recommendations improve independent learning outcomes.

**Objective:** Establish through a controlled study that decisions based on the learner-state model produce better independent educational outcomes than an appropriate comparison condition.

**Dependencies:** Provisional completion of WS01-WS09; intervention stability; school partnerships; independent outcomes.

**Accountability:** Independent Research Lead (A); Product Lead, Curriculum Lead, Psychometric Lead, School Operations Lead (R/C).

**Indicative duration:** One academic year plus analysis

## Repository implementation boundary

- `EXISTING: app/modules/study_plans/runtime_kg_planner.py`
- `EXISTING: app/modules/lessons/adaptive_remediation.py`
- `EXISTING: app/services/study_plan_service_v2.py`
- `EXISTING: app/services/lesson_service_v2.py`
- `EXISTING: tests/e2e/study_plan_and_lesson.spec.ts`
- `NEW: docs/research/longitudinal_validation/impact_study_protocol.md`
- `NEW: scripts/educational_validation/run_impact_analysis.py`

## Task execution order

1. [LEV-10.01](../tasks/LEV-10.01.md) — Define the intervention precisely: which recommendations use the KG, when, for whom and with what teacher authority.
1. [LEV-10.02](../tasks/LEV-10.02.md) — Select the comparison condition, such as non-adaptive CAPS sequence or appropriate business-as-usual provision.
1. [LEV-10.03](../tasks/LEV-10.03.md) — Choose the experimental design, preferably cluster randomisation where feasible, and pre-specify the estimand.
1. [LEV-10.04](../tasks/LEV-10.04.md) — Perform statistical power and precision calculations accounting for clustering, expected attrition and multiple outcomes.
1. [LEV-10.05](../tasks/LEV-10.05.md) — Pre-register primary and secondary outcomes, subgroup analyses, mediation analyses and harm boundaries.
1. [LEV-10.06](../tasks/LEV-10.06.md) — Obtain ethics, privacy, school, guardian and learner approvals and establish complaint and withdrawal procedures.
1. [LEV-10.07](../tasks/LEV-10.07.md) — Build randomisation, allocation concealment, contamination tracking and study-condition enforcement.
1. [LEV-10.08](../tasks/LEV-10.08.md) — Create independent baseline and outcome assessments and assessor procedures.
1. [LEV-10.09](../tasks/LEV-10.09.md) — Recruit schools/classes, establish baseline equivalence and document the participant flow.
1. [LEV-10.10](../tasks/LEV-10.10.md) — Deliver the intervention while measuring fidelity, actual exposure, teacher use and cross-condition contamination.
1. [LEV-10.11](../tasks/LEV-10.11.md) — Measure independent achievement, retention, transfer, time to durable mastery and opportunity to learn.
1. [LEV-10.12](../tasks/LEV-10.12.md) — Conduct intention-to-treat analysis with clustering, missing-data and attrition handling.
1. [LEV-10.13](../tasks/LEV-10.13.md) — Conduct pre-specified per-protocol, exposure, mediation, sensitivity and subgroup analyses without replacing the primary result.
1. [LEV-10.14](../tasks/LEV-10.14.md) — Determine whether any benefit is explained only by additional time on task or narrower content exposure.
1. [LEV-10.15](../tasks/LEV-10.15.md) — Obtain independent methodological review and produce a transparent limitations statement.
1. [LEV-10.16](../tasks/LEV-10.16.md) — Repeat or extend the impact test before broad educational-effectiveness claims.

## Closure rule

The workstream may close only when every task is closed or independently waived and the following condition is supported: **Recommendations improve independent learning outcomes.**
