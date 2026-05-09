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
