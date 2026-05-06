# V2 Migration Guide

This page is the migration ledger for EduBoost SA. It explains what has
actually moved to the V2 surface, what compatibility code still exists, and
which cleanup steps remain.

## What V2 Means Here

In the current repository state:

- `app/api_v2.py` is the active FastAPI entrypoint for new work.
- `app/api_v2_routers/`, `app/services/`, `app/repositories/`, `app/core/`,
  and `app/modules/` hold the main V2 implementation path.
- `docker compose up --build` starts the V2-oriented local stack.
- The frontend defaults to the V2 API surface.

## What Still Exists for Compatibility

The migration is far enough along that V2 is the default development path, but
not so complete that every historical surface has vanished.

The repository still keeps:

- [`app/api/main.py`](/app/api/main.py) as a compatibility import shim
- archived legacy runtime code under [`app/legacy`](/app/legacy/DEPRECATED.md)
- a narrow set of migration-era compatibility behaviors instead of a total
  hard delete of every old path

That means the repository should be described as "V2-first with compatibility
shims", not as "every legacy artifact has been erased from history."

## Current Verified V2 Behaviors

- auth and role-aware access control live in the V2 runtime
- learner, diagnostics, study-plan, lesson, parent, consent, and system route
  families exist in the V2 surface
- long-running actions use FastAPI background work plus Redis-backed job status
- Redis supports cache, token revocation, and job polling
- sensitive audit events are written through the append-only PostgreSQL audit
  repository
- dependency locks are split into base, dev, docs, and ml groups

## Compose and Environment Mapping

- `docker-compose.yml` - default local development stack
- `docker-compose.v2.yml` - explicit V2 stack variant
- `docker-compose.aca.yml` - Azure Container Apps-oriented setup
- `docker-compose.prod.yml` - production-like compose workflow

Use the root Compose file unless you are intentionally targeting one of the
specialized environments above.

## Remaining Migration Work

The migration is not "done forever." The main follow-up items are:

- retire the remaining compatibility-only legacy surface on schedule
- keep the docs aligned with the actual security/runtime behavior
- keep release automation and production-promotion steps verified against the
  current repo layout
- keep public and internal audit narratives synchronized

See [`docs/project_status.md`](/docs/project_status.md) and the root
[`TODO.md`](/TODO.md) for the live tracking view.
