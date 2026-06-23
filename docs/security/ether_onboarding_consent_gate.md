---
title: "Ether Onboarding Consent Boundary"
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

# Ether Onboarding Consent Boundary

## Route

```text
POST /api/v2/ether/onboarding/submit
```

## Decision

```text
authenticated_catalog_boundary
```

## Rationale

`ether.py::submit_onboarding` accepts `OnboardingResponse`, which carries
classification content but no `learner_id`. Because the route has no learner
record subject, it cannot correctly call an active-consent check.

The route remains authenticated and role-gated. Learner-record onboarding writes
are covered separately by the canonical onboarding router.

## Verification

```bash
pytest -c pytest.ini tests/unit/test_ether_onboarding_consent_gate_wiring.py -q --no-cov
make popia-consent-boundary-check
```
