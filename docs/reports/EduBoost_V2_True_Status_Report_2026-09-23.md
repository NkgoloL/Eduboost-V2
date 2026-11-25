# EduBoost V2 — True Status Technical Report

**Audit date:** 2026-09-23  
**Repository snapshot:** branch master, commit ff0e09bc7c96e1effad822a45448e4b8a99e8c55  
**Latest commit at audit time:** 2026-09-22, feat(lev): PRD-4A Longitudinal Educational Validation fast-track implementation (#574)  
**Status:** substantial, active software implementation; current release and production operation are not established by this checkout or this audit.

## 1. Scope and method

This report describes what is present and what could be demonstrated in the WSL checkout on 2026-09-23. Repository documentation, roadmaps, and evidence registers were treated as claims to check, not as proof of implementation. Primary evidence was source code, ORM models and migrations, tests and results, build configuration, Git history, CI workflow definitions, generated contract checks, and local container state.

The checkout had one pre-existing working-tree edit at the start of the audit: .agent.md. It was not modified. Audit commands regenerated tracked artifacts; because those paths were unchanged at audit start, those generated changes were restored. At report creation, the only pre-existing modification remained .agent.md.

The audit covered application architecture and runtime entrypoints; backend service/domain/router structure; frontend source and toolchain; database migration lineage; educational validation; test and static-check configuration; CI and deployment workflows; and local runtime availability. It executed the repository fast unit suite, the LEV-focused unit suite, and selected local static/build checks.

This is a repository audit, not a penetration test or independent education-science evaluation. I did not use production credentials, access a hosted staging or production environment, or query a live learner database. CI workflow definitions were inspected, but hosted CI run results for this exact commit were not available. Postgres integration/migration tests were not run against the local database because the available container was not a verified disposable test database.

## 2. Executive summary

EduBoost V2 is a sizeable FastAPI modular-monolith backend with a substantial Next.js frontend, extensive service and domain packages, a large automated test corpus, and deployment and operations assets. It is no longer accurately described by a July 3 snapshot. Git history contains **950 commits** between the last commit before July 4 and this snapshot. The raw diff over that interval touches 4,916 files and reports about 1.09 million insertions and 302 thousand deletions; this includes generated documentation, archived evidence and historical snapshots, so it must not be interpreted as application-code growth.

The current codebase has a broad product surface: authentication and authorization, learner and parent journeys, lessons and practice, diagnostics, tutoring, billing/commercial readiness, consent and data-subject operations, curriculum and content governance, content generation/review, observability, and release-readiness controls. The API entrypoint imports successfully, OpenAPI drift checking passes, and Alembic currently resolves to one head. This is meaningful engineering progress.

Current local quality evidence is mixed:

- The configured backend fast unit selection completed with **5,283 passed, 19 failed, 28 skipped, and 1 xpassed**. Eighteen failures are concentrated in content-factory route tests whose assertions expect business fields at the top level of successful JSON responses; one provider test also fails. These failures must be resolved or explicitly reconciled with the canonical response contract before this suite can be treated as green.
- Ruff, Python compilation, test-import integrity, OpenAPI drift, runtime entrypoint checking, the LEV task-register verifier, and static coverage-threshold alignment passed.
- Mypy reports **four errors across two files**. The current route-inventory check also fails: it reports 459 committed route entries and 915 generated entries, while the live app-entrypoint checker reports 455 registered routes.
- The backend coverage policy is configured for 90% line coverage with branch coverage and is internally aligned across the Makefile/CI contract. This audit did not produce a fresh measured coverage report; the fast suite used the no-coverage target and failed.
- Frontend TypeScript checking and the frontend unit suite passed locally; the suite reported 149 tests in 44 files. The production build also completed. But the installed frontend dependencies are behind the versions declared in app/frontend/package.json: local Next.js is 16.2.11 versus declared 16.3.3, local ESLint is 8.57.0 versus declared ESLint 9, and local eslint-config-next is 15.5.18 versus declared 16.3.3. Consequently, frontend lint failed while loading the config module. The successful build and tests are evidence for the installed dependency tree, not a clean verification of the declared locked toolchain.
- The latest Longitudinal Educational Validation (LEV) work adds substantial statistical and traceability code and passes its focused **67-test** suite. It is not yet connected to the runtime API or an observed learner-event path. Its schema defaults an omitted consent state to consented, and the “append-only” property is not enforced by a database trigger or repository guard in the inspected code. This is an integration and data-governance boundary, not a validated live educational measurement system.
- The repository contains CI definitions for database integration, migration reversibility, security and supply-chain checks, but no deployment workflow was found among the six current workflows. The frontend Playwright workflow uses --dry-run and suppresses errors with || echo, so it does not provide evidence that the learner/parent journeys actually ran.
- At inspection time, docker ps showed a single Supabase Postgres container in “health: starting” state, with no EduBoost API or Redis container listed. docker compose ps could not render the default Compose configuration because required environment values were missing, including GRAFANA_ADMIN_PASSWORD. The current full-stack runtime and database migration state therefore remain unverified.

**Overall assessment:** this is an actively developed, broad pre-release product codebase with real implemented capabilities and substantial verification infrastructure. It is not supportable to describe the current snapshot as fully green, empirically validated for live learner use, or production-deployed based on the evidence available here.

## 3. Current-state snapshot

| Area | Verified state at audit time |
|---|---|
| Git | master at ff0e09bc; latest commit dated 2026-09-22; pre-existing .agent.md edit |
| Backend entrypoint | app.api_v2:app imports; runtime entrypoint checker reports 455 routes |
| API contract | scripts/generate_openapi.py --check passes |
| Route inventory artifact | Check fails: 459 committed entries versus 915 generated |
| Database migration graph | 53 tracked migration-version Python files; alembic heads reports one head, 20260922_1600_educational_validation_traceability |
| Backend tests | 5,283 passed; 19 failed; 28 skipped; 1 xpassed in make test-fast |
| LEV-focused tests | 67 passed; three Pydantic protected-namespace warnings |
| Type and lint | Ruff passes; Mypy fails with four errors |
| Frontend | TypeScript passes; 149 Vitest tests pass; Next build completes on a mismatched local install; ESLint cannot load config |
| Coverage | 90% line / branch policy is configured and contract-aligned; no fresh successful measured report established in this audit |
| LEV task register | Integrity check passes with 222 tasks, no errors or warnings |
| Runtime stack | One Postgres container was visible and still starting; no app or Redis container listed |
| Deployment status | Deployment assets exist; no live deployment or successful hosted release evidence was verified |

Tracked-source inventory is approximately 485 backend Python files, 1,361 Python test files, 1,163 Python scripts, 2,224 Markdown files under docs/, 218 TypeScript/TSX files under the frontend source tree, 53 migration-version files, and six GitHub workflow YAML files. Documentation and tooling are an unusually large share of the repository; counts include generated and archival material.

## 4. Application architecture and implemented product surface

### 4.1 Backend and API

app/api_v2.py is the FastAPI application entrypoint. The source describes the backend as a strict modular monolith rather than a microservice deployment. It assembles routers, middleware, exception handling, health checks, request IDs, structured logging, timing, rate limiting, API deprecation behavior, security headers, CORS, and Prometheus metrics. Startup validates JWT keyring configuration and starts consent-expiry work; production configuration can also start the Key Vault rotation loop.

The API router and module tree contain functional areas for authentication, learners, lessons, practice, diagnostics, study plans, tutor interactions, parents, consent and privacy operations, billing/commercial readiness, content factory and review, curriculum expansion, IRT quality, jobs, observability, performance/cost, controlled beta, and release readiness. The runtime entrypoint check verifies the import and reports 455 routes. This is a source-level import/registration check, not proof that each route is backed by a healthy external dependency or has passed a live request journey.

The OpenAPI generation check passed. The separate route-inventory check failed. This inconsistency means the API contract artifact and the route-inventory artifact do not currently provide a unified, passing account of registered routes. It should be resolved before treating repository route inventories as canonical.

### 4.2 Learner-facing frontend

The frontend is a Next.js App Router application. The local production build generated 24 static pages and listed learner, parent, diagnostic, lesson, plan, auth, privacy-settings, admin content-factory, and roadmap routes. Dynamic server-rendered routes are also present. Frontend unit coverage includes auth/client APIs, learner journeys, diagnostic flows, tutor safety, parent-review permissions and redaction, offline synchronization, content-factory clients, accessibility contracts, and Grade R phonics/earcon components.

TypeScript passed, and Vitest reported 44 passing files and 149 passing tests. React emitted act(...) warnings in interactive component tests.

The local install is materially out of sync with the manifest. Frontend lint failed before linting because its ESLint configuration attempted to load eslint-config-next/core-web-vitals, unavailable in the installed older package layout. The build succeeded under Next 16.2.11, not declared Next 16.3.3. A clean pnpm install --frozen-lockfile CI run is needed before claiming the manifest toolchain is healthy.

The build log said Serwist was disabled. The source config makes service-worker generation conditional, so this audit establishes that the tested build did not demonstrate a service worker; it does not establish whether that setting is intentional for deployment. If offline/PWA behavior is a release requirement, verify the deployment build with the required setting and inspect the generated worker.

### 4.3 Educational services and content pipeline

The backend contains dedicated packages for content generation and safety, curriculum, ETL, LLM providers, semantic retrieval, runtime knowledge-graph behavior, and the new educational validation services. The API and admin surfaces support content scopes, generation runs, review/approval workflow, coverage and staging checks, and production-promotion controls. The frontend also includes admin content-factory screens.

The existence of these packages demonstrates implementation breadth, but production promotion, real provider configuration, curriculum evidence quality, and live learner outcomes are not established by a successful local unit suite alone. The 18 content-factory fast-suite failures deserve attention because they occur in production-gate, promotion, review-queue, health/status, and scope route tests.

### 4.4 Authentication, privacy, and safety

The app entrypoint validates the JWT keyring at import and configures security headers, rate limiting, CORS, request logging, and private-network restrictions for metrics access. The source tree includes role and authorization logic, consent services, POPIA/data-subject request services, audit persistence, privacy operations, tutor scope/safety controls, and content safety components.

These are real software controls in the repository, but their presence does not establish legal compliance or safe production operation. This audit did not process real consent records, attempt cross-tenant access against a deployed service, exercise erasure/export against a live database, inspect cloud key-vault configuration, or independently verify backup restoration. Such claims require runtime and organizational evidence.

### 4.5 Database and deployment assets

SQLAlchemy models and Alembic migrations are present, and the Alembic graph resolves to a single head. The latest migration creates the new LEV traceability schema. The product-runtime.yml workflow is configured to start disposable Postgres/Redis services, upgrade to head, run selected integration tests, and test one-step downgrade/re-upgrade behavior.

Those database-backed CI steps were not run locally in this audit. The local docker compose ps invocation failed before listing services because required configuration was missing. A direct container listing showed a Supabase Postgres container in startup health state, but no EduBoost API or Redis container. No migration was applied to that container.

The repository includes Docker Compose files, Bicep templates, Kubernetes manifests, Render configuration, Prometheus/Alertmanager/Grafana assets, and operations workflows. These are deployment inputs and operational scaffolding. No checked workflow deployed the application, and no live endpoint or hosted deployment was verified. The operations workflow is a backup/restore dry-run drill, not evidence of a completed production restore.

## 5. Longitudinal Educational Validation (latest implementation)

The latest commit introduces a substantial LEV package under app/services/educational_validation/, along with typed schemas, ORM models, a repository, a traceability service, a migration, tests, and task-register evidence.

The code implements methods for:

- calibration metrics including expected calibration error, Brier score, and Cronbach alpha;
- classification-risk estimates and Wilson confidence intervals;
- population-stability-index drift checks and item-parameter drift;
- subgroup fairness metrics and Mantel–Haenszel differential-item-functioning analysis;
- clustered-RCT/ANCOVA and difference-in-differences impact evaluation;
- multi-model retention-curve fitting;
- transfer evaluation and transfer matrices;
- learner interaction safety classification;
- mastery-state reasonableness checks and assistance discounting;
- confidence-bounded use authorization; and
- SHA-256 canonical state hashing and persistence of interactions, mastery transitions, and validation-run records.

The focused suite at tests/unit/educational_validation passed: **67 passed**. The LEV task-register verifier also passed with 222 tasks and no warnings. These checks support that the package is syntactically integrated and its isolated behavior is exercised.

### 5.1 Runtime integration is incomplete

A repository-wide source search found no API router or runtime service invoking EducationalTraceabilityService. The new feature is not registered as an HTTP capability, and no production entrypoint for learner-event ingestion was found. The package currently behaves as an internal library with persistence primitives, not an end-to-end learner validation product flow. It cannot yet be described as monitoring real learner outcomes from the application’s normal request lifecycle.

### 5.2 Consent and empirical-evidence boundary

InteractionEventSchema defaults consent_state to "consented"; evidence_type defaults to "synthetic_fixture". The traceability service accepts a schema and persists it but does not itself call the consent service or reject a non-consented state. Because the module has no runtime call site today, this is a future integration hazard rather than evidence of current live learner data being ingested. Before connecting real learners, consent must be checked at the authoritative boundary and omission must fail closed.

The synthetic default is useful, but statistical method implementation is not empirical validation. No empirical field cohort, approved protocol execution, or production model-calibration run was demonstrated in this audit. Results from synthetic fixtures must remain clearly separated from claims about educational impact or learner safety.

### 5.3 Traceability integrity is weaker than “append-only” implies

The state transition method computes a canonical SHA-256 hash and stores it alongside the transition. That is useful for detecting a changed payload if independently recomputed. In the inspected repository/migration, however, there is no LEV-specific database trigger or repository guard rejecting update/delete operations, no hash-chain linkage to a preceding transition, and no signature or external witness. The repository exposes insert/read methods, but the database model remains updateable through ordinary SQLAlchemy/database access. Thus “append-only” is currently an application convention and “cryptographic traceability” is a stored payload fingerprint, not tamper-proof event storage.

Before relying on this log as regulatory, safety, or scientific evidence, enforce immutability at the database permissions/trigger boundary, specify key and canonicalization policy, verify hashes during reads/audits, and test tampering and retention behavior.

## 6. Verification performed

| Check | Result | Interpretation |
|---|---|---|
| python3 -m compileall -q app tests scripts alembic | Pass | Python source compiles |
| ruff check app tests scripts | Pass | Configured Ruff rules pass on these trees |
| scripts/audit_test_imports.py | Pass | Test imports resolve against current code |
| scripts/generate_openapi.py --check | Pass | Generated OpenAPI artifact matches generation |
| scripts/check_runtime_entrypoints.py | Pass | app.api_v2:app imports; checker reports 455 routes |
| scripts/generate_route_inventory.py --check | **Fail** | 459 committed entries versus 915 generated entries |
| python3 -m mypy app | **Fail** | Four errors in two files (details below) |
| scripts/educational_validation/verify_lev_task_register.py --repo-root . --json | Pass | Valid; 222 tasks; no errors/warnings |
| scripts/coverage_suites/verify_coverage_contract.py --threshold-only | Pass | 90% threshold and branch-coverage settings align statically |
| make test-fast | **Fail** | 5,283 passed, 19 failed, 28 skipped, 1 xpassed; 283.94 seconds |
| pytest tests/unit/educational_validation -q | Pass | 67 passed; three Pydantic warnings |
| Frontend pnpm run type-check | Pass | TypeScript check succeeds under installed packages |
| Frontend pnpm run test | Pass | 44 files, 149 tests |
| Frontend pnpm run lint:release | **Could not lint** | Installed ESLint/config versions are older than declared; config import fails |
| Frontend pnpm run build | Pass with qualification | Build succeeds under installed Next 16.2.11; manifest declares 16.3.3; Serwist disabled |

The coverage result above validates threshold configuration only. It is not a measured coverage result. The checked-in local .coverage file predates this snapshot and was not treated as evidence for current coverage.

### 6.1 Backend fast-suite failure detail

Eighteen of the 19 failures are in content-factory route tests. The requests returned HTTP 200, then assertions raised KeyError when looking for fields such as scope_id, status, total, or passed directly in the JSON root. This pattern is consistent with an envelope/consumer assertion mismatch, but the audit does not assume which side is authoritative: the failing tests and the current envelope contract need to be reconciled explicitly. One remaining failure is test_json_completion_groq_and_anthropic_providers in tests/unit/services/test_curriculum_and_llm_burndown_complete_batch417.py.

The run emitted 199 warnings, including Pydantic protected-namespace warnings, un-awaited AsyncMock coroutine warnings in learner-tutor test paths, and short-HMAC-key warnings from token test fixtures. Some may be test-fixture artifacts, but they obscure actionable warnings and should be triaged.

### 6.2 Mypy failures

python3 -m mypy app checked 485 source files and reported:

- app/services/auth_lifecycle_impl.py:198: Any | None supplied where str is required;
- app/services/learner_service.py:25: repository union lacks get_by_guardian;
- app/services/learner_service.py:28: missing db argument when calling BaseRepository.create; and
- app/services/learner_service.py:176: repository union lacks update_archetype.

The PR workflow includes this exact Mypy check, so this is a concrete local failure of a configured quality gate.

## 7. CI and release-evidence assessment

The six checked workflows cover PR core quality, product/runtime integration, frontend quality/E2E, security/supply-chain scans, operations drills, and manual release-evidence generation. The PR core workflow enforces compile/Ruff/import checks, full test collection, Mypy, a coverage run at 90%, OpenAPI and route inventory, entrypoint checks, documentation/readiness consistency, and LEV task integrity.

The local audit reproduced passing and failing parts of those checks. Route-inventory and Mypy checks fail locally, and the local fast-suite selection has 19 failures. The 90% coverage policy is present, but this audit has no new passing measured coverage artifact. Hosted check status for commit ff0e09bc was not queried.

The product-runtime workflow configures disposable Postgres/Redis integration and Alembic upgrade/downgrade checks. That is the correct kind of CI structure for database verification, but its presence does not prove the job passed on this commit.

The frontend workflow installs with a frozen lockfile, but its Playwright commands use --dry-run and || echo. Those steps can report success even when the Playwright command fails, and a dry run does not exercise a real user journey. The frontend unit suite does run in its frontend-quality job, but the current E2E workflow should not be presented as runtime E2E evidence.

The release-evidence workflow is manually dispatched and generates SBOMs and route/OpenAPI/CI authority inventories. No deployment command or deployment workflow was found in the checked workflow set. The presence of Azure, Kubernetes, Render, and Compose assets shows deployment options are prepared in source; it does not establish that any environment is currently deployed, authorized, or healthy.

## 8. Principal risks

| Priority | Finding | Why it matters |
|---|---|---|
| High | Backend fast unit selection has 19 failures | A configured product-quality gate is not green in this local run; failures cover content-factory API behavior and one provider path. |
| High | Mypy gate has four errors | The exact static-analysis command in PR CI fails locally. |
| High | Route inventory is inconsistent with runtime and committed artifact | API route authority cannot be inferred consistently from the checked generated files. |
| High before real LEV data | LEV schema defaults missing consent to consented; service has no consent integration | Integrating this ingestion path without a fail-closed consent check could treat omitted consent state as permission. |
| High before evidence use | LEV append-only storage is not enforced in the migration/repository | Hash storage alone does not prevent or reliably evidence privileged updates/deletes. |
| High | Playwright CI steps are dry-run/non-gating | Workflow success does not prove learner/parent flows execute against a running application. |
| Medium | Frontend local dependencies do not match the manifest | Local lint fails at configuration load; successful build/test runs do not verify the declared toolchain versions. |
| Medium | No current full-stack health or migration run was demonstrated | Only a Postgres container was visible and it was still starting; required Compose configuration was absent. |
| Medium | No empirical LEV validation is established | Statistical code and synthetic tests do not establish outcomes, fairness, or safety on field data. |
| Medium | 199 test warnings, including async mock and weak test-key warnings | Noise can hide real runtime issues and test fixtures can overstate token-security behavior. |
| Medium | No live release/deployment state was verified | Deployment files and evidence generators do not substitute for hosted health, approvals, or production telemetry. |

## 9. Recommended work, in order

1. **Restore a green backend gate.** Reconcile the 18 content-factory assertions with the canonical API envelope contract, resolve the provider test failure, rerun the same unit selection and then the coverage-enabled CI target, and publish a fresh measured coverage report.
2. **Fix Mypy and route inventory drift.** Resolve the four type errors. Regenerate or repair route inventory generation so committed, generated, and runtime route authorities agree; retain the passing OpenAPI check as a separate contract.
3. **Make frontend verification reproducible.** In a clean environment install the checked-in frontend lockfile with frozen mode, then run lint, type-check, tests, and production build at the declared versions. Decide whether Serwist should be enabled for the deployment profile and verify the resulting worker when offline/PWA support is required.
4. **Make end-to-end CI execute journeys.** Replace Playwright dry runs and swallowed failures with real test execution against a disposable API/frontend stack or explicitly label the job as a syntax/harness check and add a separate gating E2E job.
5. **Harden LEV before ingestion.** Require explicit consent proof, bind learner pseudonyms to a controlled privacy-preserving identity scheme, reject non-consented or unspecified events at the service boundary, enforce immutable persistence at the database layer, and add tamper/retention/access-control tests.
6. **Separate implementation from validation evidence.** Keep synthetic fixtures clearly marked; define approved empirical cohorts and analysis protocols; record actual input manifests and execution results; and do not describe LEV metrics as field-validated until real evidence is reviewed.
7. **Verify database and deployment behavior in controlled environments.** Run Alembic upgrade/downgrade against disposable PostgreSQL, execute the defined product-runtime integration suite, complete backup/restore drills, and collect current readiness, observability, security, approval, and release-authority evidence from the intended hosted environment.
8. **Triage test warnings and token fixtures.** Replace weak test-only JWT keys with compliant fixtures where practical, await async mock calls correctly, and remove noisy React/Pydantic warnings when they represent real misuse.
9. **Refresh the current-state report after gates settle.** Re-run this inventory after the above changes; keep historical reports dated and clearly scoped so old results are not treated as current.

## 10. Conclusion

Since the July 3 report, the repository has undergone a very large amount of engineering work. The current source contains extensive learner/product functionality, quality and release controls, and a new longitudinal validation subsystem. The latest feature is genuinely implemented at the service/model/test level; it is not yet a runtime-integrated or empirically validated learner-outcomes capability.

This snapshot should be classified as **active pre-release development with meaningful implemented functionality and several unresolved verification gates**. The most immediate blockers are the backend unit failures, Mypy errors, route-inventory mismatch, frontend toolchain mismatch, and non-executing Playwright job. Production readiness remains unverified because the full runtime stack and hosted release state were not demonstrated in this audit.
