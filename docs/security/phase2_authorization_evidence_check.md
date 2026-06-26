---
title: "Phase 2 Authorization Evidence Check"
status: current-evidence
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

# Phase 2 Authorization Evidence Check

## Purpose

This check consolidates the Phase 2 authorization evidence created so far.

It verifies that the authorization policy, dependency adapter, enforced pilot
routes, HTTP tests, and documentation are present and wired.

## Command

```bash
make phase2-authz-check
```

Equivalent direct command:

```bash
python3 scripts/check_phase2_authorization_evidence.py
```

## Current Endpoint Coverage

| Area | Endpoint |
| --- | --- |
| Ether onboarding questions auth boundary | `docs/security/ether_onboarding_questions_auth_boundary.md` |
| Consent renewal admin boundary | `docs/security/consent_renewal_admin_auth_boundary.md` |
| Dev-session environment gate | `docs/security/dev_session_environment_gate.md` |
| Phase 2 closure stamp | `docs/security/PHASE2_AUTHORIZATION_CLOSURE.md` |
| Phase 2 final closure check | `make phase2-authz-closure` |
| Phase 2 closure report | `docs/security/PHASE2_AUTHORIZATION_CLOSURE.md` |
| Learner authorization CI | `.github/workflows/learner-authz-coverage.yml` |
| Learner authorization coverage guard | `make learner-authz-check` |
| Learner authorization matrix | `docs/security/learner_authz_matrix.md` |
| Phase 2 router import smoke | `tests/unit/test_phase2_router_import_smoke.py` |
| Assessment attempt model contract | `app/domain/api_v2_models.py` |
| Onboarding questions auth boundary | `GET /api/v2/onboarding/questions` |
| Assessment list auth boundary | `GET /api/v2/assessments` |
| Onboarding write | `POST /api/v2/onboarding/submit`, `POST /api/v2/onboarding/archetype` |
| Assessment attempt write | `POST /api/v2/assessments/{assessment_id}/attempt` |
| Lesson stream write | `POST /api/v2/lessons/generate/stream` |
| Gamification award XP write | `POST /api/v2/gamification/award-xp` |
| Learner read | `GET /api/v2/learners/{learner_id}` |
| Learner mastery | `GET /api/v2/learners/{learner_id}/mastery` |
| Study plan write | `POST /api/v2/study-plans/{learner_id}` |
| Lesson generation write | `POST /api/v2/lessons/generate` |
| Diagnostic items read | `GET /api/v2/diagnostics/items/{learner_id}` |
| Diagnostic submit write | `POST /api/v2/diagnostics/submit` |
| POPIA data export read | `GET /api/v2/popia/data-export/{learner_id}` |
| Parent progress read | `GET /api/v2/parents/learners/{learner_id}/progress` |
| POPIA deletion request write | `POST /api/v2/popia/deletion-request/{learner_id}` |
| POPIA deletion cancel write | `POST /api/v2/popia/deletion-cancel/{learner_id}` |

## Non-Goal

This check does not claim all Phase 2 authorization work is complete. It is an
evidence gate for the endpoints already migrated.
