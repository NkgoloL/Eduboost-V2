# EduBoost V2 Error Contract

## Status

This document records the PR-002R error-envelope baseline.

## Canonical Shape

All handled API errors should use the canonical V2 envelope:

```json
{
  "data": null,
  "error": {
    "code": "not_found",
    "message": "Resource not found",
    "field_errors": [],
    "remediation": null,
    "details": {}
  },
  "meta": {
    "api_version": "v2",
    "request_id": "req_123",
    "pagination": null
  }
}
```

## Baseline Error Codes

| Code | Typical HTTP status | Meaning |
| --- | ---: | --- |
| `validation_error` | 422 | Request validation failed. |
| `unauthorized` | 401 | Authentication missing or invalid. |
| `forbidden` | 403 | Authenticated actor lacks permission. |
| `not_found` | 404 | Resource or route not found. |
| `conflict` | 409 | Duplicate or conflicting resource state. |
| `rate_limited` | 429 | Rate limit exceeded. |
| `consent_required` | 403 | Required consent is missing. |
| `consent_expired` | 403 | Existing consent has expired. |
| `dependency_unavailable` | 503 | External or internal dependency unavailable. |
| `internal_error` | 500 | Unhandled server error with safe message. |
| `popia_violation` | 451 | Operation would violate POPIA/legal constraints. |
| `http_error` | varies | Fallback for unmapped HTTP errors. |

## Security Rules

- Do not expose raw exception text from unhandled exceptions.
- Do not expose stack traces.
- Do not expose tokens, cookies, API keys, passwords, or secrets.
- Do not expose unnecessary learner or guardian PII.

## Evidence

- Implementation: `app/core/exceptions.py`
- Models/helpers: `app/domain/api_v2_models.py`
- Tests: `tests/unit/test_exception_envelopes.py`
