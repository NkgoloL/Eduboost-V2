---
title: "Engineering — PRD-11.0R.RUNTIME-RESTORE.EXECUTION-2 — Generated Contract Regeneration and Frontend Quality Execution"
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
# PRD-11.0R.RUNTIME-RESTORE.EXECUTION-2 — Generated Contract Regeneration and Frontend Quality Execution

This slice starts clearing real generated-contract and frontend-quality blockers.
It repairs command definitions that still referenced non-existent frontend scripts
or ambient `python3`, adds a command-backed gate runner, and records that OpenAPI,
route inventory, TypeScript, ESLint, Vitest, and Next production build evidence
must come from independent command results.

The slice does not claim the frontend or generated-contract gates are green. It
keeps the controlled-beta operational hold and production-release block in place.
