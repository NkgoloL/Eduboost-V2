# Auth Router Boundary Introspection

Generated at: `2026-05-19T22:55:57Z`

| Check | Value |
|---|---|
| Auth router exists | True |
| Auth runtime dependency imported | True |
| LearnerRepository symbol count | 0 |
| LearnerRepository constructor count | 0 |
| Direct `.get_by_guardian(` count | 0 |

## Functions

- `_canonical_access_claims` args=['user', 'existing_claims', 'extra']
- `_canonical_refresh_claims` args=['existing_claims', 'user']
- `_legacy_refresh_error_response` args=['message', 'status_code']
- `me` args=['current_user']
- `register` args=['request', 'body', 'response', 'db', 'auth_runtime', 'auth_service']
- `login` args=['request', 'body', 'response', 'db', 'auth_runtime', 'auth_service']
- `create_dev_session` args=['response', 'db', 'auth_runtime', 'auth_service']
- `refresh_token` args=['request', 'response', 'body', 'db', 'cookie_refresh', 'auth_runtime', 'auth_service']
- `_set_refresh_cookie` args=['response', 'token']
- `list_sessions` args=['current_user']
- `logout` args=['response', 'current_user', 'db', 'cookie_refresh']
- `revoke_all_tokens` args=['response', 'current_user', 'db', 'cookie_refresh']
