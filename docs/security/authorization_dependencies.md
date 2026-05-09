# Authorization Dependency Adapter

## Purpose

`app/security/dependencies.py` adapts request-level authentication context into
the Phase 2 object-authorization policy surface.

This slice does not enforce authorization on production routes yet. It creates
a tested adapter that later route wiring can call consistently.

## Headers Used by the Adapter

| Header | Purpose |
| --- | --- |
| `X-EduBoost-Subject-Id` | Authenticated actor subject id |
| `X-EduBoost-Roles` | Comma-separated role list |
| `X-EduBoost-Learner-Ids` | Learner ids owned by the learner actor |
| `X-EduBoost-Guardian-Learner-Ids` | Learner ids assigned to a guardian |
| `X-EduBoost-Educator-Learner-Ids` | Learner ids assigned to an educator |

These headers are a local contract/testing adapter. Production authentication
can later resolve the same `Actor` object from JWT claims, sessions, or database
lookups without changing object-authorization policy semantics.

## Functions

| Function | Purpose |
| --- | --- |
| `build_actor_from_headers(...)` | Converts raw header values to an `Actor` |
| `get_authorization_actor(...)` | FastAPI dependency for current actor |
| `raise_for_learner_access(...)` | Generic learner access enforcement |
| `require_learner_read(...)` | Read access helper |
| `require_learner_write(...)` | Write access helper |
| `require_learner_delete(...)` | Delete access helper |

## Router Wiring Pattern

```python
from fastapi import Depends

from app.security.dependencies import get_authorization_actor, require_learner_read
from app.security.object_authorization import Actor

async def get_learner_profile(
    learner_id: str,
    actor: Actor = Depends(get_authorization_actor),
):
    require_learner_read(actor, learner_id)
    ...
```

## Verification

```bash
pytest -c pytest.ini tests/unit/test_security_dependencies.py -q --no-cov
```

## Follow-Up

The next Phase 2 slice should wire this dependency into one learner-scoped
read route and add positive/negative HTTP contract tests.

## Learner Route Inspection

Run:

```bash
python3 scripts/inspect_learner_routes.py
```

Review `docs/security/learner_route_authorization_inspection.md` before wiring the first route.

## Enforcement Wiring

- [`docs/security/learner_route_authorization_wiring.md`](learner_route_authorization_wiring.md)

## Write-Path Wiring

- [`docs/security/study_plan_authorization_wiring.md`](study_plan_authorization_wiring.md)

## Lesson Generation Authorization

- [`docs/security/lesson_generation_authorization_wiring.md`](lesson_generation_authorization_wiring.md)

## Diagnostic Items Authorization

- [`docs/security/diagnostic_items_authorization_wiring.md`](diagnostic_items_authorization_wiring.md)

## Diagnostic Submit Authorization

- [`docs/security/diagnostic_submit_authorization_wiring.md`](diagnostic_submit_authorization_wiring.md)

## POPIA Data Export Authorization

- [`docs/security/popia_data_export_authorization_wiring.md`](popia_data_export_authorization_wiring.md)

## Parent Progress Authorization

- [`docs/security/parent_progress_authorization_wiring.md`](parent_progress_authorization_wiring.md)

## POPIA Deletion Request Authorization

- [`docs/security/popia_deletion_request_authorization_wiring.md`](popia_deletion_request_authorization_wiring.md)

## POPIA Deletion Cancel Authorization

- [`docs/security/popia_deletion_cancel_authorization_wiring.md`](popia_deletion_cancel_authorization_wiring.md)

## POPIA Correction Request Authorization

- [`docs/security/popia_correction_request_authorization_wiring.md`](popia_correction_request_authorization_wiring.md)

## POPIA Restriction Request Authorization

- [`docs/security/popia_restriction_request_authorization_wiring.md`](popia_restriction_request_authorization_wiring.md)

## POPIA Deletion Status Authorization

- [`docs/security/popia_deletion_status_authorization_wiring.md`](popia_deletion_status_authorization_wiring.md)

## Parent Erasure Authorization

- [`docs/security/parent_erasure_authorization_wiring.md`](parent_erasure_authorization_wiring.md)

## POPIA Deletion Execute Authorization

- [`docs/security/popia_deletion_execute_authorization_wiring.md`](popia_deletion_execute_authorization_wiring.md)

## Parent Export Authorization

- [`docs/security/parent_export_authorization_wiring.md`](parent_export_authorization_wiring.md)

## Consent Status Authorization

- [`docs/security/consent_status_authorization_wiring.md`](consent_status_authorization_wiring.md)

## Parent Trust Dashboard Authorization

- [`docs/security/parent_trust_dashboard_authorization_wiring.md`](parent_trust_dashboard_authorization_wiring.md)

## Parent Dashboard Authorization

- [`docs/security/parent_dashboard_authorization_wiring.md`](parent_dashboard_authorization_wiring.md)

## Consent Grant Authorization

- [`docs/security/consent_grant_authorization_wiring.md`](consent_grant_authorization_wiring.md)

## Consent Revoke Authorization

- [`docs/security/consent_revoke_authorization_wiring.md`](consent_revoke_authorization_wiring.md)

## Gamification Profile Authorization

- [`docs/security/gamification_profile_authorization_wiring.md`](gamification_profile_authorization_wiring.md)

## Gamification Award XP Authorization

- [`docs/security/gamification_award_xp_authorization_wiring.md`](gamification_award_xp_authorization_wiring.md)

## Lesson Stream Authorization

- [`docs/security/lesson_stream_authorization_wiring.md`](lesson_stream_authorization_wiring.md)

## Assessment Attempt Authorization

- [`docs/security/assessment_attempt_authorization_wiring.md`](assessment_attempt_authorization_wiring.md)

## Onboarding Authorization

- [`docs/security/onboarding_authorization_wiring.md`](onboarding_authorization_wiring.md)

## Assessment List Authentication Boundary

- [`docs/security/assessment_list_auth_boundary.md`](assessment_list_auth_boundary.md)

## Onboarding Questions Authentication Boundary

- [`docs/security/onboarding_questions_auth_boundary.md`](onboarding_questions_auth_boundary.md)

## Assessment Attempt Model Contract

- [`docs/security/assessment_attempt_model_contract.md`](assessment_attempt_model_contract.md)

## Phase 2 Router Import Smoke

- [`docs/security/phase2_router_import_smoke.md`](phase2_router_import_smoke.md)

## Learner Authorization Matrix

- [`docs/security/learner_authz_matrix.md`](learner_authz_matrix.md)

## Learner Authorization Coverage Check

- [`docs/security/learner_authz_coverage_check.md`](learner_authz_coverage_check.md)

## Learner Authorization Coverage CI

- [`docs/security/learner_authz_ci.md`](learner_authz_ci.md)

## Phase 2 Authorization Closure Report

- [`docs/security/PHASE2_AUTHORIZATION_CLOSURE.md`](PHASE2_AUTHORIZATION_CLOSURE.md)

## Phase 2 Authorization Closure Check

- [`docs/security/phase2_authorization_closure_check.md`](phase2_authorization_closure_check.md)

## Dev Session Environment Gate

- [`docs/security/dev_session_environment_gate.md`](dev_session_environment_gate.md)

## Consent Renewal Admin Authorization Boundary

- [`docs/security/consent_renewal_admin_auth_boundary.md`](consent_renewal_admin_auth_boundary.md)

## Ether Onboarding Questions Authentication Boundary

- [`docs/security/ether_onboarding_questions_auth_boundary.md`](ether_onboarding_questions_auth_boundary.md)
