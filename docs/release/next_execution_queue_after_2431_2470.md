---
title: Next Execution Queue After DEPLOY-FE-001 / code_2431_2470
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

# Next Execution Queue After DEPLOY-FE-001 / code_2431_2470

## Recommended next batch

`AUTH-SERVICE-CLEANUP-001 / code_2471_2510` — remove auth service monkey-patching and move logout/revoke-all route logic into AuthApplicationService.

## Why

The uploaded audit and repo snapshot still show auth lifecycle methods assigned onto `AuthApplicationService` at module scope and direct `logout` / `revoke_all_tokens` router logic.

## Boundary

This should be a code cleanup/proof batch, not release evidence.
