---
title: "Active Consent Route Order"
status: active
owner: security
reviewers: [security, engineering, privacy]
audience: security-reviewer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: '2026-09-23'
review_interval_days: 90
evidence_command: 'PYTHON=.venv/bin/python make popia-consent-order-check'
code_anchors: [app/api_v2_routers/learners.py, tests/unit/test_active_consent_route_order.py]
---
# Active Consent Route Order

## Policy

Evidence phrase: object authorization must run before active POPIA consent.


For learner-scoped routes, object authorization must run before active POPIA
consent enforcement.

That order prevents consent checks from becoming an oracle for unauthorized
actors.

## Command

```bash
make popia-consent-order-check
```

## Verification

```bash
pytest -c pytest.ini tests/unit/test_active_consent_route_order.py -q --no-cov
```
