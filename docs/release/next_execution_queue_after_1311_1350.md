---
title: "Release — Next Execution Queue After LESSON-AUTH-001 / code_1311_1350"
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
# Next Execution Queue After LESSON-AUTH-001 / code_1311_1350

## Recommended next batch

`ARCH-001 / code_1351_1390` — import-linter ignore reduction and remaining router repository boundaries.

## Scope candidates

1. Inventory current `.importlinter` ignores.
2. Remove ignores made obsolete by auth, POPIA, diagnostics, ARQ, and lesson repairs.
3. Expand router → repository boundary contracts where safe.
4. Add an ignore-count regression guard.
5. Keep known transitional exceptions explicit with owner/removal notes.
