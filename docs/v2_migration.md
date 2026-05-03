# V2 Migration Guide

This page tracks the migration from the legacy EduBoost runtime to the new V2 modular-monolith architecture.

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

## Next Steps
- verify V2 import/tests in Python 3.11
- reconcile remaining service/repository contract mismatches found by tests
- continue promoting V2 runtime as default
- document any legacy runtime paths that reappear in future checkouts

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

Remaining work is now less about missing route families and more about deepening the implementations, reducing legacy dependencies, and making V2 the sole operational architecture.

## 2026-05-02 Stabilisation Notes

The V2 tree had several consolidation mismatches: `app/services` was referenced but absent, Alembic pointed at legacy model imports, and the frontend defaulted to `/api/v1`. These have been corrected in the working tree. Local verification is constrained by the available Windows Python 3.13 environment; the project should be verified in Python 3.11 as declared by CI and `.python-version`.
