# ADR-021: Backend Consolidation Must Be Evidence-First

## Status

Accepted

## Context

EduBoost V2 has identified backend consolidation risks across audit persistence, consent persistence/service paths, ORM-vs-database schema drift, and health/readiness diagnostics.

A previous consolidation proposal correctly named these risks, but direct deletion or table merging would be unsafe without call-site inventory, migration evidence, and release-owner decision records.

## Decision

Backend consolidation must proceed in this order:

1. Diagnostic inventory.
2. Compatibility adapter or normalizer, where required.
3. Runtime call-site migration.
4. Data-retention and migration decision record.
5. Full local and CI verification.
6. Deletion only after explicit approval.

## Consequences

- Legacy-looking audit/consent code may remain temporarily while inventories and adapters are introduced.
- Any table consolidation requires a separate ADR and migration evidence.
- `alembic stamp head` is not a repair action unless a written decision record explains why it is safe.
- Health/readiness hardening must not add unsafe public mutations.

## Release gates

Before backend consolidation can be considered complete:

- `make backend-consolidation-diagnostics-check` passes.
- `make audit-compatibility-check` passes.
- `make consent-compatibility-check` passes.
- `make backend-runtime-diagnostics-check` passes.
- `make backend-consolidation-report` generates a current report.
- `make backend-consolidation-release-guard` passes.
