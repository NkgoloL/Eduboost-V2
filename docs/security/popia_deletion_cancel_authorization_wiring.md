---
title: "POPIA Deletion Cancel Authorization Wiring"
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

# POPIA Deletion Cancel Authorization Wiring

## Endpoint

This slice enforces learner write authorization on:

```text
POST /api/v2/popia/deletion-cancel/{learner_id}
```

## Policy Function

```python
require_learner_write_for_current_user(current_user, learner_id)
```

Cancelling a pending deletion changes learner processing state and therefore
uses the write authorization policy.

## Verification

```bash
pytest -c pytest.ini \
  tests/unit/test_popia_deletion_cancel_authorization_wiring.py \
  tests/integration/test_popia_deletion_cancel_authorization.py \
  -q --no-cov
```
