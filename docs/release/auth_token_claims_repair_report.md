---
title: "Release — Auth Token Claims Repair Report"
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
# Auth Token Claims Repair Report

Generated at: `2026-05-17T20:36:18Z`

**Status:** implemented

| Item | Value |
|---|---|
| Auth router | `app/api_v2_routers/auth.py` |
| Canonical helper import inserted | True |
| Obvious raw email_encrypted writes patched | 0 |
| Inline create_access_token claim calls patched | 0 |

## Boundary

This batch centralizes token-claim semantics and blocks obvious raw email_encrypted persistence. Full AuthService extraction is a later boundary-consolidation batch.
