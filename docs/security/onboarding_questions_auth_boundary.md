---
title: "Onboarding Questions Authentication Boundary"
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

# Onboarding Questions Authentication Boundary

## Endpoint

```text
GET /api/v2/onboarding/questions
```

## Boundary

This endpoint returns onboarding question catalog data. It does not carry a
`learner_id`, so it is guarded by authentication rather than learner object
authorization.

## Verification

```bash
pytest -c pytest.ini tests/unit/test_onboarding_questions_auth_boundary.py -q --no-cov
```
