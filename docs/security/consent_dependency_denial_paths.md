---
title: "Consent Dependency Denial Paths"
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

# Consent Dependency Denial Paths

## Purpose

The centralized consent dependency must delegate denial behavior to
`ConsentService.require_active_consent` without swallowing or translating the
exception path.

## Contract

The adapter:

- resolves actor identity with `actor_id_from_current_user`
- delegates directly to `ConsentService(db).require_active_consent`
- does not catch `ConsentRequiredError`
- does not catch `ConsentExpiredError`
- preserves consent-service audit semantics for rejected access

## Verification

```bash
pytest -c pytest.ini tests/unit/test_consent_dependency_denial_paths.py -q --no-cov
```
