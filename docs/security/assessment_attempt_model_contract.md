# Assessment Attempt Model Contract

## Purpose

`AssessmentAttemptRequest` and `AssessmentAttemptResponseItem` are centralized in:

```text
app/domain/api_v2_models.py
```

The assessment router imports the shared model directly. This replaces the
temporary local fallback used to keep the route importable while the missing
model was discovered.

## Verification

```bash
pytest -c pytest.ini tests/unit/test_assessment_attempt_model_contract.py -q --no-cov
```
