---
title: "Ether Onboarding Questions Authentication Boundary"
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

# Ether Onboarding Questions Authentication Boundary

## Endpoint

```text
GET /api/v2/ether/onboarding/questions
```

## Policy

The route now requires an authenticated user:

```python
user: dict = Depends(get_current_user)
```

The route does not carry a `learner_id`, so it is guarded by authentication
rather than learner-object authorization.

## Verification

```bash
pytest -c pytest.ini tests/unit/test_ether_onboarding_questions_auth_boundary.py -q --no-cov
make learner-authz-check
```
