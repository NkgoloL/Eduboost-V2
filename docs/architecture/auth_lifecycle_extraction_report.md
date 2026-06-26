---
title: "Auth Lifecycle Extraction Report"
status: current-evidence
owner: architecture
reviewers: [architecture, engineering]
audience: developer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-06-23
review_interval_days: 60
evidence_command: "make docs-housekeeping-stage4-check"
code_anchors: [docs/architecture/README.md]
---

# Auth Lifecycle Extraction Report

Generated at: `2026-05-18T16:23:45Z`

| Method | Delegated through AuthApplicationService |
|---|---:|
| `register` | True |
| `login` | True |
| `refresh` | True |
| `create_dev_session` | True |

## Preserved legacy helpers

- `_auth_lifecycle_legacy_create_dev_session_impl`
- `_auth_lifecycle_legacy_login_impl`
- `_auth_lifecycle_legacy_refresh_impl`
- `_auth_lifecycle_legacy_register_impl`

## Remaining debt

- Move preserved private helpers into `AuthApplicationService` proper.
- Add HTTP request/response tests using dependency overrides and realistic payloads.
