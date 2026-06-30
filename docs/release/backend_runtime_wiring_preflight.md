# Backend Runtime Wiring Preflight

**Status:** non-destructive preflight active

## Scope

This preflight checks whether the backend consolidation implementation seams are ready for future runtime wiring.

## Areas

| Area | Preflight |
|---|---|
| Audit | adapter-ready audit candidates can produce canonical payloads |
| Consent | consent runtime operation normalization and constructor probes are stable |
| Deep-readiness | public checks are read-only and unsafe probes are not public |
| Schema drift | real DB proof remains externally gated |

## Boundary

This preflight does not wire runtime routes, delete repositories, merge consent tables, mutate databases, or approve Alembic stamping.
