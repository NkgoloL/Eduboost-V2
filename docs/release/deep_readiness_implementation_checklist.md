# Deep Readiness Implementation Checklist

**Status:** pending implementation

## Required deep-readiness checks

| Check | Runtime behavior | Public-safe? |
|---|---|---|
| DB connectivity | read-only ping | yes |
| Alembic revision | read current/head information | yes |
| Required core tables | read-only table existence check | yes |
| Audit persistence | read-only capability check by default | yes |
| Consent persistence | read-only capability check by default | yes |
| Redis/cache | ping only | yes |
| Mutating audit write probe | internal/admin only, disabled by default | no |

## Guardrail

The lightweight health route must remain cheap. Deep readiness can be heavier, but it must not write to the DB on a public unauthenticated path.
