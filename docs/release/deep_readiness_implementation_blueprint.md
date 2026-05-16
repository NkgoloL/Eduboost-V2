# Deep Readiness Implementation Blueprint

**Status:** implementation blueprint ready; route wiring still pending

## Allowed public deep-readiness checks

- database connectivity read-only probe
- Alembic revision read-only probe
- required table presence read-only probe
- audit persistence read-only capability probe
- consent persistence read-only capability probe

## Blocked checks

- public mutating audit write probe
- public database write/readback probe
- any health route operation requiring destructive permissions

## Runtime wiring rule

The first deep-readiness runtime implementation must be read-only and must not change public liveness semantics.
