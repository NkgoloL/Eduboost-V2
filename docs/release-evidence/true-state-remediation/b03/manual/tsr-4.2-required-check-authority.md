# TSR-4.2 Required-Check Authority

## Canonical Required Check Mapping
Every branch protection check maps to one canonical job:
1. `pr-core` -> lint, typecheck, unit-fast, route-check, openapi-check
2. `product-runtime` -> integration, migrations, live db tests
3. `frontend-e2e` -> type-check, lint, unit, build, playwright
4. `security-supply-chain` -> bandit, pip-audit, pnpm audit, secret scan

## Review Metadata
- **Reviewer**: Nkgolo Lebelo (Lead Engineer, Self-Review)
- **Decision**: `completed`
- **Conflict Disclosure**: Self-review by sole developer; not independent approval.
