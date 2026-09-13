---
title: "Engineering — PRD-11.3R — Coverage Alignment and Documentation-defined Coverage Closure"
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
# PRD-11.3R — Coverage Alignment and Documentation-defined Coverage Closure

This record closes the taxonomy overhaul sequence by making coverage explicit, documented and
verifiable. It responds to the true-state finding that release evidence must not be self-confirming or
presence-only.

## Implemented controls

- Coverage contract recorded in `docs/roadmap/production_readiness/coverage_contract.json`.
- Product/runtime/governance/advisory coverage classes aligned to PRD-11.1R and PRD-11.2R.
- Coverage thresholds aligned to the documentation-defined minimum: at least 70% line coverage,
  branch coverage enabled, `app` as measured source, and evidence retention required.
- Makefile coverage target no longer swallows pytest failure with `|| true`.
- PRD-11.3R capture advances to `PRD-11.0R.RUNTIME-RESTORE`, not to production release.

## Boundary

This is a coverage-alignment and closure gate. It does not claim the runtime baseline is green and does
not authorise production release, deployment, public beta, billing launch or live payment processing.
