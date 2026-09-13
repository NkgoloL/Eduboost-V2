---
title: "Engineering — PRD-11.0R.RUNTIME-RESTORE-5 — Coverage Execution, Frontend Quality, and Advisory Gate Repair"
status: "active"
owner: "engineering"
reviewers: ['engineering', 'architecture']
audience: "developer"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-09-13"
review_interval_days: 90
evidence_command: "make docs-housekeeping-check"
code_anchors: "[]"
---
# PRD-11.0R.RUNTIME-RESTORE-5 — Coverage Execution, Frontend Quality, and Advisory Gate Repair

This slice repairs the advisory/static side of the runtime-restore sequence.

It does not authorise production release, public beta, billing, deployment, or release tags. It also does not claim the coverage, frontend, or advisory gates are green. It records the gate contract, command plan, blockers, and evidence capture format required before green status may be claimed.

## Required proof families

- Fresh documentation-defined coverage execution.
- Frontend lint, Vitest, and production build.
- Ruff, mypy, and Bandit static checks.
- Python and frontend dependency audits.
- OpenAPI and route inventory drift checks.
- Secret baseline scan and review.

## Release rule

A governance/evidence record cannot override a failed advisory gate. A captured file proving that a command was planned is not the same as evidence that the command passed.
