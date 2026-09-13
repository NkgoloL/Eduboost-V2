---
title: "Release — Next Execution Queue After DEPLOY-FE-001 / code_2431_2470"
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
# Next Execution Queue After DEPLOY-FE-001 / code_2431_2470

## Recommended next batch

`AUTH-SERVICE-CLEANUP-001 / code_2471_2510` — remove auth service monkey-patching and move logout/revoke-all route logic into AuthApplicationService.

## Why

The uploaded audit and repo snapshot still show auth lifecycle methods assigned onto `AuthApplicationService` at module scope and direct `logout` / `revoke_all_tokens` router logic.

## Boundary

This should be a code cleanup/proof batch, not release evidence.
