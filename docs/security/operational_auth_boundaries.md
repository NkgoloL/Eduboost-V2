---
title: "Operational Auth Boundaries"
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

# Operational Auth Boundaries

## Purpose

This evidence document aggregates the non-learner-object operational routes
that were reviewed after Phase 2 learner-object authorization closure.

## Boundaries

| Route | Boundary |
| --- | --- |
| `POST /api/v2/auth/dev-session` | non-production only, hidden with production `404` |
| `POST /api/v2/admin/consent/trigger-renewal-reminders` | admin auth via `Depends(require_admin)` |
| `GET /api/v2/ether/onboarding/questions` | authenticated user via `Depends(get_current_user)` |

## Verification

```bash
pytest -c pytest.ini tests/unit/test_operational_auth_boundaries.py -q --no-cov
make learner-authz-check
make phase2-authz-closure
```
