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
## Retired Compatibility Surface

The historical compatibility API and its dedicated tests were removed.

- app/api_v2.py is the only supported FastAPI entrypoint.
- V1 and legacy-prefixed routes are forbidden from the canonical runtime.
- Migration-era compatibility behavior is retained only where it is part of an active V2 module, not as a second API surface.
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
