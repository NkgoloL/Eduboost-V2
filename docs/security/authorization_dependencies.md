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
