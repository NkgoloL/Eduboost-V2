---
title: "Release — Auth Token Claims Introspection"
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
# Auth Token Claims Introspection

Generated at: `2026-05-17T20:36:18Z`

| Check | Value |
|---|---|
| Auth router | app/api_v2_routers/auth.py |
| Canonical claim helper imported | True |
| Raw email_encrypted assignment | False |
| Local token claim marker count | 9 |

## Functions

- `_canonical_access_claims`
- `_canonical_refresh_claims`
- `_legacy_refresh_error_response`
- `_set_refresh_cookie`
- `create_dev_session`
- `list_sessions`
- `login`
- `logout`
- `me`
- `refresh_token`
- `register`
- `revoke_all_tokens`
