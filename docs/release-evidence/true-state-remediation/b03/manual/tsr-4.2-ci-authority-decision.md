# TSR-4.2 CI Authority and Required-Check Decision

## Purpose
Define the exact single-source authority for GitHub Actions workflows, PR required status checks, and branch protection policies.

## Canonical Required Checks
Every pull request to `master` must pass the following canonical checks:
1. `Compile & Ruff Lint` (via `pr-core.yml`)
2. `Mypy Static Type Analysis` (via `pr-core.yml`)
3. `Fast Product Unit Tests` (via `pr-core.yml`)
4. `Route & OpenAPI Canonical Contract Audit` (via `pr-core.yml`)
5. `Disposable PostgreSQL & Redis Integration` (via `product-runtime.yml`)
6. `Alembic Migration Reversibility & Clean Down` (via `product-runtime.yml`)
7. `TypeScript Check & ESLint` (via `frontend-e2e.yml`)
8. `Next.js Production Build` (via `frontend-e2e.yml`)
9. `Bandit Python Security Scan` (via `security-supply-chain.yml`)
10. `Python pip-audit` (via `security-supply-chain.yml`)
11. `Frontend pnpm audit` (via `security-supply-chain.yml`)
12. `Detect-Secrets Baseline Scan` (via `security-supply-chain.yml`)

## Decision
Duplicate and conflicting workflow definitions are completely retired. All historical check definitions are mapped to these canonical 12 jobs in `docs/ci/ci_authority_matrix.json`.
