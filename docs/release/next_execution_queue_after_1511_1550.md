---
title: "Release — Next Execution Queue After TX-DIAG-001 / code_1511_1550"
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
# Next Execution Queue After TX-DIAG-001 / code_1511_1550

## Recommended next batch

`TX-LESSON-001 / code_1551_1590` — lesson completion + gamification XP transaction rollback proof.

## Scope candidates

1. Model lesson completion and XP award as one transaction.
2. Prove lesson completion failure creates no XP event.
3. Prove XP award failure creates no completed lesson orphan.
4. Keep broader TX-001 open until remaining high-risk domains have rollback proof.
