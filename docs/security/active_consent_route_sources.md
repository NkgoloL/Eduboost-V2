---
title: "Active Consent Route Sources"
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
