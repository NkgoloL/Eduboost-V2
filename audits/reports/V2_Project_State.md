# EduBoost V2 — Project State

**Status:** In Progress

## What exists now

The V2 project already includes:

- a dedicated API entrypoint (`app/api_v2.py`)
- dedicated V2 routers (`app/api_v2_routers/`)
- dedicated V2 services (`app/services/`)
- dedicated V2 repositories (`app/repositories/`)
- typed request models for V2 router inputs
- a V2 Docker runtime path (`docker-compose.v2.yml`, `docker/Dockerfile.v2`)
- MkDocs + mkdocstrings documentation setup
- mirrored tracking files and agent instructions for the V2 stream

## What is still incomplete

The project is **not yet fully V2-complete** because:

- some V2 services still need deeper, more native logic
- not all V2 services are fully repository-driven yet
- legacy runtime still exists as compatibility mode
- V2 is not yet the sole operational architecture
- CI/test coverage for V2 can still be improved

## Best current summary

The repository is now beyond the "idea" stage for V2. It contains a **real parallel V2 application**, but the migration is still in progress.
