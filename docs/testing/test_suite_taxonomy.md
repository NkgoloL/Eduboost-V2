# EduBoost Test Suite Taxonomy

This document defines the four test classes used by PRD-11.1R and later.

## Product tests

Release-blocking tests for application behaviour: services, routes, DB-backed domain flows, auth, POPIA, billing, learner journeys, diagnostics, lessons, study plans, and parent portal flows.

## Runtime tests

Release-blocking tests for stack health: Postgres, Redis, migrations, schema, `/ready`, worker boot, frontend/backend proxy, and runtime configuration.

## Governance/evidence tests

Supporting tests for PRD records, registers, evidence files, authority transitions, documentation sync, and freshness. These tests must verify that governance data agrees on the same state and was reviewed within 21 days.

## Advisory/static tests

Release-blocking for final release unless explicitly waived: Ruff, mypy, Bandit, coverage, dependency audit, secret scan, route inventory, OpenAPI drift, frontend lint/typecheck/Vitest/build.

## Anti-pattern

A test that only proves that a file exists, a dataclass returns `accepted`, or a string appears in source is not sufficient evidence for product readiness.
