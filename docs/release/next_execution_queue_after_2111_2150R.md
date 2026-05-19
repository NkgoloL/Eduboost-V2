# Next Execution Queue After ROUTE-TX-POPIA-001R / code_2111_2150R

## Recommended next batch

`ROUTE-TX-POPIA-IMPL-001 / code_2151_2190` — implement the POPIA route transaction source repairs identified by the gap plan.

## Scope candidates

1. Read `docs/release/popia_route_transaction_gap_plan.md`.
2. Refactor the listed POPIA routes to delegate mutation work to service/application boundaries.
3. Remove any direct router-level DB mutation calls from those selected routes.
4. Add route-level negative tests for the refactored routes.
5. Keep live DB rollback proof separate from local source proof.
