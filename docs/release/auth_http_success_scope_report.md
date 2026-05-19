# Auth HTTP Success Scope Report

Generated at: `2026-05-19T18:43:57Z`

**Status:** controlled_dependency_override_success_scope_proof

## Proofs

- register success path through AuthApplicationService override
- login success path through AuthApplicationService override
- refresh success path preserving guardian_learner_ids through override
- duplicate register clean 409 failure
- wrong password clean 401 failure

## Auth lifecycle routes

| Path | Methods | Endpoint | Response model |
|---|---|---|---|
| `/api/v2/auth/register` | POST | `register` | `TokenResponse` |
| `/api/v2/auth/login` | POST | `login` | `TokenResponse` |
| `/api/v2/auth/dev-session` | POST | `create_dev_session` | `-` |
| `/api/v2/auth/refresh` | POST | `refresh_token` | `TokenResponse` |
| `/v2/auth/register` | POST | `register` | `TokenResponse` |
| `/v2/auth/login` | POST | `login` | `TokenResponse` |
| `/v2/auth/dev-session` | POST | `create_dev_session` | `-` |
| `/v2/auth/refresh` | POST | `refresh_token` | `TokenResponse` |
| `/__dev/slow_query` | GET | `dev_slow_query` | `-` |

## Boundary

This proof uses FastAPI dependency overrides. It verifies route registration, request validation compatibility, route-to-service delegation, clean failure handling, and refresh scope propagation. It does not prove real database persistence.
