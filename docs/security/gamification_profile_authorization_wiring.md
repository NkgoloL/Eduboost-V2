---
title: "Gamification Profile Authorization Wiring"
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

# Gamification Profile Authorization Wiring

## Endpoint

This slice enforces learner read authorization on:

```text
GET /api/v2/gamification/profile/{learner_id}
```

## Policy Function

```python
require_learner_read_for_current_user(current_user, learner)
```

The route loads the learner first, applies shared object authorization, then
checks consent and returns the gamification profile.

## Verification

```bash
pytest -c pytest.ini \
  tests/unit/test_gamification_profile_authorization_wiring.py \
  tests/integration/test_gamification_profile_authorization.py \
  -q --no-cov
```
