# PRD-11.1R — Test Suite Taxonomy and Behavioural Gate Overhaul

Status: authority recorded, evidence pending.

This corrective PRD makes the test system explicitly separate release-blocking product/runtime/static gates from supporting governance/evidence gates. It responds to the true-state report finding that EduBoost can produce internally consistent PRD evidence while runtime stack, schema, tests, dependency audits, and drift checks remain red.

## Test classes

1. Product tests: real application behaviour, services, routes, DB-backed domain flows, auth, POPIA, billing, learner journeys.
2. Runtime tests: Postgres, Redis, migrations, schema, `/ready`, worker, frontend proxy.
3. Governance/evidence tests: PRD records, registers, evidence files, authority transitions, documentation sync and freshness.
4. Advisory/static tests: Ruff, mypy, Bandit, coverage, dependency audit, route inventory, OpenAPI drift.

## Behavioural gate rule

Presence-only tests are insufficient for release evidence. Product-critical and runtime-critical claims require behaviour or negative-path tests. Governance evidence is supporting unless it consumes independent runtime/product outputs.

## Handoff rule

PRD-11.2R is not authorised until PRD-11.1R evidence is captured and the taxonomy verifier reports `valid: true`.
