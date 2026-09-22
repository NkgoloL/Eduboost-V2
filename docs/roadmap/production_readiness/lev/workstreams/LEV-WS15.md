# LEV-WS15 — Document unsupported uses and residual limitations

**Definition of done:** EduBoost clearly documents which uses remain unsupported.

**Objective:** Prevent valid evidence for one context or use from being overstated as universal support, and make every residual limitation operationally visible and enforceable.

**Dependencies:** Outputs and decisions from all prior workstreams; product and release governance.

**Accountability:** Product Governance Lead (A); Educational Measurement, Legal/Privacy, Curriculum, Engineering and Communications Leads (R/C).

**Indicative duration:** Initial 4-6 weeks; continuous maintenance

## Repository implementation boundary

- `EXISTING: app/services/runtime_kg/feature_flags.py`
- `EXISTING: app/services/runtime_kg/schemas.py`
- `EXISTING: docs/learning_science/mastery_model.md`
- `EXISTING: docs/diagnostics/mastery_model_assessment_contract.md`
- `EXISTING: docs/roadmap/production_readiness/production_readiness_register.json`
- `NEW: docs/research/longitudinal_validation/unsupported_use_register.json`
- `NEW: app/services/educational_validation/use_authorization.py`

## Task execution order

1. [LEV-15.01](../tasks/LEV-15.01.md) — Create a limitations taxonomy covering construct, population, content, time horizon, language, delivery context, model, data and consequence limitations.
1. [LEV-15.02](../tasks/LEV-15.02.md) — Create an unsupported-use register linked to mastery claims, model versions, grades, subjects, populations and decisions.
1. [LEV-15.03](../tasks/LEV-15.03.md) — Map each unsupported use to the missing evidence, known risk and evidence needed for future authorisation.
1. [LEV-15.04](../tasks/LEV-15.04.md) — Define mandatory wording for internal documents, API descriptions, dashboards, reports, marketing and school agreements.
1. [LEV-15.05](../tasks/LEV-15.05.md) — Expose validation status, authorised population, expiry and limitation codes in the model registry and internal APIs.
1. [LEV-15.06](../tasks/LEV-15.06.md) — Implement feature flags and policy checks preventing unsupported high-impact uses.
1. [LEV-15.07](../tasks/LEV-15.07.md) — Add teacher- and administrator-facing explanations when a projection has insufficient evidence, stale evidence or unsupported context.
1. [LEV-15.08](../tasks/LEV-15.08.md) — Add developer documentation describing where mastery values may and may not be consumed.
1. [LEV-15.09](../tasks/LEV-15.09.md) — Review all generated reports and analytics for misleading certainty or unsupported aggregation.
1. [LEV-15.10](../tasks/LEV-15.10.md) — Review contractual, privacy and consent materials to ensure research and operational uses are accurately distinguished.
1. [LEV-15.11](../tasks/LEV-15.11.md) — Update limitations based on impact-study findings, subgroup results and adverse-consequence evidence.
1. [LEV-15.12](../tasks/LEV-15.12.md) — Update authorised and unsupported uses after replication and independent review.
1. [LEV-15.13](../tasks/LEV-15.13.md) — Add CI or release-gate checks requiring current limitation records for every promoted model.
1. [LEV-15.14](../tasks/LEV-15.14.md) — Establish a public correction process for inaccurate claims and an internal incident process for unsupported use.
1. [LEV-15.15](../tasks/LEV-15.15.md) — Review limitations at least quarterly and after every material model, graph, item-bank or policy change.

## Closure rule

The workstream may close only when every task is closed or independently waived and the following condition is supported: **EduBoost clearly documents which uses remain unsupported.**
