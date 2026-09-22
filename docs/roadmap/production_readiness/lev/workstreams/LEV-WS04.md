# LEV-WS04 — Calibrate mastery estimates against independent outcomes

**Definition of done:** Mastery estimates are calibrated against independent outcomes.

**Objective:** Show that predicted mastery probabilities correspond to observed success on independent, CAPS-aligned assessments not used to drive the learner's adaptive experience.

**Dependencies:** WS02 validation bank; WS03 traceability; prospective cohort; statistical analysis plan.

**Accountability:** Psychometric Lead (A); Data Science Lead, Research Lead, Assessment Operations Lead (R).

**Indicative duration:** Pilot plus 9-12 months of cohort evidence

## Repository implementation boundary

- `EXISTING: app/modules/diagnostics/irt_engine.py`
- `EXISTING: app/modules/diagnostics/calibration_service.py`
- `EXISTING: app/repositories/irt_repository.py`
- `EXISTING: app/services/diagnostic_scoring_snapshot.py`
- `EXISTING: docs/research/mastery_model/rr013_evaluation_protocol.md`
- `NEW: app/services/educational_validation/calibration.py`
- `NEW: scripts/educational_validation/run_calibration_analysis.py`

## Task execution order

1. [LEV-04.01](../tasks/LEV-04.01.md) — Pre-specify calibration estimands, time horizons, outcome definitions, minimum sample sizes and acceptable uncertainty.
1. [LEV-04.02](../tasks/LEV-04.02.md) — Define independence rules preventing validation items, labels or later outcomes from leaking into training or adaptation.
1. [LEV-04.03](../tasks/LEV-04.03.md) — Build baseline, term and concept-level independent assessment administrations with standardised conditions.
1. [LEV-04.04](../tasks/LEV-04.04.md) — Collect shadow-mode predictions before independent outcomes are observed.
1. [LEV-04.05](../tasks/LEV-04.05.md) — Assess data completeness, representativeness, missingness and outcome quality before modelling.
1. [LEV-04.06](../tasks/LEV-04.06.md) — Compare the production model with simple baselines such as last response, rolling accuracy, IRT-only and non-temporal models.
1. [LEV-04.07](../tasks/LEV-04.07.md) — Estimate calibration intercept, calibration slope, reliability curves, Brier score, log loss and uncertainty by concept.
1. [LEV-04.08](../tasks/LEV-04.08.md) — Evaluate discrimination and ranking metrics without treating them as substitutes for calibration.
1. [LEV-04.09](../tasks/LEV-04.09.md) — Evaluate calibration by evidence count, item exposure, time since evidence, assistance level and concept difficulty.
1. [LEV-04.10](../tasks/LEV-04.10.md) — Evaluate calibration on unseen learners, unseen items and later time windows.
1. [LEV-04.11](../tasks/LEV-04.11.md) — Evaluate subgroup calibration and differential prediction for approved contexts.
1. [LEV-04.12](../tasks/LEV-04.12.md) — Develop and test recalibration methods without altering the underlying construct definition.
1. [LEV-04.13](../tasks/LEV-04.13.md) — Set model release thresholds, uncertainty displays and fallback behaviour when calibration fails.
1. [LEV-04.14](../tasks/LEV-04.14.md) — Obtain independent psychometric review of the calibration evidence and limitations.
1. [LEV-04.15](../tasks/LEV-04.15.md) — Automate recurring calibration monitoring against later independent outcomes.

## Closure rule

The workstream may close only when every task is closed or independently waived and the following condition is supported: **Mastery estimates are calibrated against independent outcomes.**
