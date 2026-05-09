# Study Plan Authorization Wiring

## Endpoint

This slice starts Phase 2 write-path enforcement on:

```text
POST /api/v2/study-plans/{learner_id}
POST /api/v2/study-plans/generate/{learner_id}
```

## Policy Function

```python
require_learner_write_for_current_user(current_user, learner_id)
```

The authorization check runs before `enqueue_job(...)`, so unauthorized actors
cannot enqueue learner-scoped study-plan generation work.

## Claim-Based Scope

Unlike `GET /learners/{learner_id}`, this endpoint does not load a learner
object before enqueueing. Guardian/educator relationship scope therefore comes
from current-user claims or dependency overrides:

```text
guardian_learner_ids
educator_learner_ids
learner_ids
```

Admin/system actors remain globally authorized. Learner self-write is allowed
when `sub == learner_id`.

## HTTP Contract Coverage

| Scenario | Expected |
| --- | --- |
| Admin generates plan | 202 |
| Guardian with learner claim generates plan | 202 |
| Legacy `/generate/{learner_id}` alias | 202 |
| Learner self generates plan | 202 |
| Unrelated guardian generates plan | 403 |
| Missing auth | 401 |

## Verification

```bash
pytest -c pytest.ini   tests/unit/test_study_plan_authorization_wiring.py   tests/integration/test_study_plan_authorization.py   -q --no-cov
```
