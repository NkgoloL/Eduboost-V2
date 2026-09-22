# LEV-WS11 — Measure and control adverse educational effects

**Definition of done:** Adverse effects are measured and acceptably controlled.

**Objective:** Identify, quantify and mitigate unintended effects such as curriculum narrowing, excessive remediation, frustration, inequitable opportunity, over-reliance and privacy harm.

**Dependencies:** Consequence theory; instrumentation; teacher/learner feedback; safety governance.

**Accountability:** Educational Safety Lead (A); Product, Privacy, Curriculum, SRE and Teacher Advisory Panel (R/C).

**Indicative duration:** Starts LEV-0 and remains continuous

## Repository implementation boundary

- `EXISTING: app/services/runtime_kg/feature_flags.py`
- `EXISTING: app/services/consent_service.py`
- `EXISTING: app/services/audit_service.py`
- `EXISTING: app/api_v2_routers/audit.py`
- `EXISTING: docs/operations`
- `EXISTING: docs/compliance`
- `NEW: app/services/educational_validation/safety.py`
- `NEW: docs/research/longitudinal_validation/adverse_consequence_monitoring_plan.md`

## Task execution order

1. [LEV-11.01](../tasks/LEV-11.01.md) — Create an adverse-consequence taxonomy covering educational, psychological, operational, fairness, privacy and teacher-workflow harms.
1. [LEV-11.02](../tasks/LEV-11.02.md) — Define severity, likelihood, detectability, escalation and stop-work criteria.
1. [LEV-11.03](../tasks/LEV-11.03.md) — Define leading and lagging indicators for each major harm.
1. [LEV-11.04](../tasks/LEV-11.04.md) — Instrument curriculum breadth, grade-level exposure, repetition burden, remediation duration, abandonment, help requests and overrides.
1. [LEV-11.05](../tasks/LEV-11.05.md) — Implement learner-, guardian- and teacher-facing feedback and complaint channels.
1. [LEV-11.06](../tasks/LEV-11.06.md) — Establish baseline rates before high-impact adaptation is enabled.
1. [LEV-11.07](../tasks/LEV-11.07.md) — Review sampled learner pathways for over-remediation, skipped content, lock-in and feedback-loop behaviour.
1. [LEV-11.08](../tasks/LEV-11.08.md) — Analyse adverse indicators by learner context and model error type.
1. [LEV-11.09](../tasks/LEV-11.09.md) — Run qualitative interviews or focus groups on frustration, trust, understanding and teacher workload.
1. [LEV-11.10](../tasks/LEV-11.10.md) — Define and implement mitigations such as content floors, maximum remediation windows, teacher override and mandatory grade-level exposure.
1. [LEV-11.11](../tasks/LEV-11.11.md) — Implement automated freeze, rollback or authority-reduction behaviour for breached harm thresholds.
1. [LEV-11.12](../tasks/LEV-11.12.md) — Include adverse outcomes and curriculum-breadth measures in the controlled impact study.
1. [LEV-11.13](../tasks/LEV-11.13.md) — Convene an independent safety review before expanding model authority.
1. [LEV-11.14](../tasks/LEV-11.14.md) — Operate a recurring educational-safety review board and publish internal trend reports.
1. [LEV-11.15](../tasks/LEV-11.15.md) — Maintain post-incident learning, corrective-action verification and reauthorisation requirements.

## Closure rule

The workstream may close only when every task is closed or independently waived and the following condition is supported: **Adverse effects are measured and acceptably controlled.**
