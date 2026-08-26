---
title: "Documentation-defined Coverage Contract"
status: "active"
owner: "quality"
reviewers: ["quality", "engineering"]
audience: "developer"
source_of_truth: false
supersedes: []
superseded_by: null
prd_id: "PRD-11.3R"
last_reviewed: "2026-08-26"
review_interval_days: 21
evidence_command: "make docs-housekeeping-check"
code_anchors: ["docs/testing/documentation_defined_coverage.md"]
---

# Documentation-defined Coverage Contract

PRD-11.3R aligns coverage with the PRD-11.1R test taxonomy and PRD-11.2R script taxonomy.
Coverage is not only a line percentage. A release candidate must prove coverage across four evidence
classes: product, runtime, governance, and advisory/static.

## Required coverage classes

1. **Product coverage** — real behaviour for services, routes, database access, auth, POPIA, billing,
   learner journeys, parent portal, assessment, lesson, study-plan, runtime KG and audit trails.
2. **Runtime coverage** — Postgres, Redis, migration lineage, schema, `/ready`, worker, frontend proxy,
   backup/restore and rollback.
3. **Governance coverage** — production register, PRD register, evidence files, authority transitions,
   documentation freshness and release-boundary agreement.
4. **Advisory/static coverage** — Ruff, mypy, Bandit, coverage, dependency audit, route inventory,
   OpenAPI drift, secret scanning and frontend quality.

## Release rule

Presence-only checks do not prove coverage. Constant `accepted: true` readiness payloads do not prove
coverage. Coverage evidence must include command outputs, negative-path proof where applicable, and
freshness metadata. PRD-11.3R does not authorise production release; it returns the stream to
`PRD-11.0R.RUNTIME-RESTORE` so the restored runtime baseline can execute the real gates.
