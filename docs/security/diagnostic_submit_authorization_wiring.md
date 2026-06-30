---
title: "Diagnostic Submit Authorization Wiring"
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

# Diagnostic Submit Authorization Wiring

## Endpoint

This slice enforces learner write authorization on:

```text
POST /api/v2/diagnostics/submit
```

## Policy Function

```python
require_learner_write_for_current_user(current_user, body.learner_id)
```

The diagnostic submit endpoint mutates learner state by completing a diagnostic
session, updating theta, and persisting knowledge gaps. It is therefore treated
as a write operation.

## Coverage

| Scenario | Expected |
| --- | --- |
| Admin submits diagnostic | 200 |
| Guardian with learner claim submits diagnostic | 200 |
| Learner submits own diagnostic | 200 |
| Unrelated guardian | 403 |
| Missing auth | 401 |
| Missing learner | 404 |

## Verification

```bash
pytest -c pytest.ini \
  tests/unit/test_diagnostic_submit_authorization_wiring.py \
  tests/integration/test_diagnostic_submit_authorization.py \
  -q --no-cov
```
