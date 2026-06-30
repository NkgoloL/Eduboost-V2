# Backend Runtime Wiring Fixture Contract

**Status:** fixture-backed wiring tests active

## Scope

This contract defines deterministic fixture cases for the first runtime wiring phase.

## Fixture groups

| Group | Fixture |
|---|---|
| Audit runtime wiring | `tests/fixtures/backend_consolidation/audit_runtime_wiring_cases.json` |
| Consent runtime wiring | `tests/fixtures/backend_consolidation/consent_runtime_wiring_cases.json` |
| Deep-readiness route wiring | `tests/fixtures/backend_consolidation/deep_readiness_route_wiring_cases.json` |

## Boundary

The fixtures prove wiring payloads and readiness catalogue behaviour. They do not wire production routes, delete repositories, merge tables, stamp Alembic, or mutate databases.
