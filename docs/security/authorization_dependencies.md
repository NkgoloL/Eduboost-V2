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
