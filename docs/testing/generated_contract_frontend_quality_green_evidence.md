# Generated Contract and Frontend Quality Green Evidence

**PRD:** `PRD-11.0R.RUNTIME-RESTORE.EXECUTION-4`
**Status:** Authority definition
**Last reviewed:** `2026-07-11T10:31:49.020030+00:00`

This contract turns the Execution-3 generated-contract/frontend-quality command plan into an evidence-producing green gate. It is intentionally stricter than a presence check: generated contracts and frontend quality become green only when independent command outputs report zero exit codes.

## Release-blocking gates

1. `openapi_regenerate` — regenerate `docs/openapi.json` from the canonical FastAPI app.
2. `route_inventory_regenerate` — regenerate `docs/route_inventory.md` from the canonical app.
3. `generated_contract_readonly_check` — rerun both generated-contract checks without mutation.
4. `frontend_release_quality` — run the frontend release-quality command.
5. `frontend_build_side_effect_check` — confirm frontend build/type artifacts did not leave tracked generated files dirty.

## Frontend quality policy

`quality:release` is error-blocking and command-backed. ESLint warnings remain visible advisory debt until the strict lint gate is deliberately made release-blocking. This prevents warning debt from hiding real errors while preserving the separate advisory/static gate for warning reduction.

## Green evidence rule

The capture script may be run in two modes:

- Without `--require-green`, it records command outputs and blockers.
- With `--require-green`, it fails unless every release-blocking gate is green.

Production-release handoff must use `--require-green` before generated contracts and frontend quality may be treated as green.
