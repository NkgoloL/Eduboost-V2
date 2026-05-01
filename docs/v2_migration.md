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

## Next Steps
- migrate remaining legacy routes
- promote V2 runtime as default
- deprecate legacy runtime paths

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
