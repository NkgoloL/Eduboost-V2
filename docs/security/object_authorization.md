# Object-Level Authorization Baseline

## Purpose

Phase 2 starts by creating a shared object-authorization policy surface.

The goal is to prevent routers and services from implementing learner,
guardian, educator, support, or admin checks inconsistently.

## Module

```text
app/security/object_authorization.py
```

## Core Types

| Type | Purpose |
| --- | --- |
| `Role` | Normalized EduBoost actor role values |
| `Permission` | Canonical `read`, `write`, `delete`, and `admin` permissions |
| `OwnershipScope` | Why a user is allowed to access learner-scoped data |
| `Actor` | Normalized caller identity and scoped learner relationships |
| `AuthorizationDecision` | Structured allow/deny result |

## Policy Summary

| Actor scope | Read | Write | Delete/Admin |
| --- | --- | --- | --- |
| Admin | yes | yes | yes |
| System | yes | yes | yes |
| Learner self | yes | yes | no |
| Guardian assigned learner | yes | yes | no |
| Educator assigned learner | yes | yes | no |
| Support | yes | no | no |
| Unrelated actor | no | no | no |

## Usage Pattern

Routers and services should normalize the authenticated caller into an `Actor`
and then call:

```python
from app.security.object_authorization import Permission, require_learner_access

require_learner_access(actor, learner_id, Permission.READ)
```

For non-throwing checks:

```python
from app.security.object_authorization import Permission, can_access_learner

decision = can_access_learner(actor, learner_id, Permission.WRITE)
if not decision.allowed:
    ...
```

## Phase 2 Follow-Up

Later Phase 2 slices should wire this policy into:

- learner profile routes,
- guardian/parent routes,
- lesson and study-plan routes,
- diagnostics routes,
- jobs and async result routes,
- POPIA export/erasure routes.

## Verification

```bash
pytest -c pytest.ini tests/unit/test_object_authorization.py -q --no-cov
```

## Related Documents

- [`docs/security/authorization_dependencies.md`](authorization_dependencies.md)
