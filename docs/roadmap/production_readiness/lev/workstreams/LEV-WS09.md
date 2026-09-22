# LEV-WS09 — Establish validity across relevant learner contexts

**Definition of done:** Results remain valid across relevant learner contexts.

**Objective:** Determine where the model is sufficiently valid across language, school, device, connectivity, attainment and support contexts, and constrain use outside supported contexts.

**Dependencies:** Lawful context data; adequate samples; WS04-WS08 metrics; fairness governance.

**Accountability:** Fairness and Inclusion Lead (A); Privacy Lead, Psychometric Lead, Research Lead, Accessibility Lead (R/C).

**Indicative duration:** Runs throughout LEV-2 to LEV-5

## Repository implementation boundary

- `EXISTING: docs/diagnostics/assessment_quality_fairness_contract.md`
- `EXISTING: app/modules/diagnostics/bias_review_router.py`
- `EXISTING: app/modules/diagnostics/quality_scorer.py`
- `EXISTING: app/services/runtime_kg/feature_flags.py`
- `EXISTING: docs/compliance`
- `NEW: app/services/educational_validation/fairness.py`
- `NEW: scripts/educational_validation/run_fairness_analysis.py`

## Task execution order

1. [LEV-09.01](../tasks/LEV-09.01.md) — Define the intended learner population and every context dimension material to the model's use.
1. [LEV-09.02](../tasks/LEV-09.02.md) — Determine which context variables may lawfully and ethically be collected, for what purpose and for how long.
1. [LEV-09.03](../tasks/LEV-09.03.md) — Define minimum subgroup sample requirements and rules for suppressing unstable estimates.
1. [LEV-09.04](../tasks/LEV-09.04.md) — Design recruitment to include varied school contexts, baseline attainment, language, device and connectivity conditions.
1. [LEV-09.05](../tasks/LEV-09.05.md) — Implement accessibility and accommodation metadata without conflating support with ability.
1. [LEV-09.06](../tasks/LEV-09.06.md) — Measure representation, missingness, data quality and platform exposure by context.
1. [LEV-09.07](../tasks/LEV-09.07.md) — Test differential item functioning and differential test functioning where estimable.
1. [LEV-09.08](../tasks/LEV-09.08.md) — Test subgroup calibration, discrimination, false mastery, false non-mastery, retention and transfer.
1. [LEV-09.09](../tasks/LEV-09.09.md) — Analyse interaction effects for device, connectivity, language and opportunity to learn.
1. [LEV-09.10](../tasks/LEV-09.10.md) — Conduct qualitative investigation with teachers and learners where quantitative differences appear.
1. [LEV-09.11](../tasks/LEV-09.11.md) — Identify unsupported or weakly supported contexts and impose conservative product behaviour.
1. [LEV-09.12](../tasks/LEV-09.12.md) — Remediate item, interface, content, model or access causes and re-test affected groups.
1. [LEV-09.13](../tasks/LEV-09.13.md) — Pre-register impact-study subgroup analyses and harm boundaries.
1. [LEV-09.14](../tasks/LEV-09.14.md) — Confirm generalisability in an additional school, region, language or delivery context where feasible.
1. [LEV-09.15](../tasks/LEV-09.15.md) — Monitor context mix and automatically flag population shift beyond the authorised envelope.

## Closure rule

The workstream may close only when every task is closed or independently waived and the following condition is supported: **Results remain valid across relevant learner contexts.**
