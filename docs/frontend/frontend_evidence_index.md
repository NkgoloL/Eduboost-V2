# Frontend Evidence Index

## Cluster G Closure

- `docs/frontend/CLUSTER_G_CLOSURE.md`
- `scripts/check_cluster_g_closure.py`
- `.github/workflows/cluster-g-frontend.yml`
- `.github/workflows/frontend-e2e-opt-in.yml`

## Journey Contracts

- `docs/frontend/learner_vertical_journey_contract.md`
- `docs/frontend/parent_vertical_journey_contract.md`
- `docs/frontend/frontend_auth_consent_denial_contract.md`

## Inventories

- `docs/frontend/frontend_route_inventory.md`
- `docs/frontend/frontend_api_client_inventory.md`
- `docs/frontend/frontend_runtime_inventory.md`

## Playwright Evidence

- `docs/frontend/playwright_e2e_scaffold.md`
- `docs/frontend/playwright_vertical_journey_specs.md`
- `docs/frontend/playwright_journey_fixture_contract.md`
- `docs/frontend/playwright_mock_api_fixtures.md`
- `docs/frontend/playwright_mock_route_helpers.md`
- `docs/frontend/playwright_mocked_journey_specs.md`
- `docs/frontend/frontend_e2e_environment_contract.md`
- `docs/frontend/frontend_e2e_runtime_commands.md`
- `docs/frontend/frontend_e2e_opt_in_workflow.md`

## Accessibility and Quality

- `docs/frontend/frontend_accessibility_contract.md`
- `docs/frontend/frontend_accessibility_static_scan.md`
- `docs/frontend/frontend_build_test_lint_contract.md`

## Required Commands

```bash
make frontend-route-inventory
make frontend-api-client-inventory
make frontend-runtime-inventory
make cluster-g-frontend-check
make cluster-g-closure-check
```
