---
title: "Release — Next Execution Queue After code_831_870"
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
# Next Execution Queue After code_831_870

## Recommended next batch

`code_871_910`: Full AuthService extraction and router repository import closure.

## Scope candidates

1. Move remaining auth repository interactions into canonical AuthService.
2. Remove auth repository imports.
3. Remove auth import-linter ignore rules.
4. Add register/login/refresh integration tests with dependency overrides.
5. Keep focused ruff mandatory.
