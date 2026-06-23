---
title: "Active Consent Route Order"
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
