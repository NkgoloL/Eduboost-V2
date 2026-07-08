# PRD-0.6 — Workflow Command Hygiene and CI Inventory

**Status:** Authority pending evidence capture  
**Depends on:** PRD-0.5 — Test failure and collection stabilisation register

PRD-0.6 standardises workflow pytest command execution and records a CI workflow inventory after the PRD-0.5 failing-test baseline.

## Goals

- Convert direct workflow `pytest` invocations to the canonical module command: `PYTHONPATH=. python3 -m pytest`.
- Record a workflow command inventory for CI follow-up.
- Preserve the PRD-0.5 failure baseline and defer product/test behaviour repair to later slices.
- Keep OpenAPI/generated artifact canonicalisation deferred to PRD-0.7.
- Keep branch/release naming reconciliation deferred to PRD-0.8.

## Non-goals

- No production release, deployment, public beta, live learner traffic, billing launch, or live payment authority.
- No new KG slice.
- No broad product behaviour fixes.
- No deletion or silent xfail of tests.
