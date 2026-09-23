---
title: "Operations — Staging Smoke Checks"
status: "active"
owner: "operations"
reviewers: ['operations', 'sre', 'engineering']
audience: "internal"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: '2026-09-23'
review_interval_days: 90
evidence_command: make docs-housekeeping-check
code_anchors: "[]"
---
# Staging Smoke Checks

The staging smoke script validates the public operational endpoints after deploy:

```bash
python scripts/staging_smoke.py --base-url https://staging.example.com --json-output reports/staging_smoke.json
```

Checked endpoints:

| Endpoint | Expected |
|---|---|
| `/health` | `200` and status payload |
| `/ready` | `200` when critical dependencies are available |
| `/metrics` | `200` and Prometheus metrics |
| `/docs` | Swagger UI rendered |
| `/openapi.json` | OpenAPI schema available |

A failed staging smoke blocks production promotion.
