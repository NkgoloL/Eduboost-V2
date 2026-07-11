# Runtime Stack, Database Lineage, Schema, and `/ready` Green Evidence

**PRD:** PRD-11.0R.RUNTIME-RESTORE.EXECUTION-5

This contract converts runtime readiness from planning evidence into live command-backed proof.
A green capture requires a disposable or controlled runtime stack with PostgreSQL, Redis, API, worker, and frontend available.

## Release-blocking gates

- `compose_contract` — committed stack contract includes PostgreSQL, Redis, API, worker, and frontend.
- `alembic_upgrade_head` — migrations are applied with the current repository Python interpreter against the disposable database.
- `disposable_stack_schema_lineage_live` — live Alembic revision equals the single repository head and critical runtime tables/columns exist.
- `redis_readiness` — configured Redis responds to `PING`.
- `ready_http_probe` — the API `/ready` endpoint returns HTTP 200.

Presence-only evidence is forbidden. A capture with `--require-green` fails unless all gates are green.
