# LEV-WS07 — Demonstrate transfer validity

**Definition of done:** Estimates predict transfer to unfamiliar tasks.

**Objective:** Establish that learner-state projections predict application of knowledge to unfamiliar representations and related problems rather than memorisation of exposed items.

**Dependencies:** WS02 transfer bank; WS06 retention design; curriculum expert review.

**Accountability:** Mathematics Curriculum Lead (A); Psychometric Lead, Research Lead, Content Lead (R).

**Indicative duration:** 9-15 months

## Repository implementation boundary

- `EXISTING: app/services/runtime_kg/service.py`
- `EXISTING: app/services/runtime_kg/schemas.py`
- `EXISTING: app/modules/lessons/adaptive_remediation.py`
- `EXISTING: app/modules/study_plans/runtime_kg_planner.py`
- `EXISTING: app/services/content_blueprint_validation.py`
- `NEW: app/services/educational_validation/transfer.py`
- `NEW: scripts/educational_validation/run_transfer_analysis.py`

## Task execution order

1. [LEV-07.01](../tasks/LEV-07.01.md) — Define near transfer, far transfer and unsupported extrapolation for each CAPS concept family.
1. [LEV-07.02](../tasks/LEV-07.02.md) — Create a protected transfer-item bank using unfamiliar wording, representation and problem contexts.
1. [LEV-07.03](../tasks/LEV-07.03.md) — Ensure transfer items preserve the target mathematical construct while changing superficial features.
1. [LEV-07.04](../tasks/LEV-07.04.md) — Map expected transfer relationships and prerequisite paths in the KG without using outcome data.
1. [LEV-07.05](../tasks/LEV-07.05.md) — Pilot transfer items for difficulty, discrimination, language load and unintended strategy requirements.
1. [LEV-07.06](../tasks/LEV-07.06.md) — Collect transfer outcomes after mastery projections are frozen.
1. [LEV-07.07](../tasks/LEV-07.07.md) — Estimate the relationship between concept mastery and near-transfer performance.
1. [LEV-07.08](../tasks/LEV-07.08.md) — Estimate far-transfer performance where curriculum and sample size support the claim.
1. [LEV-07.09](../tasks/LEV-07.09.md) — Compare graph-informed transfer predictions with flat skill and item-level baselines.
1. [LEV-07.10](../tasks/LEV-07.10.md) — Test whether prerequisite mastery patterns predict successful transfer.
1. [LEV-07.11](../tasks/LEV-07.11.md) — Analyse transfer error by representation, language, context and learner subgroup.
1. [LEV-07.12](../tasks/LEV-07.12.md) — Identify concepts for which the system must not infer transfer without direct evidence.
1. [LEV-07.13](../tasks/LEV-07.13.md) — Test whether transfer-targeted recommendations improve unfamiliar-task performance.
1. [LEV-07.14](../tasks/LEV-07.14.md) — Replicate transfer findings using new items and a later cohort.
1. [LEV-07.15](../tasks/LEV-07.15.md) — Maintain item-exposure controls and periodically refresh transfer instruments.

## Closure rule

The workstream may close only when every task is closed or independently waived and the following condition is supported: **Estimates predict transfer to unfamiliar tasks.**
