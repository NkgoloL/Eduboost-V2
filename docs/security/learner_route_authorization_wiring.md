# Learner Route Authorization Wiring

## Pilot Endpoint

The first Phase 2 enforcement slice wires the shared object-authorization
policy into:

```text
app/api_v2_routers/learners.py::get_learner
GET /learners/{learner_id}
```

## Policy Function

```python
require_learner_read_for_current_user(current_user, learner)
```

This function adapts the existing JWT payload shape from
`app.core.security.get_current_user` into the Phase 2 `Actor` policy type, then
enforces learner-scoped read access.

## Current Mapping

| Existing token role | Phase 2 role | Scope source |
| --- | --- | --- |
| `admin` | `admin` | global admin scope |
| `parent` / `guardian` | `guardian` | `learner.guardian_id == current_user["sub"]` |
| `student` / `learner` | `learner` | `learner.id == current_user["sub"]` |
| `teacher` / `educator` | `educator` | optional `learner_ids` token payload |
| `support` | `support` | read-only support scope |
| `system` | `system` | system scope |

## Expected Results

| Actor | Expected |
| --- | --- |
| Admin | allow |
| Assigned guardian | allow |
| Learner self | allow |
| Unrelated guardian | deny 403 |
| Missing subject | deny 401 |
| Unknown role | deny 401 |

## Verification

```bash
pytest -c pytest.ini tests/unit/test_learner_route_authorization_wiring.py -q --no-cov
```

## Follow-Up

The next enforcement slice should add HTTP-level tests for the learner route
using FastAPI dependency overrides and a mocked learner repository/session.

## HTTP Contract Tests

- [`docs/security/learner_read_authorization_http_tests.md`](learner_read_authorization_http_tests.md)

## Mastery Route Wiring

- [`docs/security/learner_mastery_authorization_wiring.md`](learner_mastery_authorization_wiring.md)
