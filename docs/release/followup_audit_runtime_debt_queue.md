---
title: "Release — Follow-up Audit Runtime Debt Queue"
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
# Follow-up Audit Runtime Debt Queue

**Status:** active after code_781_830R2

## Remaining high-value runtime work

1. Add HTTP/integration tests for every POPIA consent lifecycle route.
2. Add real DB diagnostics tests for unserved item IDs and CAPS/session binding.
3. Complete full AuthService extraction and remove remaining auth repository imports.
4. Make focused ruff checks mandatory in CI.
5. Run live ARQ worker smoke for consent reminder jobs.
