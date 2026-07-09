# PRD-8.0-8.4 — Performance, Scale, and Cost Execution Foundation

Status: authority ready; evidence pending until captured from merged `master`.

This slice starts PRD-8 without adding another GitHub workflow file. It creates a deterministic runtime readiness contract for performance, scale, and cost execution.

## Scope

- API and learner-journey load-test readiness.
- Runtime KG query-performance readiness.
- Database/index review readiness.
- LLM cost simulation and cost-guardrail readiness.
- Queue/backpressure and capacity-plan readiness.
- Frontend performance-budget readiness.

## Boundary

This slice does not run production load tests, modify infrastructure, enable live learner traffic, authorise billing, authorise deployment, authorise release tags, or authorise production release. PRD-9 implementation remains unauthorised until PRD-8 closes and hands off.
