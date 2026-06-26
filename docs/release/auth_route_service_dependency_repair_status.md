# Auth Route Service Dependency Repair Status

Generated at: `2026-06-24T11:29:46Z`
Commit: `f5d72b8380da6403371ea91f6c8298626ba07aa1`

**Status:** `auth-route-service-dependencies-passing`

| Function | Line | References auth_service | Has dependency param | Passed |
|---|---:|---:|---:|---:|
| `me` | 80 | False | False | True |
| `register` | 86 | True | True | True |
| `login` | 105 | True | True | True |
| `create_dev_session` | 123 | True | True | True |
| `refresh` | 147 | True | True | True |
| `list_sessions` | 178 | False | False | True |
| `logout` | 187 | True | True | True |
| `revoke_all_tokens` | 203 | True | True | True |

## Blockers

- None

## No false-closure rules

- F821-free route source does not prove HTTP auth behavior.
- Auth lifecycle HTTP proof remains separate.
- This repair does not approve beta release.
