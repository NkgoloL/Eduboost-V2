---
title: "Release — Next Execution Queue After POPIA-001 / code_1151_1190"
status: "active"
owner: "release"
reviewers: ['release', 'engineering']
audience: "internal"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-09-13"
review_interval_days: 90
evidence_command: "make docs-housekeeping-check"
code_anchors: "[]"
---
# Next Execution Queue After POPIA-001 / code_1151_1190

## Next batch

`EVID-001 / code_1191_1230` — evidence registry and skipped-test governance.

## Scope candidates

1. Add `docs/release/evidence_status_registry.yml`.
2. Add proof statuses: `not-started`, `static-passing`, `runtime-passing`, `integration-passing`, `candidate-verified`, `external-blocked`, `contradicted`, `not-proven`.
3. Treat skipped tests as not-proven.
4. Require P0/P1 items to have runtime/integration proof.
5. Add registry validation script and Makefile targets.
6. Prevent release evidence scripts from silently dirtying docs during routine tests.
