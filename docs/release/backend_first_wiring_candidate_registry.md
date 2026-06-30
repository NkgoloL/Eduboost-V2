# Backend First Wiring Candidate Registry

**Status:** candidate registry active

## Scope

The registry identifies the first non-destructive candidates that can be used for adapter-backed runtime wiring tests.

## Boundary

- No production database writes.
- No route registration changes.
- No repository deletion.
- No consent table merge.
- No Alembic stamp/baseline.
