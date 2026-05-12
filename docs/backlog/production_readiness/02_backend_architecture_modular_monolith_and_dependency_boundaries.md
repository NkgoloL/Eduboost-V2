# 2. Backend architecture, modular monolith, and dependency boundaries

## 2.1 Canonical architecture

- [ ] `P0` Reconfirm V2 is a modular monolith.
- [ ] `P0` Reconfirm no production microservices except explicitly documented inference sidecar if retained.
- [ ] `P0` Reconfirm no Celery/RabbitMQ for new V2 work unless explicitly re-approved.
- [ ] `P0` Reconcile docs that say “no microservices” with any inference sidecar.
- [ ] `P0` Reconcile docs that say “V1 fully deleted” with actual legacy shim/archive state.
- [ ] `P1` Update architecture diagram.
- [ ] `P1` Add `docs/backend_architecture.md`.
- [ ] `P1` Add `docs/architecture_decisions.md` index.
- [ ] `P1` Document bounded contexts:
  - auth
  - learners
  - consent
  - diagnostics
  - lessons
  - study plans
  - gamification
  - parent portal
  - POPIA
  - billing
  - jobs
  - observability
- [ ] `P2` Generate module dependency graph.

## 2.2 Business logic location

- [ ] `P0` Decide canonical business-logic location.
- [ ] `P0` Choose between `app/services` and `app/modules/<context>/service.py`.
- [ ] `P0` Write ADR `docs/adr/0010-business-logic-location.md`.
- [ ] `P1` Inventory all files in `app/services`.
- [ ] `P1` Inventory all files in `app/modules`.
- [ ] `P1` Identify duplicate service concepts.
- [ ] `P1` Collapse duplicate auth service concepts.
- [ ] `P1` Collapse duplicate consent service concepts.
- [ ] `P1` Collapse duplicate diagnostic service concepts.
- [ ] `P1` Collapse duplicate lesson service concepts.
- [ ] `P1` Collapse duplicate study-plan service concepts.
- [ ] `P1` Collapse duplicate parent-portal service concepts.
- [ ] `P1` Collapse duplicate billing service concepts.
- [ ] `P1` Mark deprecated service paths with deprecation notices.
- [ ] `P2` Add migration guide for service path changes.

## 2.3 Router thinness

- [ ] `P1` Audit auth router for business logic.
- [ ] `P1` Audit learners router for business logic.
- [ ] `P1` Audit lessons router for business logic.
- [ ] `P1` Audit study plans router for business logic.
- [ ] `P1` Audit diagnostics router for business logic.
- [ ] `P1` Audit gamification router for business logic.
- [ ] `P1` Audit onboarding router for business logic.
- [ ] `P1` Audit parents router for business logic.
- [ ] `P1` Audit billing router for business logic.
- [ ] `P1` Audit consent router for business logic.
- [ ] `P1` Audit consent renewal router for business logic.
- [ ] `P1` Audit POPIA router for business logic.
- [ ] `P1` Audit jobs router for business logic.
- [ ] `P1` Move business logic out of routers.
- [ ] `P1` Keep routers limited to validation, dependencies, service calls, and response mapping.
- [ ] `P1` Add code-review checklist item: “Router contains no business logic.”
- [ ] `P2` Add static complexity threshold for router functions.

## 2.4 Import boundaries

- [ ] `P1` Add `import-linter` configuration.
- [ ] `P1` Enforce `routers -> services/modules`.
- [ ] `P1` Enforce `services/modules -> repositories`.
- [ ] `P1` Enforce `repositories -> models/database`.
- [ ] `P1` Enforce `domain` has no infrastructure imports.
- [ ] `P1` Enforce repositories never import routers.
- [ ] `P1` Enforce services never depend on FastAPI `Request` unless explicitly justified.
- [ ] `P1` Add `lint-imports` to CI.
- [ ] `P1` Add import boundary check to required branch protection.
- [ ] `P2` Add docs explaining import boundaries.

## 2.5 Metaphor-layer cleanup

- [ ] `P1` Inventory active-code references to `executive`.
- [ ] `P1` Inventory active-code references to `judiciary`.
- [ ] `P1` Inventory active-code references to `fourth_estate`.
- [ ] `P1` Inventory active-code references to `ether`.
- [ ] `P1` Rename active engineering boundaries to domain names.
- [ ] `P1` Move metaphor language to product/storytelling docs only, if retained.
- [ ] `P2` Add glossary mapping old metaphor names to new domain names.
- [ ] `P2` Remove metaphor terminology from onboarding docs for new engineers.

---

