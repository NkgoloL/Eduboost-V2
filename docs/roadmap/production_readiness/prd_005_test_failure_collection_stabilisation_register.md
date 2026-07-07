# PRD-0.5 — Test Failure and Collection Stabilisation Register

**Status:** Authority template. Evidence capture records closure.  
**Depends on:** PRD-0.4 — Test/dependency bootstrap baseline.  
**Next authorised item after closure:** PRD-0.6 — Workflow command hygiene and CI inventory.

## Purpose

PRD-0.5 creates a reproducible register for test failure and collection stabilisation before broad repairs begin.

This slice records the test inventory, command matrix, failure classification taxonomy, and triage queue that future PRD-0 work must use.

## Non-goals

- No production release authority.
- No deployment authority.
- No public beta or live learner traffic authority.
- No billing or live payment authority.
- No product feature implementation.
- No silent deletion of failing tests.
- No silent xfail/skip broadening.
- No broad product behavior repair.

## Required evidence

Evidence capture must record:

- PRD-0.4 verifier is valid.
- Test inventory is present.
- Collection command matrix is present.
- Failure classification schema is present.
- Triage register is present.
- No test deletion is authorised.
- Workflow command hygiene is deferred to PRD-0.6.
- OpenAPI/generated artifact canonicalisation is deferred to PRD-0.7.

## Boundary

Runtime KG authority remains executed from KG-ACT-001, but production release, deployment, public beta, live learner traffic, billing, live payments, new KG slices, and PRD-1 implementation remain unauthorised.
