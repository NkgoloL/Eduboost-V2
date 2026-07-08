# PRD-1.1 CI Inventory Authority

PRD-1.1 captures the baseline that later PRD-1 slices will use to converge CI and release gates.

## Inventory dimensions

The inventory records:

- GitHub workflow files under `.github/workflows`.
- Workflow references to `master`, `main`, `release/**`, release events, deployment/promotion language, pytest commands, and OpenAPI artifacts.
- Makefile targets and CI-related command references.
- Local documentation/configuration references to branch protection and required checks.
- Presence of `openapi.json` and `docs/openapi.json`.

## Boundary

PRD-1.1 does not change workflow semantics. It only records the current state so PRD-1.2 can classify checks and PRD-1.3 can canonicalise workflows under explicit authority.

Runtime KG implementation remains reserved for PRD-2.
