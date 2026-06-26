---
title: "POPIA Data Export Authorization Wiring"
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

# POPIA Data Export Authorization Wiring

## Endpoint

This slice enforces learner read authorization on:

```text
GET /api/v2/popia/data-export/{learner_id}
```

## Policy Function

```python
require_learner_read_for_current_user(current_user, learner)
```

The route loads the learner before building the export, then applies the shared
Phase 2 object-authorization policy.

## Coverage

| Scenario | Expected |
| --- | --- |
| Admin exports learner data | 200 |
| Assigned guardian exports learner data | 200 |
| Learner exports own data | 200 |
| Unrelated guardian | 403 |
| Missing auth | 401 |
| Missing learner | 404 |

## Verification

```bash
pytest -c pytest.ini \
  tests/unit/test_popia_data_export_authorization_wiring.py \
  tests/integration/test_popia_data_export_authorization.py \
  -q --no-cov
```
