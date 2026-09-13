---
title: "Engineering — PRD-11.0R.RUNTIME-RESTORE.EXECUTION-4 — Frontend Quality Defect Repair and Generated Contract Green Evidence"
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
# PRD-11.0R.RUNTIME-RESTORE.EXECUTION-4 — Frontend Quality Defect Repair and Generated Contract Green Evidence

This slice repairs the execution path for generated-contract/frontend-quality evidence and makes the green state dependent on real command outputs.

## Scope

- Regenerate OpenAPI and route inventory from the canonical app.
- Re-run read-only generated-contract drift checks.
- Run frontend release quality through `quality:release`.
- Prevent frontend build/type side effects from silently dirtying tracked files.
- Keep release/billing/public-beta authorities locked.

## Boundary

This slice does not authorise production release, deployment, public beta, billing, or live payment processing.
