# EduBoost V2 Testing, CI, Coverage, Security, and Quality Gates

Maps backend and frontend test taxonomies, fixtures, E2E flows, coverage execution, static analysis, dependency and secret scans, required checks, and failure triage.

## Scope and ownership

This codemap is the primary architecture owner for:
- `tests`
- `app/frontend/__tests__`
- `app/frontend/src/__tests__`
- `pytest.ini`
- `playwright.config.ts`
- `.github/workflows`
- `scripts/coverage_suites`
- `scripts/advisory_suites`

It describes current implementation paths in repository-relative form. Related cross-cutting behaviour may be referenced from other codemaps, but every maintained source file has one primary owner in `codemap_coverage_manifest.json`.

## Architectural position

This area participates in the wider EduBoost request, data, evidence, and release architecture. Read it together with `00_application_bootstrap_and_request_lifecycle.md`, `17_testing_ci_coverage_security_and_quality_gates.md`, and `18_production_readiness_release_evidence_and_live_traffic.md` when changing runtime or release-critical behaviour.

## Trace ID: 1
**Title:** Backend pytest taxonomy, fixtures, integration, and E2E

**Description:** Follows pytest configuration through collection, fixture scopes, database isolation, markers, and behavioural suites.

**Motivation:**
The repository’s large test surface needs a clear taxonomy so fast feedback, product-critical flows, and infrastructure-heavy evidence are not conflated.

**Details:**

**Execution path**

1. Load pytest and coverage configuration.
2. Collect tests according to maintained taxonomy and markers.
3. Construct isolated database, Redis, provider, and app fixtures.
4. Run unit, contract, integration, or E2E behaviour.
5. Capture failures, timeouts, coverage, and artefacts.
6. Dispose state and publish machine-readable evidence.

**State and ownership boundaries**

Fixtures own test-local state; canonical dependency-complete runs prove real backend selection where required.

**Failure, privacy, and control points**

Tests do not depend on order, stubs are explicit, timeouts expose terminal leaves, and behavioural assertions replace implementation-only checks.

**Verification signals**

Run collection-only, focused unit, product-critical, integration, and seeded E2E commands from clean environments.

**Trace text diagram:**
```text
1. Load pytest and coverage configuration [1a]
   |
   v
2. Collect tests according to maintained taxonomy and markers [1b]
   |
   v
3. Construct isolated database, Redis, provider, and app fixtures [1c]
   |
   v
4. Run unit, contract, integration, or E2E behaviour [1d]
   |
   v
5. Capture failures, timeouts, coverage, and artefacts [1d]
   |
   v
6. Dispose state and publish machine-readable evidence [1d]
```

**Location ID: 1a**
- **Title:** Pytest configuration
- **Description:** Collection, markers, and timeout defaults.
- **Path:LineNumber:** pytest.ini:16

**Location ID: 1b**
- **Title:** Root fixtures
- **Description:** Shared test environment.
- **Path:LineNumber:** tests/conftest.py:15

**Location ID: 1c**
- **Title:** Integration fixtures
- **Description:** Integration runtime setup.
- **Path:LineNumber:** tests/integration/conftest.py:12

**Location ID: 1d**
- **Title:** Core CI workflow
- **Description:** Hosted backend verification.
- **Path:LineNumber:** .github/workflows/ci-core.yml:1

### AI Guide: Backend pytest taxonomy, fixtures, integration, and E2E

**Motivation:**
The repository’s large test surface needs a clear taxonomy so fast feedback, product-critical flows, and infrastructure-heavy evidence are not conflated.

**Details:**

**Reasoning through the execution path.** Start at [1a] and follow the ordered state transition rather than jumping directly to a downstream repository or generated artefact. The trace is designed to show which layer owns transport, orchestration, persistence, and evidence. [1a] anchors pytest configuration. [1b] anchors root fixtures. [1c] anchors integration fixtures. [1d] anchors core ci workflow.

**Safe change boundary.** Fixtures own test-local state; canonical dependency-complete runs prove real backend selection where required. A change that moves responsibility across these boundaries should update the owning codemap, tests, and any affected ADR or release verifier in the same change.

**Controls to preserve.** Tests do not depend on order, stubs are explicit, timeouts expose terminal leaves, and behavioural assertions replace implementation-only checks.

**How to verify the change.** Run collection-only, focused unit, product-critical, integration, and seeded E2E commands from clean environments. Use the cited locations as navigation anchors, then inspect call sites and tests before modifying behaviour.

## Trace ID: 2
**Title:** Frontend Vitest, routing contracts, Playwright, accessibility, and performance

**Description:** Maps component and client tests through browser-level journeys and frontend release checks.

**Motivation:**
Frontend correctness includes routing, accessibility, offline behaviour, generated contracts, and production build—not only component snapshots.

**Details:**

**Execution path**

1. Load Vitest and browser test setup.
2. Test API clients, route guards, components, and accessibility contracts.
3. Build the production Next.js application.
4. Start backend and frontend for Playwright.
5. Run seeded learner and parent journeys.
6. Capture browser, Lighthouse, and generated-contract evidence.

**State and ownership boundaries**

Mocked component state and seeded E2E state are separated; generated API types are reproducible artefacts.

**Failure, privacy, and control points**

Tests cover keyboard and screen-reader semantics, offline states, route authorization, and browser failures without relying on external live data.

**Verification signals**

Run pnpm test, production build, Playwright E2E, Lighthouse, and generated contract workflows.

**Trace text diagram:**
```text
1. Load Vitest and browser test setup [2a]
   |
   v
2. Test API clients, route guards, components, and accessibility contracts [2b]
   |
   v
3. Build the production Next.js application [2c]
   |
   v
4. Start backend and frontend for Playwright [2d]
   |
   v
5. Run seeded learner and parent journeys [2d]
   |
   v
6. Capture browser, Lighthouse, and generated-contract evidence [2d]
```

**Location ID: 2a**
- **Title:** Vitest configuration
- **Description:** Frontend unit and component test setup.
- **Path:LineNumber:** app/frontend/vitest.config.ts:3

**Location ID: 2b**
- **Title:** Playwright configuration
- **Description:** Browser E2E projects and servers.
- **Path:LineNumber:** playwright.config.ts:24

**Location ID: 2c**
- **Title:** Accessibility contracts
- **Description:** Frontend accessibility regression tests.
- **Path:LineNumber:** app/frontend/src/__tests__/AccessibilityContracts.test.tsx:1

**Location ID: 2d**
- **Title:** Frontend E2E workflow
- **Description:** Hosted browser journey gate.
- **Path:LineNumber:** .github/workflows/frontend-e2e.yml:1

### AI Guide: Frontend Vitest, routing contracts, Playwright, accessibility, and performance

**Motivation:**
Frontend correctness includes routing, accessibility, offline behaviour, generated contracts, and production build—not only component snapshots.

**Details:**

**Reasoning through the execution path.** Start at [2a] and follow the ordered state transition rather than jumping directly to a downstream repository or generated artefact. The trace is designed to show which layer owns transport, orchestration, persistence, and evidence. [2a] anchors vitest configuration. [2b] anchors playwright configuration. [2c] anchors accessibility contracts. [2d] anchors frontend e2e workflow.

**Safe change boundary.** Mocked component state and seeded E2E state are separated; generated API types are reproducible artefacts. A change that moves responsibility across these boundaries should update the owning codemap, tests, and any affected ADR or release verifier in the same change.

**Controls to preserve.** Tests cover keyboard and screen-reader semantics, offline states, route authorization, and browser failures without relying on external live data.

**How to verify the change.** Run pnpm test, production build, Playwright E2E, Lighthouse, and generated contract workflows. Use the cited locations as navigation anchors, then inspect call sites and tests before modifying behaviour.

## Trace ID: 3
**Title:** Coverage, lint, typing, security scans, and required-check convergence

**Description:** Shows advisory and required quality gates from command inventory through hosted CI evidence.

**Motivation:**
Coverage percentage alone is insufficient; production readiness requires converged execution of tests, Ruff, mypy, Bandit, dependency audits, secret scans, and frontend quality.

**Details:**

**Execution path**

1. Resolve canonical commands and dependency-complete environment.
2. Execute budgeted coverage and isolate terminal timeouts.
3. Run formatting, lint, typing, and static security checks.
4. Run Python and frontend dependency audits and secret scans.
5. Aggregate results into advisory or required gate evidence.
6. Block release when required checks are missing or red.

**State and ownership boundaries**

Gate evidence is tied to commit, command, environment, and artefact hashes.

**Failure, privacy, and control points**

Timeout leaves are attributed, suppressions are reviewed, generated files are handled consistently, and required-check names match branch protection.

**Verification signals**

Run coverage suite verifiers, advisory quality gates, dependency scan, secrets scan, and CI convergence authority checks.

**Trace text diagram:**
```text
1. Resolve canonical commands and dependency-complete environment [3a]
   |
   v
2. Execute budgeted coverage and isolate terminal timeouts [3b]
   |
   v
3. Run formatting, lint, typing, and static security checks [3c]
   |
   v
4. Run Python and frontend dependency audits and secret scans [3d]
   |
   v
5. Aggregate results into advisory or required gate evidence [3d]
   |
   v
6. Block release when required checks are missing or red [3d]
```

**Location ID: 3a**
- **Title:** Coverage contract
- **Description:** Coverage execution and evidence model.
- **Path:LineNumber:** scripts/coverage_suites/coverage_contract.py:34

**Location ID: 3b**
- **Title:** Terminal isolation
- **Description:** Timeout attribution and bounded reruns.
- **Path:LineNumber:** scripts/coverage_suites/budgeted_terminal_isolation.py:32

**Location ID: 3c**
- **Title:** Combined quality suite
- **Description:** Coverage, static, and security aggregation.
- **Path:LineNumber:** scripts/advisory_suites/coverage_static_security_green.py:52

**Location ID: 3d**
- **Title:** Dependency scan workflow
- **Description:** Hosted dependency audit gate.
- **Path:LineNumber:** .github/workflows/dependency-scan.yml:3

### AI Guide: Coverage, lint, typing, security scans, and required-check convergence

**Motivation:**
Coverage percentage alone is insufficient; production readiness requires converged execution of tests, Ruff, mypy, Bandit, dependency audits, secret scans, and frontend quality.

**Details:**

**Reasoning through the execution path.** Start at [3a] and follow the ordered state transition rather than jumping directly to a downstream repository or generated artefact. The trace is designed to show which layer owns transport, orchestration, persistence, and evidence. [3a] anchors coverage contract. [3b] anchors terminal isolation. [3c] anchors combined quality suite. [3d] anchors dependency scan workflow.

**Safe change boundary.** Gate evidence is tied to commit, command, environment, and artefact hashes. A change that moves responsibility across these boundaries should update the owning codemap, tests, and any affected ADR or release verifier in the same change.

**Controls to preserve.** Timeout leaves are attributed, suppressions are reviewed, generated files are handled consistently, and required-check names match branch protection.

**How to verify the change.** Run coverage suite verifiers, advisory quality gates, dependency scan, secrets scan, and CI convergence authority checks. Use the cited locations as navigation anchors, then inspect call sites and tests before modifying behaviour.

## Change checklist

- Update this codemap when an entry point, major dependency, persistence owner, or control flow changes.
- Keep all `Path:LineNumber` references repository-relative and line-valid.
- Update `codemap_coverage_manifest.json` when files move between architecture owners.
- Run `python scripts/maintenance/verify_codemaps.py --repo-root .` before merging.
