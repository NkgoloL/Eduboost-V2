# LEV-WS05 — Quantify false-mastery and false-non-mastery risk

**Definition of done:** False-mastery and false-non-mastery rates are understood.

**Objective:** Measure classification error at every operational threshold, identify its causes and control the asymmetric educational risks of over- and under-estimating mastery.

**Dependencies:** WS01 thresholds; WS04 calibrated probabilities; delayed independent probes.

**Accountability:** Educational Measurement Lead (A); Data Science Lead, Curriculum Lead, Teacher Advisory Panel (R/C).

**Indicative duration:** Runs with LEV-2 and LEV-3

## Repository implementation boundary

- `EXISTING: app/modules/progress/mastery_model.py`
- `EXISTING: app/modules/diagnostics/irt_engine.py`
- `EXISTING: app/services/runtime_kg/schemas.py`
- `EXISTING: docs/diagnostics/mastery_model_assessment_contract.md`
- `NEW: app/services/educational_validation/classification.py`
- `NEW: scripts/educational_validation/run_classification_analysis.py`

## Task execution order

1. [LEV-05.01](../tasks/LEV-05.01.md) — Define false mastery and false non-mastery for immediate, delayed and transfer outcomes.
1. [LEV-05.02](../tasks/LEV-05.02.md) — Document the educational cost of each error type for each intended decision.
1. [LEV-05.03](../tasks/LEV-05.03.md) — Set provisional safety ceilings and harm boundaries, subject to later evidence and independent approval.
1. [LEV-05.04](../tasks/LEV-05.04.md) — Construct confusion matrices for each candidate mastery threshold and outcome horizon.
1. [LEV-05.05](../tasks/LEV-05.05.md) — Estimate sensitivity, specificity, predictive values, false discovery rate and false omission rate with uncertainty.
1. [LEV-05.06](../tasks/LEV-05.06.md) — Estimate error by concept, difficulty, evidence count, hint use, response latency and time since learning.
1. [LEV-05.07](../tasks/LEV-05.07.md) — Investigate repeated-item exposure, guessing, copying, disengagement and assistance as causes of false mastery.
1. [LEV-05.08](../tasks/LEV-05.08.md) — Investigate language load, poor item fit, missing opportunity to learn and interface problems as causes of false non-mastery.
1. [LEV-05.09](../tasks/LEV-05.09.md) — Compare threshold policies: global, concept-specific, uncertainty-aware and cost-sensitive.
1. [LEV-05.10](../tasks/LEV-05.10.md) — Introduce human-review and conservative fallback states for high-uncertainty classifications.
1. [LEV-05.11](../tasks/LEV-05.11.md) — Evaluate error rates across approved learner contexts and identify unacceptable disparities.
1. [LEV-05.12](../tasks/LEV-05.12.md) — Run teacher adjudication studies on sampled disagreements between the model and independent outcomes.
1. [LEV-05.13](../tasks/LEV-05.13.md) — Select and approve operational thresholds for each authorised use rather than one universal threshold.
1. [LEV-05.14](../tasks/LEV-05.14.md) — Monitor error rates continuously and automatically reduce decision authority when ceilings are exceeded.

## Closure rule

The workstream may close only when every task is closed or independently waived and the following condition is supported: **False-mastery and false-non-mastery rates are understood.**
