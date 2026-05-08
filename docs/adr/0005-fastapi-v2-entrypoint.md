# ADR 0005: FastAPI V2 Entrypoint

## Status
Accepted

## Context
The repository contains legacy and V2 API surfaces. Production deployment, OpenAPI generation, smoke tests, and CI need a stable application entrypoint to avoid ambiguity.

## Decision
`app.api_v2:app` is the canonical FastAPI V2 entrypoint. Legacy API modules may remain as compatibility shims while migration proceeds, but new runtime wiring and release evidence should target `app.api_v2:app`.

## Consequences

- **Pros**: Deterministic deployment target, simpler CI smoke checks, clearer OpenAPI provenance.
- **Cons**: Legacy import paths need compatibility discipline until fully retired.
