---
title: "Parent Learner Progress Authorization Wiring"
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

# Parent Learner Progress Authorization Wiring

## Endpoint

This slice enforces learner read authorization on:

```text
GET /api/v2/parents/learners/{learner_id}/progress
```

## Policy Function

```python
require_learner_read_for_current_user(current_user, learner)
```

The route now uses the same object-authorization policy as learner read and
diagnostic item routes, rather than duplicating guardian/admin checks inline.

## Coverage

| Scenario | Expected |
| --- | --- |
| Admin reads learner progress | 200 |
| Assigned guardian reads learner progress | 200 |
| Unrelated guardian | 403 |
| Missing auth | 401 |
| Missing learner | 404 |

## Verification

```bash
pytest -c pytest.ini \
  tests/unit/test_parent_progress_authorization_wiring.py \
  tests/integration/test_parent_progress_authorization.py \
  -q --no-cov
```
