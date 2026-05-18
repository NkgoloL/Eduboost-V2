# Auth Lifecycle Extraction Report

Generated at: `2026-05-18T16:23:45Z`

| Method | Delegated through AuthApplicationService |
|---|---:|
| `register` | True |
| `login` | True |
| `refresh` | True |
| `create_dev_session` | True |

## Preserved legacy helpers

- `_auth_lifecycle_legacy_create_dev_session_impl`
- `_auth_lifecycle_legacy_login_impl`
- `_auth_lifecycle_legacy_refresh_impl`
- `_auth_lifecycle_legacy_register_impl`

## Remaining debt

- Move preserved private helpers into `AuthApplicationService` proper.
- Add HTTP request/response tests using dependency overrides and realistic payloads.
