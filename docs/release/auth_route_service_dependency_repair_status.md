---
title: Auth Route Service Dependency Repair Status
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

# Auth Route Service Dependency Repair Status

Generated at: `2026-06-27T02:18:39Z`
Commit: `88840fc52a05c694c6d313e57bc8cba4bcda4c63`

**Status:** `auth-route-service-dependencies-passing`

| Function | Line | References auth_service | Has dependency param | Passed |
|---|---:|---:|---:|---:|
| `me` | 80 | False | False | True |
| `register` | 86 | True | True | True |
| `login` | 105 | True | True | True |
| `create_dev_session` | 123 | True | True | True |
| `refresh` | 147 | True | True | True |
| `list_sessions` | 178 | False | False | True |
| `logout` | 187 | True | True | True |
| `revoke_all_tokens` | 203 | True | True | True |

## Blockers

- None

## No false-closure rules

- F821-free route source does not prove HTTP auth behavior.
- Auth lifecycle HTTP proof remains separate.
- This repair does not approve beta release.
