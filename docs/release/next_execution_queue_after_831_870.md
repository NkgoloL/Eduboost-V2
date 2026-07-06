---
title: Next Execution Queue After code_831_870
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

# Next Execution Queue After code_831_870

## Recommended next batch

`code_871_910`: Full AuthService extraction and router repository import closure.

## Scope candidates

1. Move remaining auth repository interactions into canonical AuthService.
2. Remove auth repository imports.
3. Remove auth import-linter ignore rules.
4. Add register/login/refresh integration tests with dependency overrides.
5. Keep focused ruff mandatory.
