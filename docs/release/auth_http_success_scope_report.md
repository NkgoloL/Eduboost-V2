# Auth HTTP Success Scope Report

Generated at: `2026-09-02T21:18:23Z`

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
| `/__dev/slow_query` | GET | `dev_slow_query` | `-` |

## Boundary

This proof uses FastAPI dependency overrides. It verifies route registration, request validation compatibility, route-to-service delegation, clean failure handling, and refresh scope propagation. It does not prove real database persistence.
