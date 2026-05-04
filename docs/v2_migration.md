# V2 Migration Guide

This page now serves mainly as a record of what changed during the cutover to
the V2 modular monolith.

## Goals
- move business logic into `app/services`
- isolate persistence in `app/repositories`
- keep domain entities in `app/domain`
- make `app/api_v2.py` the primary API surface
- phase out broker-first and task-queue-first architecture for the main product path

## Current V2 Capabilities
- learner reads
- auth/session issuance and refresh rotation
- diagnostics
- study plans
- parent reports
- append-only audit logging target
- quota enforcement and caching
- V2 service package boundary for routers/tests
- frontend API client defaulting to `/api/v2`
- single-command V2 compose stack including frontend, API, docs, Postgres, and Redis

## Completed Outcomes

- V2 is the default local runtime through `docker compose up --build`
- `app/api` is now a compatibility wrapper over `app/legacy`
- long-running tasks use `BackgroundTasks` plus Redis job polling
- requirements are split into base, dev, docs, and ml lockfiles
- frontend API contracts are fully TypeScript-checked
- MkDocs now covers the V2 package surface

## Current Route Migration Progress
- auth → V2 router package
- learner read → V2 router package
- diagnostics → V2 router package
- study plans → V2 router package
- parent reports → V2 router package
- audit feed → V2 router package

The following route families are now available in the V2 route surface:
- lessons
- gamification
- system
- assessments

The active compatibility boundary is now intentionally narrow:

- `app.api.main` import compatibility
- `POST /api/v1/lessons/generate` returning `410 Gone`
