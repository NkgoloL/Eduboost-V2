# LEV-WS13 — Operate drift detection and revalidation controls

**Definition of done:** Drift and revalidation controls operate in production.

**Objective:** Ensure the validated model remains within its authorised evidence envelope as learners, items, content, graph structure, interaction design and software evolve.

**Dependencies:** Production telemetry; model/graph registry; reference metrics; SRE integration.

**Accountability:** ML Operations Lead (A); SRE Lead, Runtime KG Lead, Psychometric Lead, Content Governance Lead (R/C).

**Indicative duration:** Build during LEV-3 to LEV-5; continuous operation thereafter

## Repository implementation boundary

- `EXISTING: app/services/runtime_kg/feature_flags.py`
- `EXISTING: app/services/runtime_kg/acceptance.py`
- `EXISTING: prometheus`
- `EXISTING: grafana`
- `EXISTING: alertmanager`
- `EXISTING: docs/observability`
- `EXISTING: docs/operations`
- `EXISTING: scripts/roadmap_reconciliation`
- `NEW: app/services/educational_validation/drift.py`
- `NEW: scripts/educational_validation/check_educational_model_drift.py`
- `NEW: prometheus/rules/educational_validation.yml`

## Task execution order

1. [LEV-13.01](../tasks/LEV-13.01.md) — Define drift types: population, concept prevalence, item parameter, calibration, performance, feature, label, graph, content and policy drift.
1. [LEV-13.02](../tasks/LEV-13.02.md) — Create authorised reference distributions and validation baselines for each production model.
1. [LEV-13.03](../tasks/LEV-13.03.md) — Define warning, intervention and freeze thresholds with statistical and educational rationale.
1. [LEV-13.04](../tasks/LEV-13.04.md) — Implement dashboards for calibration, error, retention, transfer, state reasonableness and context mix.
1. [LEV-13.05](../tasks/LEV-13.05.md) — Implement item and anchor drift monitoring and automatic quarantine of suspect items.
1. [LEV-13.06](../tasks/LEV-13.06.md) — Implement graph-change impact analysis covering renamed, merged, split, added and removed concepts.
1. [LEV-13.07](../tasks/LEV-13.07.md) — Implement shadow evaluation for candidate models and policies before promotion.
1. [LEV-13.08](../tasks/LEV-13.08.md) — Define model expiry dates, revalidation intervals and mandatory triggers after material change.
1. [LEV-13.09](../tasks/LEV-13.09.md) — Test alerts, authority reduction, feature flags, rollback and last-validated-model recovery.
1. [LEV-13.10](../tasks/LEV-13.10.md) — Validate monitoring sensitivity using known perturbations and historical back-testing.
1. [LEV-13.11](../tasks/LEV-13.11.md) — Create recurring educational model review meetings combining SRE, psychometrics, curriculum and fairness evidence.
1. [LEV-13.12](../tasks/LEV-13.12.md) — Automate evidence capture for every model promotion, recalibration, threshold change and rollback.
1. [LEV-13.13](../tasks/LEV-13.13.md) — Require revalidation before extending the model to a new grade, subject, language or high-impact use.
1. [LEV-13.14](../tasks/LEV-13.14.md) — Audit monitoring coverage, alert response and unresolved drift at least annually.
1. [LEV-13.15](../tasks/LEV-13.15.md) — Maintain disaster-recovery procedures for telemetry loss, registry corruption and invalid model deployment.

## Closure rule

The workstream may close only when every task is closed or independently waived and the following condition is supported: **Drift and revalidation controls operate in production.**
