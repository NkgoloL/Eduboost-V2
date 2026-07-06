---
title: Follow-up Audit Runtime Debt Queue
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

# Follow-up Audit Runtime Debt Queue

**Status:** active after code_781_830R2

## Remaining high-value runtime work

1. Add HTTP/integration tests for every POPIA consent lifecycle route.
2. Add real DB diagnostics tests for unserved item IDs and CAPS/session binding.
3. Complete full AuthService extraction and remove remaining auth repository imports.
4. Make focused ruff checks mandatory in CI.
5. Run live ARQ worker smoke for consent reminder jobs.
