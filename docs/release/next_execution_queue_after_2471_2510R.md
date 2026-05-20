# Next Execution Queue After DEPLOY-FE-RUNTIME-001R / code_2471_2510R

## Recommended next batch

`AUTH-SERVICE-CLEANUP-001 / code_2511_2550` — remove auth service monkey-patching and move logout/revoke-all route logic into AuthApplicationService.

## Runtime deployment evidence remains separate

After this repair, runtime release proof still requires real frontend build/container/nginx/browser evidence.
