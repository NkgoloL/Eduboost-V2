# PRD-0.5 Test Failure and Collection Stabilisation Plan

PRD-0.5 is the bridge between the PRD-0.4 dependency bootstrap baseline and later CI/test repairs.

## Scope

1. Record the Python test inventory.
2. Record pytest configuration files.
3. Record workflow test command inventory.
4. Record a collection command matrix.
5. Record a test failure classification taxonomy.
6. Record an initial triage register.
7. Preserve strict boundaries: no silent deletion of tests, no silent xfail/skip broadening, and no product behavior repairs in this slice.

## Classification taxonomy

Failures must be classified before repair as one of:

- dependency bootstrap
- import or collection
- stale test contract
- product behavior
- external service
- frontend tooling
- environment only
- documentation or generated artifact

## Deferred slices

- PRD-0.6 handles workflow command hygiene and CI inventory convergence.
- PRD-0.7 handles OpenAPI and generated artifact canonicalisation.
- Later PRD slices handle genuine product behavior repairs.

## Command contract

Backend test commands must prefer `PYTHONPATH=. python3 -m pytest ...`.

Frontend test commands must preserve the existing pnpm contract unless a later slice changes it deliberately.
