---
title: "Auth Service Ownership Report"
status: archived
owner: architecture
reviewers: [architecture, engineering]
audience: developer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-09-23
review_interval_days: null
evidence_command: null
code_anchors: [docs/architecture/README.md]
---

# Auth Service Ownership Report

Generated at: `2026-05-18T18:00:26Z`

| Check | Value |
|---|---|
| Auth router has legacy helpers | False |
| Auth router imports repositories | False |
| Auth router has future annotations | False |

## AuthApplicationService lifecycle ownership

- `register`: True
- `login`: True
- `refresh`: True
- `create_dev_session`: True

## Implementation functions

- `_canonical_access_claims`
- `_maybe_await`
- `_set_refresh_cookie`
- `create_dev_session_impl`
- `login_impl`
- `refresh_impl`
- `register_impl`
