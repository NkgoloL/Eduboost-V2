# PRD-11.0R.RUNTIME-RESTORE.EXECUTION-4 — Frontend Quality Defect Repair and Generated Contract Green Evidence

This slice repairs the execution path for generated-contract/frontend-quality evidence and makes the green state dependent on real command outputs.

## Scope

- Regenerate OpenAPI and route inventory from the canonical app.
- Re-run read-only generated-contract drift checks.
- Run frontend release quality through `quality:release`.
- Prevent frontend build/type side effects from silently dirtying tracked files.
- Keep release/billing/public-beta authorities locked.

## Boundary

This slice does not authorise production release, deployment, public beta, billing, or live payment processing.
