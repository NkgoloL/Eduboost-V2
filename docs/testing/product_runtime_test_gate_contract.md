# Product and Runtime Test Gate Contract

**PRD:** `PRD-11.0R.RUNTIME-RESTORE-3`
**Status:** authority recorded; evidence pending
**Purpose:** convert PRD-11.1R taxonomy into release-blocking product/runtime gates.

This contract forbids using PRD records, generated manifests, route presence, file
presence, or constant readiness payloads as product/runtime release proof.

## Product test domains

- Services
- Routes
- Database contracts
- Auth and object authorisation
- POPIA lifecycle
- Billing/commercial flows
- Learner/guardian journeys
- Diagnostics and assessments

Each product domain requires independent command output plus at least one
negative/denial/failure-path proof.

## Runtime test domains

- Postgres
- Redis
- Migrations
- Schema contract
- `/ready`
- Worker
- Frontend proxy

Each runtime domain requires command output from the disposable stack or an
explicit blocked status. Runtime baseline remains red until these commands prove
healthy stack behaviour.

## Release rule

Production-release evidence remains blocked until product/runtime gate outputs
are captured and the runtime baseline is green. Governance evidence may support
traceability, but it cannot substitute for product/runtime behaviour.
