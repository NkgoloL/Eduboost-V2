---
title: Next Execution Queue After DEPLOY-FE-RUNTIME-001 / code_2471_2510
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

# Next Execution Queue After DEPLOY-FE-RUNTIME-001 / code_2471_2510

## Recommended next batch

`AUTH-SERVICE-CLEANUP-001 / code_2511_2550` — remove auth service monkey-patching and move logout/revoke-all route logic into AuthApplicationService.

## Why

The audit still flags auth service monkey-patching/module-level method assignment and logout/revoke-all route logic in the router. This is a code-quality/runtime maintainability issue, not a release-evidence issue.
