---
title: "Generated Contract Regeneration and Frontend Quality Execution Contract"
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
code_anchors: ["docs/testing/generated_contract_frontend_quality_execution.md"]
---

# Generated Contract Regeneration and Frontend Quality Execution Contract

**PRD:** PRD-11.0R.RUNTIME-RESTORE.EXECUTION-2
**Status:** Authority contract
**Reviewed:** 2026-07-11T07:30:00+00:00

This contract turns generated API contracts and frontend quality into command-backed
release evidence. It is not enough for OpenAPI, route inventory, lint, Vitest, or
build evidence to exist as files. Each green claim must come from an independent
command result captured on the candidate commit.

## Release-blocking gates

- Generated OpenAPI regeneration.
- Generated OpenAPI and route-inventory drift checks.
- Frontend TypeScript type-check.
- Frontend ESLint.
- Frontend Vitest.
- Frontend production build.

## Evidence rules

- Use the active repository Python interpreter for backend-generated contract commands.
- Use the frontend package manager declared in `app/frontend/package.json` for frontend commands.
- Capture stdout, stderr, exit code, command, working directory, timestamp, and artifact path.
- Keep `generated_contracts_green` and `frontend_quality_green` false unless command outputs pass.
- Governance records cannot override failed generated-contract or frontend-quality command results.

## Handoff

After PRD-11.0R.RUNTIME-RESTORE.EXECUTION-2 evidence is captured, the next authorised
item is `PRD-11.0R.RUNTIME-RESTORE.EXECUTION-3`. Production release remains blocked until the full true-state
baseline is green.
