---
title: Next Execution Queue After code_911_950
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

# Next Execution Queue After code_911_950

## Recommended next batch

`code_951_990`: migrate private auth lifecycle helper bodies into AuthApplicationService proper.

## Scope candidates

1. Move register implementation body into `AuthApplicationService.register`.
2. Move login implementation body into `AuthApplicationService.login`.
3. Move refresh implementation body into `AuthApplicationService.refresh`.
4. Move dev-session implementation body into `AuthApplicationService.create_dev_session`.
5. Add HTTP tests for realistic request/response payloads.
6. Delete private legacy helpers from `auth.py`.
