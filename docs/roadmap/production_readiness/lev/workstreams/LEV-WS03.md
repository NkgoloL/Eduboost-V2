# LEV-WS03 — Make learner evidence and state changes fully traceable

**Definition of done:** Learner evidence and state changes are fully traceable.

**Objective:** Provide an immutable and reconstructable chain from learner interaction through model interpretation, state transition, recommendation, delivered action and later outcome.

**Dependencies:** WS01 state definitions; data architecture; event schemas; model registry; privacy design.

**Accountability:** Runtime KG Lead (A); Data Platform Lead, Backend Lead, Privacy Lead, SRE Lead (R/C).

**Indicative duration:** 3-5 months

## Repository implementation boundary

- `EXISTING: app/models/runtime_kg.py`
- `EXISTING: app/services/runtime_kg/repository.py`
- `EXISTING: app/services/runtime_kg/service.py`
- `EXISTING: app/services/runtime_kg/integration.py`
- `EXISTING: app/repositories/audit_repository.py`
- `EXISTING: app/services/audit_service.py`
- `EXISTING: app/core/audit.py`
- `EXISTING: alembic/versions`
- `NEW: app/models/educational_validation.py`
- `NEW: app/repositories/educational_validation_repository.py`
- `NEW: app/services/educational_validation/traceability.py`
- `NEW: alembic/versions/<new>_educational_validation_traceability.py`

## Task execution order

1. [LEV-03.01](../tasks/LEV-03.01.md) — Specify the canonical learner-interaction event schema, including item, concept, content, assistance, timing, language, device and consent context.
1. [LEV-03.02](../tasks/LEV-03.02.md) — Specify the canonical mastery-state-transition event with pre-state, post-state, uncertainty, evidence references, model version, graph version and update rationale.
1. [LEV-03.03](../tasks/LEV-03.03.md) — Implement append-only event persistence with stable event identifiers, ordering guarantees and tamper-evident integrity controls.
1. [LEV-03.04](../tasks/LEV-03.04.md) — Create a model registry storing code commit, training data manifest, features, parameters, authorised population, limitations, expiry and rollback model.
1. [LEV-03.05](../tasks/LEV-03.05.md) — Create a knowledge-graph snapshot registry and compatibility links between graph, item-bank and model versions.
1. [LEV-03.06](../tasks/LEV-03.06.md) — Record recommendation decisions, policy version, accepted or overridden status, delivered content and subsequent learner outcome.
1. [LEV-03.07](../tasks/LEV-03.07.md) — Implement trace-reconstruction APIs and internal tools for authorised reviewers.
1. [LEV-03.08](../tasks/LEV-03.08.md) — Implement idempotency, duplicate detection, late-event handling, clock-skew handling and correction-event semantics.
1. [LEV-03.09](../tasks/LEV-03.09.md) — Add event completeness, sequencing, orphan-reference and schema-version monitoring.
1. [LEV-03.10](../tasks/LEV-03.10.md) — Define lawful retention, pseudonymisation, de-identification, deletion and research-export rules for validation events.
1. [LEV-03.11](../tasks/LEV-03.11.md) — Ensure erasure workflows preserve lawful aggregated evidence while removing or anonymising learner-identifiable data.
1. [LEV-03.12](../tasks/LEV-03.12.md) — Run replay validation comparing reconstructed states with production states across a representative sample.
1. [LEV-03.13](../tasks/LEV-03.13.md) — Run adversarial audit tests for event mutation, missing evidence, wrong model linkage and unauthorised access.
1. [LEV-03.14](../tasks/LEV-03.14.md) — Create a traceability evidence report and operating procedure for research, incidents and model challenges.

## Closure rule

The workstream may close only when every task is closed or independently waived and the following condition is supported: **Learner evidence and state changes are fully traceable.**
