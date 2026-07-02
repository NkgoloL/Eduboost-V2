# RR-002 — Privacy / POPIA Completion

**Status:** authority harness installed / evidence pending  
**Register item:** `RR-002` from `docs/roadmap/reconciliation/outstanding_work_register.md`  
**Canonical area:** Privacy and authorization

## Scope

This slice closes the concrete POPIA safety gaps that remained after runtime
readiness and seeded E2E evidence:

- legal-hold checks are explicit before erasure execution;
- erasure requests persist a state-machine record instead of silently deleting;
- export is offered or waived before erasure can execute;
- legacy learner/parent delete routes use the canonical POPIA service;
- audit immutability remains preserved.

## Boundaries

This does not authorise production release, deployment, public beta, release
tagging, runtime KG implementation, or broader learner migration.
