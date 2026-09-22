# LEV-WS08 — Validate educational plausibility of state transitions

**Definition of done:** State transitions are educationally plausible.

**Objective:** Demonstrate that mastery changes follow defensible learning, prerequisite, assistance, contradiction and forgetting logic rather than opaque predictive shortcuts.

**Dependencies:** WS01 state definitions; WS03 transition ledger; teacher and expert review.

**Accountability:** Runtime KG Lead and Educational Measurement Lead (joint A); Data Science, Curriculum and Teacher Panel (R/C).

**Indicative duration:** 4-8 months, then continuous

## Repository implementation boundary

- `EXISTING: app/modules/progress/mastery_model.py`
- `EXISTING: app/services/runtime_kg/integration.py`
- `EXISTING: app/services/runtime_kg/service.py`
- `EXISTING: app/services/runtime_kg/route_integration.py`
- `EXISTING: tests/unit/runtime_kg`
- `NEW: app/services/educational_validation/state_reasonableness.py`
- `NEW: tests/unit/educational_validation/test_state_reasonableness.py`

## Task execution order

1. [LEV-08.01](../tasks/LEV-08.01.md) — Define invariants and reasonableness rules for mastery increases, decreases, uncertainty and prerequisite propagation.
1. [LEV-08.02](../tasks/LEV-08.02.md) — Create synthetic and curated learner histories representing expected learning, guessing, assistance, contradiction, forgetting and recovery.
1. [LEV-08.03](../tasks/LEV-08.03.md) — Implement automated tests for unrelated-concept leakage, impossible jumps and unsupported certainty.
1. [LEV-08.04](../tasks/LEV-08.04.md) — Implement tests ensuring assisted and repeated responses do not automatically equal independent mastery.
1. [LEV-08.05](../tasks/LEV-08.05.md) — Implement tests for staleness and increased uncertainty after long evidence gaps.
1. [LEV-08.06](../tasks/LEV-08.06.md) — Sample real transitions and have teachers and curriculum experts rate their plausibility using a standard rubric.
1. [LEV-08.07](../tasks/LEV-08.07.md) — Measure inter-rater agreement and adjudicate systematic disagreement.
1. [LEV-08.08](../tasks/LEV-08.08.md) — Identify model features or graph relationships causing implausible transitions.
1. [LEV-08.09](../tasks/LEV-08.09.md) — Compare state trajectories with alternative models and simple baselines.
1. [LEV-08.10](../tasks/LEV-08.10.md) — Test whether prerequisite propagation improves prediction without creating unsupported mastery changes.
1. [LEV-08.11](../tasks/LEV-08.11.md) — Require explanation payloads naming the evidence and rules responsible for each material change.
1. [LEV-08.12](../tasks/LEV-08.12.md) — Introduce human-review queues for contradictory or high-impact transitions.
1. [LEV-08.13](../tasks/LEV-08.13.md) — Set quantitative alert thresholds for unexplained jumps, reversals and cross-concept spill-over.
1. [LEV-08.14](../tasks/LEV-08.14.md) — Run continuous transition-reasonableness surveillance after model, KG or content changes.
1. [LEV-08.15](../tasks/LEV-08.15.md) — Maintain a public-facing limitations explanation and internal known-anomaly register.

## Closure rule

The workstream may close only when every task is closed or independently waived and the following condition is supported: **State transitions are educationally plausible.**
