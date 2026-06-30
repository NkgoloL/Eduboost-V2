# Runtime Integration Boundary Policy

**Status:** active

## Blocked changes

- route registration
- schema migration
- audit repository deletion
- consent table merge
- public health write probe
- production DB mutation
- `alembic stamp head`

## Rule

A runtime integration PR must change one scoped path only and must include rollback notes and full test evidence.
