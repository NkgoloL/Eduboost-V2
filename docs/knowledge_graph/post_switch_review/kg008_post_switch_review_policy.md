---
title: "KG-8 Post-Switch Review Policy"
status: active
---

# KG-8 Post-Switch Review Policy

KG-8 reviews the controlled runtime KG activation without widening launch authority. The review is evidence-only and must remain repository-local until a separate production/public-beta roadmap is approved.

Required controls:

- KG-ACT-001 must be valid and must explicitly unblock KG-8.
- Runtime KG authority switch may be true because KG-ACT-001 authorised and executed it.
- Production release, deployment, public beta, billing, live learner traffic, database migration, and learner-facing model change remain false.
- Optimisation and load-test execution are not authorised by KG-8; only review/backlog records are authorised.
- POPIA review evidence must remain separate from generated mechanical artifacts.
