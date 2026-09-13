---
title: "Release — Next Execution Queue After AUTH-LIFECYCLE-SEMANTIC-PROOF-001 / code_2631_2670"
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
# Next Execution Queue After AUTH-LIFECYCLE-SEMANTIC-PROOF-001 / code_2631_2670

## Recommended next batch

`AUTH-REFRESH-DB-PROOF-001 / code_2671_2710` — focused DB-backed proof for refresh-token persistence, logout clearing, and reuse detection.

## Boundary

Use a disposable test database or explicit test fixture cleanup. Do not classify skipped DB tests as proof.
