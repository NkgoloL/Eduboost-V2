# Next Execution Queue After DEPLOY-FE-RUNTIME-001 / code_2471_2510

## Recommended next batch

`AUTH-SERVICE-CLEANUP-001 / code_2511_2550` — remove auth service monkey-patching and move logout/revoke-all route logic into AuthApplicationService.

## Why

The audit still flags auth service monkey-patching/module-level method assignment and logout/revoke-all route logic in the router. This is a code-quality/runtime maintainability issue, not a release-evidence issue.
