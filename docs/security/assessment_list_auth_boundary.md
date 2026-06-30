---
title: "Assessment List Authentication Boundary"
status: active
owner: security
reviewers: [security, engineering, privacy]
audience: security-reviewer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-06-23
review_interval_days: 60
evidence_command: "make docs-housekeeping-stage4-check"
code_anchors: [docs/security/README.md, app/security]
---

# Assessment List Authentication Boundary

## Endpoint

```text
GET /api/v2/assessments
```

## Boundary

This endpoint does not carry a `learner_id`, so it cannot use learner object
authorization. It now requires an authenticated user before exposing assessment
catalog data.

## Verification

```bash
pytest -c pytest.ini tests/unit/test_assessment_list_auth_boundary.py -q --no-cov
```
