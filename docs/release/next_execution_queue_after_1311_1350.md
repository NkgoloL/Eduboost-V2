---
title: Next Execution Queue After LESSON-AUTH-001 / code_1311_1350
status: release-record
owner: release-management
reviewers: [release-management, evidence-custodian, documentation-governance]
audience: release-reviewer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-06
review_interval_days: 180
evidence_command: make docs-housekeeping-stage7-check
code_anchors: [docs/release, docs/documentation/stage_7_release_archive_backlog_codemaps_governance.md]
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
