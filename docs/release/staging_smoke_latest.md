---
title: "Release — Staging Smoke Evidence"
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
# Staging Smoke Evidence

**Status:** runtime smoke passed
<!-- Status: runtime smoke passed -->

- Captured at: `2026-05-17T10:11:49Z`
- Base URL: `http://localhost:8000`
- JSON evidence: `/home/nkgolol/Dev/SandBox/dev/Eduboost-V2/docs/release/staging_smoke_latest.json`

| Check | Method | Path | Expected | Actual | Passed | Error |
|---|---|---|---|---:|---|---|
| health_deep | GET | `/api/v2/health/deep` | `200,503` | 503 | yes |  |
| openapi | GET | `/openapi.json` | `200` | 200 | yes |  |
| security_headers | GET | `/api/v2/health` | `200,404` | 404 | yes |  |
| auth_register_shape | POST | `/api/v2/auth/register` | `201,400,409,422` | 422 | yes |  |
| popia_export_requires_auth | GET | `/api/v2/popia/data-export/smoke-learner` | `401,403,404` | 404 | yes |  |

## Decision

- [ ] Staging smoke accepted by release owner.
- [ ] Staging smoke rejected and release blocked.
