---
title: "Consent Status Authorization Wiring"
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

# Consent Status Authorization Wiring

## Endpoint

This slice enforces learner read authorization on:

```text
GET /api/v2/consent/status/{learner_id}
```

## Policy Function

```python
require_learner_read_for_current_user(current_user, learner)
```

Consent status exposes learner data-rights state and is treated as a read
operation.

## Verification

```bash
pytest -c pytest.ini \
  tests/unit/test_consent_status_authorization_wiring.py \
  tests/integration/test_consent_status_authorization.py \
  -q --no-cov
```
