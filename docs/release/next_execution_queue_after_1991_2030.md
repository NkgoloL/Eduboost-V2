# Next Execution Queue After APPROVAL-EVID-001 / code_1991_2030

## Recommended next batch

`ROUTE-TX-IMPL-001 / code_2031_2070` — production transaction route wiring implementation plan.

## Scope candidates

1. Use `tx_route_wiring_inventory.md` to select the first safe route group.
2. Wire route handlers through transactional application services where already proven.
3. Add route-level negative tests for rollback behavior.
4. Keep live database proof separate from local unit proof.
