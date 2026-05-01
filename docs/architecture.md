# Architecture

## Current state

The repository currently contains a legacy runtime and a V2 migration stream.

## V2 target

EduBoost V2 follows a strict modular monolith shape:

- `app/core` for runtime primitives
- `app/domain` for entities and API schemas
- `app/repositories` for persistence access
- `app/services` for business logic
- `app/api_v2.py` for the new lean API surface

## Replaced-or-superseded target assumptions

The V2 direction aims to supersede:

- broker-first audit/event architecture
- Celery-first async orchestration
- RabbitMQ-first operational assumptions
- inference microservice dependence for the main product path
- multi-compose / multi-topology complexity for the default runtime

## Migration principle

The migration is incremental. Working legacy systems remain in place until equivalent V2 slices exist. The new `docker-compose.v2.yml` and `docker/Dockerfile.v2` define the preferred single-node baseline for V2 development.

## Router split

The project now has a clear split:

- `app/api/routers/*` → legacy compatibility surface
- `app/api_v2_routers/*` → active V2 route surface

New route work should land in the V2 router package first.
