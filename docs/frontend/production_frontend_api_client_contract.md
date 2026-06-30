# Production Frontend API Client Contract

## Purpose

This contract defines production behavior for the typed frontend API client that consumes the canonical PR-002R backend envelope.

## Required API Client Controls

- Update typed API client to consume canonical PR-002R envelope.
- Normalize error handling against canonical error envelope.
- Add auth token handling.
- Add refresh handling.
- Add request ID propagation.
- Add typed response parsing.
- Add typed error parsing.
- Add retry behavior for safe idempotent requests.
- Add network-offline detection.
- Add stale-data handling.
- Add API client tests.

## Canonical Envelope Contract

The client must support:

- `data`
- `error`
- `meta`
- `request_id`
- normalized validation field errors
- user-safe 401, 403, 429, 503, and 504 messages

## Repository Evidence

- `app/frontend/src/lib/api/client.ts`
- `app/frontend/src/lib/api/types.ts`
- `app/frontend/src/lib/api/offlineSync.ts`
- `app/frontend/src/lib/productionReadiness/contracts.ts`
- `app/frontend/src/__tests__/ApiLayer.test.ts`
- `docs/frontend/frontend_api_client_inventory.md`

## Verification

```bash
make frontend-production-readiness-check
```
