---
title: "Release — Next Execution Queue After ARCH-001R / code_1351_1390R"
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
# Next Execution Queue After ARCH-001R / code_1351_1390R

## Next batch

`TX-001 / code_1391_1430` — transaction boundary audit and rollback proofs.

## Scope candidates

1. Inventory multi-write operations.
2. Identify transaction ownership per service/application boundary.
3. Add rollback tests for auth register, POPIA lifecycle + audit, diagnostics response + mastery, and lesson completion + XP.
4. Update evidence registry with transaction-bound proof status.
