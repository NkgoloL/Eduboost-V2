# Next Execution Queue After ROUTE-TX-IMPL-001 / code_2031_2070

## Recommended next batch

`ROUTE-TX-AUTH-001 / code_2071_2110` — first production route transaction wiring slice for auth routes.

## Scope candidates

1. Select the highest-priority auth mutation routes from `route_transaction_implementation_plan.md`.
2. Wire them through transactional application services where the service is already isolated-rollback proven.
3. Add route-level negative tests with injected service failures.
4. Do not claim live database proof until it is actually executed.
