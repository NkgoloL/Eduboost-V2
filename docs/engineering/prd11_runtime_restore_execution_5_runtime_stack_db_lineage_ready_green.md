# PRD-11.0R.RUNTIME-RESTORE.EXECUTION-5 — Runtime Stack, DB Lineage, Schema, and Ready Green Execution

This slice clears the runtime-stack side of the true-state baseline by requiring live proof for PostgreSQL, Redis, exact Alembic lineage, runtime schema, and `/ready`.

It does not authorise production release, deployment, billing, public beta, or live payment processing.

The authority branch records the required commands and fail-closed evidence path. The evidence branch must run the runtime green command with `--execute --apply-migrations --require-green` before capture.
