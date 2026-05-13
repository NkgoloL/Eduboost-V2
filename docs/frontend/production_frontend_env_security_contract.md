# Production Frontend Environment Security Contract

## Purpose

This contract defines the production-readiness boundary for browser-safe frontend environment variables.

## Required Controls

- Separate browser-safe environment variables from server-only secrets.
- Ensure no secrets are exposed through `NEXT_PUBLIC_*`.
- Add frontend env validation script to CI.
- Add safe public API URL configuration.
- Add typed environment schema.
- Add staging frontend env validation.
- Add production frontend env validation.
- Document frontend environment variables.

## Browser-Safe Public Variables

- `NEXT_PUBLIC_API_URL`
- `NEXT_PUBLIC_APP_ENV`
- `NEXT_PUBLIC_ENABLE_DEV_SESSION`

## Server-Only Secret Denylist

The frontend must not expose variables matching:

- `SECRET`
- `TOKEN`
- `KEY`
- `PASSWORD`
- `PRIVATE`
- `DATABASE_URL`
- `REDIS_URL`
- `STRIPE_SECRET`
- `SUPABASE_SERVICE_ROLE`

## Repository Evidence

- `app/frontend/src/lib/env.ts`
- `app/frontend/src/lib/productionReadiness/contracts.ts`
- `scripts/validate_frontend_env.py`
- `docs/frontend/frontend_e2e_environment_contract.md`
- `app/frontend/package.json`

## Verification

```bash
make frontend-production-readiness-check
```
