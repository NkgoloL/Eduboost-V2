# Assessment Attempt Authorization Wiring

## Endpoint

```text
POST /api/v2/assessments/{assessment_id}/attempt
```

## Policy Function

```python
require_learner_write_for_current_user(current_user, request.learner_id)
```

Submitting an assessment attempt creates learner-owned assessment state, so it is
treated as a write-sensitive learner operation.

## Verification

```bash
pytest -c pytest.ini tests/unit/test_assessment_attempt_authorization_wiring.py -q --no-cov
```

## Compatibility Note

`assessments.py` now keeps a local fallback `AssessmentAttemptRequest` model when the shared API model is unavailable, preserving router importability while the shared model surface is reconciled.
