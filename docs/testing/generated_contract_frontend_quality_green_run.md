# Generated Contract and Frontend Quality Green Run Contract

**PRD:** `PRD-11.0R.RUNTIME-RESTORE.EXECUTION-3`
**Status:** Authority gate; green status requires captured independent command results.

This contract turns the PRD-11.0R generated-contract and frontend-quality work from a command-plan into an executable green-run path.

## Release-blocking gates

- OpenAPI regeneration from `app.api_v2:app`.
- Route inventory regeneration from `app.api_v2:app`.
- Read-only generated-contract drift check after regeneration.
- Frontend TypeScript check.
- Frontend ESLint check.
- Frontend Vitest run.
- Frontend production build.
- Combined frontend release-quality script.

## Evidence rule

A gate is green only when its command executes in the repository environment and exits with code `0`. File presence, governance records, PRD summaries, or command definitions cannot substitute for captured command output.

## Operational state

This slice may record the green-run execution contract and evidence, but it must keep release and live-traffic boundaries locked until the complete runtime baseline is green.
