# Next Execution Queue After code_911_950

## Recommended next batch

`code_951_990`: migrate private auth lifecycle helper bodies into AuthApplicationService proper.

## Scope candidates

1. Move register implementation body into `AuthApplicationService.register`.
2. Move login implementation body into `AuthApplicationService.login`.
3. Move refresh implementation body into `AuthApplicationService.refresh`.
4. Move dev-session implementation body into `AuthApplicationService.create_dev_session`.
5. Add HTTP tests for realistic request/response payloads.
6. Delete private legacy helpers from `auth.py`.
