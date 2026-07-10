# PRD-11.0R.RUNTIME-RESTORE-1 — Runtime Stack, DB Lineage, and Readiness Restoration

**Status:** Authority recorded
**Scope:** Restore fail-closed runtime-readiness evidence for the stack, Alembic lineage, critical schema, Redis, and `/ready` before PRD-11 release evidence can continue.

## Purpose

This corrective slice responds to the true-state finding that readiness could report success while Redis was absent, the live database revision was unknown to the repository, and critical ORM tables/IRT columns were missing. The slice turns those findings into release-blocking runtime checks.

## Installed controls

- Repository Alembic head is discovered from migration files instead of hard-coded release notes.
- Live `alembic_version` must match the single repository head exactly.
- Unknown revisions, split revisions, missing revision rows, and `base`-only rows fail readiness.
- Critical runtime tables and columns are checked through a read-only schema contract.
- IRT diagnostic columns and runtime-KG tables are explicit release-blockers.
- Redis and HTTP `/ready` are explicit runtime baseline hard gates.
- `docker-compose.yml` must still define the disposable stack services: Postgres, Redis, API, worker, and frontend.
- PRD evidence capture records the actual runtime baseline status without converting blocked/missing infrastructure into green release evidence.

## Boundary

This slice does not authorise production release, deployment, release tags, public beta, billing launch, or live payment processing. It preserves the controlled-beta operational hold until the runtime baseline is green.

## Next step

After evidence capture, the next authorised corrective item is `PRD-11.0R.RUNTIME-RESTORE-2`.
