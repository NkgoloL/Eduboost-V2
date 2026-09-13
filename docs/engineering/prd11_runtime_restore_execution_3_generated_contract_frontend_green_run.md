---
title: "Engineering — PRD-11.0R.RUNTIME-RESTORE.EXECUTION-3 — Generated Contract Drift Cleanup and Frontend Quality Green Run"
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
# PRD-11.0R.RUNTIME-RESTORE.EXECUTION-3 — Generated Contract Drift Cleanup and Frontend Quality Green Run

This slice installs the executable green-run surface for generated API contracts and frontend quality. It regenerates and checks OpenAPI/route inventory through explicit commands and requires frontend type-check, lint, Vitest, build, and release quality outputs to be captured before any green claim is accepted.

The slice does not authorise production release, public beta, billing launch, or operational learner-traffic safety.
