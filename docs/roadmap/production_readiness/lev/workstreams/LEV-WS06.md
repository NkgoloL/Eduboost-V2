# LEV-WS06 — Demonstrate delayed-retention validity

**Definition of done:** Estimates predict delayed retention.

**Objective:** Show that mastery projections distinguish temporary success from knowledge retained after meaningful delays and reduced practice support.

**Dependencies:** WS02 parallel forms; WS03 timestamps; WS04 calibration; cohort follow-up.

**Accountability:** Research Lead (A); Psychometric Lead, Curriculum Lead, School Operations Lead (R).

**Indicative duration:** 12-18 months

## Repository implementation boundary

- `EXISTING: app/modules/progress/mastery_model.py`
- `EXISTING: app/services/runtime_kg/service.py`
- `EXISTING: app/modules/study_plans/runtime_kg_planner.py`
- `EXISTING: app/services/study_plan_service_v2.py`
- `EXISTING: docs/learning_science/mastery_model.md`
- `NEW: app/services/educational_validation/retention.py`
- `NEW: scripts/educational_validation/run_retention_analysis.py`

## Task execution order

1. [LEV-06.01](../tasks/LEV-06.01.md) — Define retention horizons relevant to Grade 4 instruction, provisionally including 2-4 weeks, 8-12 weeks, end of term and cross-year follow-up.
1. [LEV-06.02](../tasks/LEV-06.02.md) — Create independent retention probes with parallel items and controlled overlap with instruction.
1. [LEV-06.03](../tasks/LEV-06.03.md) — Define when a mastery declaration becomes eligible for a retention probe and how re-practice affects interpretation.
1. [LEV-06.04](../tasks/LEV-06.04.md) — Instrument exposure history, spacing, cumulative review and intervening instruction.
1. [LEV-06.05](../tasks/LEV-06.05.md) — Schedule and administer short-, medium- and long-delay assessments using standardised procedures.
1. [LEV-06.06](../tasks/LEV-06.06.md) — Model retention probability as a function of mastery estimate, uncertainty, evidence history and elapsed time.
1. [LEV-06.07](../tasks/LEV-06.07.md) — Compare predictive value of mastery estimates with immediate correctness alone and other baselines.
1. [LEV-06.08](../tasks/LEV-06.08.md) — Estimate forgetting curves by concept and learner context, with appropriate multilevel uncertainty.
1. [LEV-06.09](../tasks/LEV-06.09.md) — Test whether assisted success and repeated exposure produce weaker retention than independent success.
1. [LEV-06.10](../tasks/LEV-06.10.md) — Evaluate whether uncertainty and staleness indicators correctly identify retention risk.
1. [LEV-06.11](../tasks/LEV-06.11.md) — Identify concept-specific retention thresholds and review schedules where justified.
1. [LEV-06.12](../tasks/LEV-06.12.md) — Update the runtime KG state model to represent retention unverified, retained, stale and contradictory evidence states.
1. [LEV-06.13](../tasks/LEV-06.13.md) — Test whether retention-aware review scheduling improves later independent outcomes.
1. [LEV-06.14](../tasks/LEV-06.14.md) — Repeat retention analyses in a later cohort or academic year.
1. [LEV-06.15](../tasks/LEV-06.15.md) — Monitor retention failure and recalibrate forgetting assumptions over time.

## Closure rule

The workstream may close only when every task is closed or independently waived and the following condition is supported: **Estimates predict delayed retention.**
