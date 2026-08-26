---
title: "PRD-11.2R Script Taxonomy and Functional Overhaul"
status: "active"
owner: "quality"
reviewers: ["quality", "engineering"]
audience: "developer"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-08-26"
review_interval_days: 60
evidence_command: "make docs-housekeeping-check"
code_anchors: ["docs/testing/script_taxonomy.md"]
---

# PRD-11.2R Script Taxonomy and Functional Overhaul

PRD-11.2R groups repository scripts by both evidence domain and functional role so that scripts are no longer treated as interchangeable helpers.

## Script classes

| Class | Purpose | Release use |
|---|---|---|
| Product | Product behaviour scripts for services, routes, DB-backed auth, POPIA, billing and learner journeys. | Blocking when used as product proof. |
| Runtime | Stack health scripts for Postgres, Redis, migrations, schema, `/ready`, worker and frontend proxy. | Blocking for release/runtime proof. |
| Governance | PRD records, registers, evidence files, authority transitions, documentation sync and freshness. | Supporting evidence only. |
| Advisory | Ruff, mypy, Bandit, coverage, dependency audit, route inventory, OpenAPI drift and generated artifacts. | Blocking when the relevant release gate requires it. |

## Functional roles

Scripts must be understood as one of: `audit`, `verify`, `capture`, `collect`, `generate`, `apply`, or `maintenance`.

Audit and verify scripts are read-only. Capture scripts may write evidence, but they must consume independent command outputs and must not convert unknown or red runtime state into green proof. Apply and maintenance scripts intentionally mutate the repository, but they are never standalone release evidence.

## Governance sync and freshness

The production readiness register, PRD-11 register, test-suite taxonomy and script taxonomy must agree on the active corrective state and must be reviewed within 21 days. Governance tests remain important, but governance success cannot substitute for product/runtime/security proof.
