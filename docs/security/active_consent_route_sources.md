---
title: "Active Consent Route Sources"
status: active
owner: security
reviewers: [security, engineering, privacy]
audience: security-reviewer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: '2026-09-23'
review_interval_days: 90
evidence_command: 'PYTHON=.venv/bin/python make popia-consent-source-check'
code_anchors: [app/api_v2_routers/learners.py, tests/unit/test_active_consent_route_sources.py]
---
# Active Consent Route Sources

## Purpose

All active-consent route boundaries should use the centralized consent adapter:

```python
require_active_consent_for_current_user
```

Routes should not call `ConsentService(db).require_active_consent` directly,
because centralization preserves consistent actor attribution and evidence
semantics.

## Command

```bash
make popia-consent-source-check
```

## Verification

```bash
pytest -c pytest.ini tests/unit/test_active_consent_route_sources.py -q --no-cov
```
