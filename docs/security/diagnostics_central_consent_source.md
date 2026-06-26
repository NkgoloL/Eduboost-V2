---
title: "Diagnostics Central Consent Source"
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

# Diagnostics Central Consent Source

## Purpose

Diagnostics routes must use the centralized active-consent adapter and must not
call `ConsentService(db).require_active_consent` directly.

## Covered Routes

```text
GET /api/v2/diagnostics/items/{learner_id}
POST /api/v2/diagnostics/submit
```

## Verification

```bash
pytest -c pytest.ini tests/unit/test_diagnostics_central_consent_source.py -q --no-cov
make popia-consent-source-check
```
