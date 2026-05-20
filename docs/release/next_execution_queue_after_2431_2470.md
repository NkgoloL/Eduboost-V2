# Next Execution Queue After DEPLOY-FE-001 / code_2431_2470

## Recommended next batch

`AUTH-SERVICE-CLEANUP-001 / code_2471_2510` — remove auth service monkey-patching and move logout/revoke-all route logic into AuthApplicationService.

## Why

The uploaded audit and repo snapshot still show auth lifecycle methods assigned onto `AuthApplicationService` at module scope and direct `logout` / `revoke_all_tokens` router logic.

## Boundary

This should be a code cleanup/proof batch, not release evidence.
