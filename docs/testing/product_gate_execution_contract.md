# Product Gate Execution and Critical Flow Repair Contract

**PRD:** PRD-11.0R.RUNTIME-RESTORE-4
**Status:** Authority / evidence gate for product critical-flow execution discipline.

This contract turns the PRD-11.0R product/runtime gate taxonomy into a critical-flow execution plan.  It is intentionally stricter than presence checks: every product flow must produce independent command output for positive and negative behaviour before it can support release evidence.

## Release-blocking product flows

- Auth and object authorisation.
- POPIA lifecycle.
- Billing and commercial subscription flow.
- Learner and guardian journeys.
- Diagnostics and assessments.
- Audit trail capture.

## Evidence rule

A flow is not green because a file, route, model, or governance record exists.  It is green only when command output shows the expected positive behaviour and at least one denial/failure behaviour.

## Runtime dependency rule

Product evidence captured against a database-backed path must record the runtime context: database, Redis, exact Alembic head, schema contract and `/ready` state.

## Operational hold

PRD-11.0R.RUNTIME-RESTORE-4 does not authorise production release, public beta, live billing, or operationally safe live learner traffic.  It keeps the PRD-11.0R operational hold active until the product and runtime gates are independently green.
