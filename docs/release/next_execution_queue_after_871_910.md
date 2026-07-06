---
title: Next Execution Queue After code_871_910
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

# Next Execution Queue After code_871_910

## Recommended next batch

`code_911_950`: Auth lifecycle integration tests and method-level AuthService extraction.

## Scope candidates

1. Add dependency-override HTTP tests for register/login/refresh/dev-session.
2. Move register orchestration into `AuthApplicationService.register`.
3. Move login orchestration into `AuthApplicationService.login`.
4. Move refresh orchestration into `AuthApplicationService.refresh`.
5. Move dev-session bootstrap into `AuthApplicationService.create_dev_session`.
6. Prove token claims and `email_encrypted` remain correct after extraction.
