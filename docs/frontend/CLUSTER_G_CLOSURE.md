# Cluster G Frontend Vertical Journey Closure

## Scope

Cluster G establishes the frontend readiness evidence baseline for learner and
parent vertical journeys, consent/authorization denial UX, API client surfaces,
Playwright scaffolding, mocked API fixtures, accessibility checks, and opt-in
runtime browser workflow execution.

## Closure Commands

```bash
make frontend-route-inventory
make frontend-api-client-inventory
make frontend-runtime-inventory
make frontend-route-inventory-check
make frontend-api-client-inventory-check
make frontend-runtime-inventory-check
make frontend-journey-fixture-check
make frontend-mock-api-fixture-check
make frontend-playwright-scaffold-check
make frontend-playwright-specs-check
make frontend-playwright-mock-helper-check
make frontend-playwright-mocked-specs-check
make frontend-e2e-env-contract-check
make frontend-e2e-runtime-command-check
make frontend-build-test-lint-contract-check
make frontend-e2e-opt-in-workflow-check
make frontend-accessibility-contract-check
make frontend-accessibility-static-check
make learner-vertical-journey-contract-check
make parent-vertical-journey-contract-check
make frontend-auth-consent-denial-check
make cluster-g-frontend-check
make cluster-g-closure-check
```

## Closure Artifacts

- `docs/frontend/frontend_evidence_index.md`
- `docs/frontend/frontend_route_inventory.md`
- `docs/frontend/frontend_api_client_inventory.md`
- `docs/frontend/frontend_runtime_inventory.md`
- `docs/frontend/learner_vertical_journey_contract.md`
- `docs/frontend/parent_vertical_journey_contract.md`
- `docs/frontend/frontend_auth_consent_denial_contract.md`
- `docs/frontend/playwright_e2e_scaffold.md`
- `docs/frontend/playwright_mocked_journey_specs.md`
- `docs/frontend/frontend_accessibility_contract.md`
- `.github/workflows/cluster-g-frontend.yml`
- `.github/workflows/frontend-e2e-opt-in.yml`

## Closure Stamp

Cluster G is first-pass closed when `make cluster-g-closure-check` passes.

## Current Boundary

This closure includes CI-safe scaffold checks and opt-in runtime browser
execution. Full automatic E2E browser execution remains gated until the frontend runtime package and server command are canonical.

## Next Hardening Targets

1. Normalize frontend package scripts.
2. Run mocked Playwright tests automatically against a stable test server.
3. Add browser-level axe accessibility checks.
4. Add visual regression coverage for learner and parent journeys.
