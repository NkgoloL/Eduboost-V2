---
title: "Release — Next Execution Queue After DOCS-INTEL-001 / code_1711_1750"
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
# Next Execution Queue After DOCS-INTEL-001 / code_1711_1750

## Recommended next batch

`TX-ROUTE-001 / code_1751_1790` — production route transaction wiring proof planning/check.

## Scope candidates

1. Inspect live route functions for transaction wrapper usage.
2. Identify which routes can be safely wired now.
3. Add route-level checker for transactional service delegation.
4. Keep live Postgres proof separate from isolated rollback proof.
