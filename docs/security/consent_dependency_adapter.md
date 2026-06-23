---
title: "POPIA Consent Dependency Adapter"
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

# POPIA Consent Dependency Adapter

## Purpose

`require_active_consent_for_current_user` centralizes POPIA active-consent
enforcement for learner-scoped routes.

Authorization and consent are separate gates:

| Gate | Question |
| --- | --- |
| Authorization | May this actor access this learner? |
| Consent | May this learner's data be processed right now? |

## Adapter

```python
await require_active_consent_for_current_user(db, current_user, learner_id)
```

This delegates to:

```python
ConsentService(db).require_active_consent(str(learner_id), actor_id=...)
```

## Verification

```bash
pytest -c pytest.ini tests/unit/test_consent_dependency_adapter.py -q --no-cov
```
