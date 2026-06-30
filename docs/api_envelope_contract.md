# API Envelope Contract

This document records the current V2 API envelope contract. It is evidence for
the envelope and error-contract helpers, not a claim that every production
router has completed response-envelope migration.

## Success Envelope

Successful responses use:

```json
{
  "data": {},
  "error": null,
  "meta": {
    "api_version": "v2",
    "request_id": "req_123",
    "pagination": null
  }
}
```

Implementation evidence:

- `app/domain/api_v2_models.py`
- `tests/unit/test_api_v2_envelope.py`

## Error Envelope

Handled errors use:

```json
{
  "data": null,
  "error": {
    "code": "forbidden",
    "message": "Human-readable message",
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

Implementation evidence:

- `app/core/exceptions.py`
- `docs/error_contract.md`
- `tests/unit/test_exception_envelopes.py`

## Pagination Envelope

Paginated responses use the same success envelope with `meta.pagination`:

```json
{
  "data": [],
  "error": null,
  "meta": {
    "api_version": "v2",
    "request_id": "req_123",
    "pagination": {
      "limit": 25,
      "offset": 0,
      "cursor": null,
      "next_cursor": "cursor_2",
      "total": 51,
      "has_more": true
    }
  }
}
```

## Router Rollout

The envelope helpers and global error handlers are implemented and tested.
Success-envelope migration across all routers remains a route-by-route rollout
task. Until a router has focused tests proving its response shape, leave that
router-specific TODO item unchecked.

## Aggregate Check

Run the aggregate contract check with:

```bash
make api-envelope-error-contract-check
```

## Verification Gaps

- Success envelopes have not been proven for every production router.
- A lint/test rule preventing raw production router dictionaries is still
  required.
- OpenAPI examples for all major request/response models remain a separate API
  documentation task.
