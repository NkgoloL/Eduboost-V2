---
title: "Release — Next Execution Queue After ROUTE-TX-ROLLUP-001 / code_2191_2230"
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
# Next Execution Queue After ROUTE-TX-ROLLUP-001 / code_2191_2230

## Recommended next batch

`LIVE-DB-TX-EVID-001 / code_2231_2270` — live database transaction evidence attachment support.

## Scope candidates

1. Add controlled helpers for attaching live DB evidence for auth, POPIA, and diagnostics route slices.
2. Validate evidence URL, commit SHA, database target, test result, verifier, and date.
3. Regenerate route transaction slice rollup after evidence attachment.
4. Keep TX-ROUTE-001 blocked until every slice has local source proof and accepted live DB evidence.
