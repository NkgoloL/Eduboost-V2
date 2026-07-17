# EduBoost V2 — Comprehensive True-State Technical Report

**Assessment date:** 13 July 2026  
**Reviewed artifact:** `Eduboost-V2-master(31)(4).zip`  
**Extracted snapshot digest:** `a059d4134b8dc99e10db4fb98a19cba933fc3baacaeb7471a86c4a8c1101e9e2`  
**Declared application version:** `1.0.0-rc1`  
**Assessment posture:** Independent static and executable review of the supplied ZIP, supplemented by the repository's committed evidence records.

---

## 1. Executive conclusion

EduBoost V2 is an **advanced pre-production educational platform**, not an early prototype. It has a substantial FastAPI backend, a real Next.js frontend, a broad PostgreSQL schema, an implemented runtime knowledge-graph layer, learner and parent journeys, diagnostics/IRT, content generation and review, POPIA controls, billing scaffolding, operational monitoring, and an unusually extensive evidence-driven governance system.

The project is nevertheless **not production-release ready**. Its own current authority records correctly keep production release, deployment, release tagging, public beta, live payment processing, and billing launch unauthorised. The immediate release blocker is PRD-11 Runtime Restore Execution-7: coverage, Ruff, mypy, Bandit, Python and frontend dependency audit, and secret-baseline review have not all produced green, independently captured evidence.

The most accurate one-line description is:

> **EduBoost is functionally broad and operationally promising, with green critical product/runtime paths, but it remains under a justified operational hold because whole-repository quality and security assurance have not converged.**

### Overall engineering score: **6.7 / 10**

| Dimension | Score | True-state assessment |
|---|---:|---|
| Product implementation | 8.0 | Major learner, guardian, curriculum, diagnostic, lesson, study-plan, gamification, content-factory and KG capabilities exist. |
| Architecture | 7.0 | Strong modular-monolith direction and boundaries, weakened by oversized services, exceptions, compatibility layers and duplicated paths. |
| Data and persistence | 7.8 | Mature PostgreSQL/Alembic model and a single migration head; schema is large and operationally complex. |
| Testing | 7.0 | Thousands of tests and meaningful product/runtime evidence; full coverage baseline and canonical test convergence are still incomplete. |
| Security and privacy | 6.6 | Strong design controls and POPIA coverage; release-blocking SAST, dependency and secret gates remain red/unproven. |
| Frontend | 6.8 | Strict TypeScript, tests, E2E and green recorded quality; dependency alignment needs correction and fresh audit proof. |
| DevOps and operability | 6.5 | Health/readiness, metrics, Docker, CI and observability exist; workflow sprawl and release-gate fragmentation reduce reliability. |
| Documentation and governance | 6.0 | Exceptionally deep evidence trail, but canonical truth is stale and documentation volume now obscures the actual state. |
| Production readiness | 4.8 | Product/runtime baseline is green, but production authority is correctly withheld. |

---

## 2. Scope, methodology and limitations

### 2.1 Work performed

The review included:

- Archive extraction, inventory and deterministic content hashing.
- Source-layout and code-size analysis.
- Review of the active FastAPI entrypoint, router registry, settings, database layer, security boundaries, runtime KG, frontend package and build configuration.
- Static compilation of Python application, tests, scripts and migrations.
- Inspection of CI workflows, Makefile release commands, test configuration, coverage contracts and release evidence.
- Inspection of the production-readiness register and PRD-11 Execution-6/7 records.
- Test inventory through Python AST analysis.
- Unit-test collection in the available audit environment.
- Focused execution of the ETL MCP startup tests.
- Static inspection of ORM tables, Alembic migration topology and committed OpenAPI artifacts.
- Complexity indicators: large modules, long functions, broad exception handlers, TODOs and coverage exclusions.

### 2.2 Successfully reproduced checks

- `python -m compileall -q app tests scripts alembic` — **passed**.
- PRD-11 Execution-6 evidence verifier — committed summary reports **valid: true** and critical product flows green.
- PRD-11 Execution-7 authority verifier — authority/contract is valid, but final result is **valid: false** because the advisory gates are not green.
- `tests/unit/test_etl_mcp_server_startup.py` — **2 passed** in this audit environment.
- Alembic topology static inspection — **47 revision files and one apparent head**.

### 2.3 Important limitations

The supplied archive does not contain `.git` metadata. Therefore, the review could not independently validate:

- the claimed branch name or clean working tree;
- merge commit SHA provenance;
- GitHub branch protection and required-check configuration;
- hosted CI run conclusions;
- whether every evidence artifact was captured from the exact merged commit claimed in historical records.

The execution environment also lacked the complete pinned dependency set. Full unit-test collection reached **2,802 collected tests** but produced **132 collection errors**, all attributable to missing packages in the audit environment (`asyncpg`, `bcrypt`, `structlog`, `redis`, `slowapi`, `anthropic`, `passlib`, `hypothesis`, `psycopg2`). These are **not counted as repository test failures**. They demonstrate that the full project requires its canonical Python 3.12 dependency environment and cannot be validated meaningfully from a generic interpreter.

Docker services and the live Postgres/Redis stack were not restarted from the archive during this review. Runtime conclusions therefore distinguish between directly inspected source and committed runtime evidence.

---

## 3. Repository scale and composition

The project is large for a single-product, pre-production learning platform.

| Area | Observed scale |
|---|---:|
| Application files under `app/` | 739 |
| Test files under `tests/` | 1,011 |
| Documentation files under `docs/` | 3,099 |
| Scripts under `scripts/` | 1,247 |
| GitHub files | 108 |
| GitHub workflow files | 86 |
| Core source/test/script/migration lines | approximately 365,509 |
| Python files in core scope | 2,593 |
| TypeScript/TSX source files | 257 |
| Unit-test Python files | 795 |
| Approximate Python unit-test functions | 3,736 |
| Integration-test files | 53 |
| Approximate integration tests | 249 |
| Backend E2E files | 14 |
| Approximate backend E2E tests | 109 |
| Frontend test/spec files | 48 |
| Approximate frontend tests | 152 |
| ORM table classes | 103 |
| Alembic revision files | 47 |
| Canonical OpenAPI paths | 438 |
| Canonical OpenAPI operations | 446 |
| OpenAPI schemas | 178 |

### Interpretation

The codebase has crossed the threshold where informal single-developer coordination is no longer sufficient. The project now needs strict consolidation, ownership boundaries, generated-artifact discipline and a smaller number of authoritative workflows. The volume of governance code, scripts and documents is itself a material maintenance surface.

---

## 4. What the system currently implements

### 4.1 Active runtime shape

The active implementation is a **modular monolith**:

- FastAPI application: `app/api_v2.py`.
- Next.js frontend: `app/frontend`.
- PostgreSQL persistence through SQLAlchemy and Alembic.
- Redis for cache/session/job-related support where configured.
- ARQ-oriented background job support.
- Prometheus metrics and deep readiness checks.
- Optional Azure Key Vault secret loading and Azure-oriented deployment assets.
- Runtime knowledge graph persisted in PostgreSQL.

The FastAPI application mounts the same router registry under both `/api/v2` and `/v2`, resulting in two public aliases for almost the complete API surface.

### 4.2 Implemented product domains

The code and schemas demonstrate real implementation across:

- Authentication, refresh tokens, password lifecycle and onboarding.
- Learner profiles and guardian relationships.
- Consent lifecycle, version history, withdrawal, export and erasure workflows.
- Diagnostic sessions and IRT-based assessment capabilities.
- Lesson generation, lesson persistence and completion tracking.
- Practice sessions, spaced review and mastery snapshots.
- Study plans and study-plan templates.
- Gamification, points, badges and leaderboards.
- Parent/guardian progress and reporting paths.
- Learner tutor sessions, messages, grounding records and escalations.
- Curriculum source acquisition, extraction, page/chunk provenance and review.
- Curriculum graph nodes, edges, mappings and runtime KG state.
- Content Factory generation, review, staging, promotion and production-read verification.
- AI provider usage, reservation and budget controls.
- Subscription/billing models and Stripe webhook handling.
- Observability, security-assurance, privacy-operations, performance and release-readiness projections.

This breadth is a genuine strength. It also creates a risk of declaring maturity based on domain presence rather than live operational proof.

### 4.3 Scope inconsistency

The product identity is not stated consistently:

- `README.md` and `docs/current_state.md` describe a South African **Grade 4 Mathematics** platform.
- The FastAPI description states **Grade R to 7**.
- Repository tests and content-scope records indicate Grade 4 Mathematics remains the only launch-active scope, while broader grades are review/expansion scopes.

The external product statement should be narrowed to what is currently learner-visible and operationally supported.

---

## 5. True production-readiness state

### 5.1 Verified green areas

The current register and Execution-6 evidence record the following as green:

- Critical product flows.
- Product gate and product-runtime gate.
- Runtime baseline.
- Runtime stack.
- Database lineage and schema contract.
- Redis readiness.
- Ready probe.
- Generated contracts.
- Frontend quality.

Execution-6 is recorded as `valid: true`, with independent product commands and captured evidence.

### 5.2 Current release blockers

Execution-7 defines seven release-blocking commands:

1. Fresh, bounded, sharded coverage execution.
2. Ruff over `app` and `tests`.
3. mypy over `app`.
4. Bandit over `app` and `scripts`.
5. `pip-audit` over base and development requirements.
6. `pnpm audit --prod` for the frontend.
7. `detect-secrets` baseline review over release-relevant paths.

The current record states:

- `coverage_gate_green: false`
- `advisory_static_gate_green: false`
- `dependency_audit_gate_green: false`
- `secret_baseline_gate_green: false`
- `evidence_recorded: false`
- `production_release_authorised: false`
- `deployment_authorised: false`
- `release_tag_authorised: false`
- `public_beta_authorised: false`
- `live_payment_processing_authorised: false`

This is the correct decision. The system should not move to production merely because feature and runtime tests are green.

### 5.3 Controlled-beta nuance

The authority register says limited live learner traffic has been authorised by PRD-10, but it simultaneously records:

- `live_learner_traffic_operationally_safe: false`
- `controlled_beta_activation_operational_hold: true`

The practical interpretation is that governance authority exists for a controlled cohort, but activation remains suspended until current operational and advisory evidence is green. This distinction should be made explicit in every public or operator-facing status page.

### 5.4 Register inconsistency

The production-readiness register contains inconsistent summary layers:

- Top-level `status` still reads `prd11_runtime_restore_execution_5_evidence_recorded`.
- Top-level and `current_truth` fields record later Execution-6 completion and Execution-7 as the next authorised item.

This does not invalidate the detailed state, but it weakens the register as a machine-readable single source of truth.

---

## 6. Architecture assessment

### 6.1 Strengths

- The active backend is clearly designated as `app/api_v2.py`.
- Domain, repository, service, module and router layers exist.
- Import-linter contracts attempt to prevent direct router-to-repository coupling.
- A shared `EnvelopedRoute` provides response-contract consistency.
- Authentication and consent dependencies are widely applied.
- Runtime KG is integrated as a first-class persistence and projection layer rather than an isolated experiment.
- Database sessions use transaction commit/rollback boundaries.
- Production secrets are forced through Azure Key Vault when the environment is production.
- Readiness and operational endpoints are separated from domain routes.

### 6.2 Layering is only partially enforced

The import-linter contract explicitly exempts several routers from the no-direct-repository rule, including consent, content factory, gamification, learners, onboarding and parents. The largest router, `content_factory.py`, is approximately **1,336 lines** and imports repositories and many orchestration services directly.

This shows that the desired architecture is clearer than the implemented architecture. The project should treat the current exceptions as a debt register with removal dates, not permanent policy.

### 6.3 Oversized modules and functions

Examples of large active modules include:

- `app/services/etl/etl_pipeline.py` — about 1,464 lines.
- `app/api_v2_routers/content_factory.py` — about 1,336 lines.
- `app/services/etl/etl_pipeline_v2.py` — about 1,106 lines.
- `app/services/curriculum/graph.py` — about 983 lines.
- `app/services/content_review_governance.py` — about 959 lines.
- `app/services/batch_generation.py` — about 876 lines.
- `app/services/popia_service.py` — about 784 lines.

There are multiple functions over 180 lines, including content staging, learner tutor, batch execution, POPIA export, KG alignment and grounded generation.

These modules are difficult to reason about, mock, type-check and secure. They are also likely contributors to the current Ruff/mypy/Bandit convergence problem.

### 6.4 Duplicate and transitional implementations

The ETL area contains:

- `etl_pipeline.py`
- `etl_pipeline_v2.py`
- `etl_pipeline_v3_additions.py`

The database layer exposes compatibility aliases for legacy tests and helper modules. The source tree also retains `app/legacy` and multiple overlapping authorisation implementations under `app/core` and `app/security`.

This is understandable during migration, but a release candidate should have a single supported implementation per concern, or a documented retirement path with executable deprecation checks.

### 6.5 Broad exception handling

The non-legacy application contains approximately **122 broad `except Exception` or bare exception handlers**. Some are appropriate at integration boundaries, but hotspots occur in health, jobs, database instrumentation, LLM providers, content-generation execution and runtime readiness.

The risk is not simply style. Broad handling can:

- turn real failures into degraded-but-200 responses;
- conceal provider or persistence defects;
- prevent meaningful retry classification;
- make Sentry/metrics less actionable;
- reduce branch coverage and type precision.

### 6.6 API alias duplication

Every registered router is mounted under both `/api/v2` and `/v2`. This doubles much of the OpenAPI surface and increases:

- authorization-test burden;
- rate-limit and middleware consistency requirements;
- client contract ambiguity;
- deprecation complexity;
- attack surface and observability cardinality.

The project should designate one canonical prefix and time-box the other as a compatibility alias.

---

## 7. Data and persistence assessment

### 7.1 Strengths

The data model is far beyond a mock implementation:

- 103 ORM table classes.
- 47 Alembic revisions.
- One apparent migration head: `20260711_1510_prd11_runtime_green_exec5`.
- Explicit tables for learners, guardians, consent, audit, diagnostics, lessons, mastery, practice, runtime KG, curriculum provenance, content review, AI operations and billing.
- Database-lineage evidence is recorded green in Execution-5/6.
- Postgres-specific operational controls include connection timeouts, pool pre-ping and production pool sizing.
- Audit-event mutation prevention is attempted through database rules.

### 7.2 Risks

#### Large schema surface

A 103-table model before production creates substantial migration, backup, retention, privacy and support obligations. Every table containing learner, guardian, tutor or audit data should be classified in a live data inventory with:

- lawful purpose;
- owner;
- retention period;
- export behavior;
- erasure behavior;
- encryption classification;
- backup handling;
- tenant/isolation rule.

#### Migration history complexity

The migration chain includes several branch merges and historical repair migrations. It currently appears to converge to one head, which is positive, but production promotion should still prove:

- upgrade from the last supported release state;
- restore into an empty database;
- rollback/forward-fix behavior;
- migration duration on realistic data volume;
- schema/model drift after migration.

#### Transaction policy

`get_db()` commits after every successful request dependency scope. This is convenient but can produce hidden write transactions for read-oriented handlers when services mutate ORM state or emit audit events. Explicit command/query transaction ownership would make behavior easier to reason about.

---

## 8. Runtime knowledge graph assessment

The knowledge-graph pivot is materially implemented. The schema includes:

- graph loads;
- runtime nodes and edges;
- learner node states;
- runtime KG events;
- curriculum node/edge versions;
- source mappings and review events;
- learner projection services.

The learner projection service deterministically calculates mastery from evidence, confidence and correctness, and marks gaps relative to a threshold.

### Strengths

- Stable-code-based mapping supports versioned curriculum identity.
- Learner state is separated from target curriculum structures.
- Runtime persistence and event tables support auditability.
- KG capability is integrated into diagnostics, lessons and study-plan projections.

### Remaining maturity gaps

- The current mastery projection is still comparatively simple: correctness ratio multiplied by average confidence. It is not yet a full probabilistic learner model.
- Graph quality depends on reviewed CAPS mappings and corpus governance; runtime sophistication cannot compensate for mapping errors.
- Scale characteristics of graph traversal, projection refresh and event growth need production-sized load evidence.
- Version migration of learner states across graph revisions needs explicit, tested policy.
- The system should distinguish authoritative learner mastery, inferred mastery and tentative evidence in API contracts.

The KG implementation is a credible foundation, but it should not yet be marketed as a mature adaptive knowledge model without longitudinal validation.

---

## 9. Testing and quality assessment

### 9.1 Strengths

The repository contains one of its strongest assets in its test suite:

- Approximately 3,736 Python unit-test functions.
- Approximately 249 integration tests.
- Approximately 109 backend E2E tests.
- Approximately 152 frontend tests.
- Separate markers for unit, integration, E2E, slow, LLM, performance, smoke, governance, product, runtime and advisory tests.
- Recorded green product-critical-flow evidence.
- Dedicated authorization, consent, POPIA, audit, migration, content review, KG, frontend and CI-contract tests.
- Property-based diagnostics tests are present.
- Playwright and accessibility contracts are present.

### 9.2 Coverage is not currently trustworthy as a release metric

The target is 70% line coverage. The current production register still records the coverage gate as false. The old RR-003 fallback showed `0.0%`, but that value was caused by collection blockers and is not a meaningful measure of actual exercised code.

The correct next step is exactly what Execution-7 defines: a clean, bounded, sharded coverage run with structured summaries and no terminal timeout leaves.

### 9.3 Environment-dependent MCP startup tests

The focused MCP startup tests passed in this audit environment because the real `mcp.server.fastmcp` backend is absent, causing the test stub path to be selected.

In the dependency-complete canonical environment, the real backend is installed and selected first. The tests set `EDUBOOST_ALLOW_MCP_TEST_STUB=1`, but that flag permits fallback; it does not force the stub. This creates two environment-sensitive failures unless the tests explicitly block the real backend import or otherwise force `FASTMCP_BACKEND == "test-stub"`.

This is a real test-isolation defect, not a product-runtime failure.

### 9.4 Test-suite maintainability

A large portion of the test suite verifies governance documents, scripts, PR evidence and workflow text. These controls are useful, but they inflate the unit suite and can make the signal from product behavior less visible.

Recommended separation:

- `product-unit`
- `product-integration`
- `runtime-stack`
- `architecture-static`
- `governance-contract`
- `release-evidence`

Only the first four should dominate ordinary pull-request feedback. Governance and evidence suites should remain strict but run in clearly named, separately reported jobs.

---

## 10. Frontend assessment

### 10.1 Strengths

- Next.js App Router application.
- Strict TypeScript with `noUncheckedIndexedAccess`, `noImplicitOverride`, `noImplicitReturns` and no emit.
- Vitest and Testing Library coverage.
- Playwright E2E.
- PWA/service-worker support through Serwist, disabled by default during ordinary quality gates.
- Explicit environment validation.
- Quality commands cover type-check, lint, tests and build.
- The current production-readiness register records frontend quality green.

### 10.2 Dependency alignment risk

The frontend manifest currently combines:

- `next: 16.2.7`
- `react/react-dom: 18.3.1`
- `eslint-config-next: 15.5.18`
- `@next/bundle-analyzer: 15.5.18`
- TypeScript `5.4.5`

Next.js 16's App Router is aligned with React 19.2-era capabilities. The mixed Next 16 / React 18 / Next tooling 15 set is therefore a material compatibility and supportability risk. Even where installation succeeds, the project can encounter peer-dependency warnings, unsupported behavior, lint-rule drift and framework/runtime assumptions.

The frontend should use one intentionally tested compatibility set and pin the framework, React, ESLint config and bundle analyzer to a coherent release line.

### 10.3 Dual package-management surfaces

There is a root `package.json` and root `pnpm-lock.yaml`, plus a separate frontend package and lockfile. The root package contains Supabase, ESLint and Playwright dependencies, while the frontend contains the application dependencies.

This can be valid for workspace-style E2E tooling, but no explicit pnpm workspace file was observed at the root. The repository should either:

- formalize a pnpm workspace and central dependency policy; or
- isolate root E2E tooling and document exactly which lockfile each CI job must use.

---

## 11. Security and POPIA assessment

### 11.1 Strong controls already present

- Production configuration requires Azure Key Vault.
- JWT secrets are length-validated.
- Access tokens are short-lived by default.
- Password policy and bcrypt configuration exist.
- Refresh-token rotation and denylist tests exist.
- CORS origins are parsed and validated.
- Metrics access is restricted to private address ranges in production.
- Security headers middleware is installed.
- Rate-limit configuration exists for authentication, LLM and tutor routes.
- Admin routers use `require_admin` dependencies.
- Learner/guardian object-authorization tests are extensive.
- Consent, versioning, withdrawal, export, erasure and audit records are implemented.
- Audit mutation resistance is addressed at the database layer.
- LLM cost, provider and reservation controls are present.

### 11.2 Current security assurance is incomplete

The repository explicitly records that these are not green:

- Bandit release security.
- Python dependency audit.
- Frontend production dependency audit.
- Secret-baseline review.
- Combined advisory static gate.

Therefore, the correct security conclusion is:

> **The security architecture is thoughtful, but the current code and dependency state has not yet earned release assurance.**

### 11.3 Authorization duplication and placeholders

`app/security/authorization.py` contains guardian and teacher relationship helper placeholders that currently return `False`. They fail closed, so they are not an immediate privilege-escalation vulnerability. However, parallel implementations also exist in `app/core/authorization.py` and `app/security/object_authorization.py`.

This duplication makes it difficult to know which policy is authoritative and can cause accidental denial, inconsistent behavior or future unsafe bypasses. One object-authorization engine should be designated and all routes migrated to it.

### 11.4 Privacy operations require live-data proof

The presence of POPIA code and documents is not equivalent to production compliance. Before live production, the project still needs evidence for:

- data inventory against the live schema;
- actual export completeness;
- actual erasure across primary, derived, cache, analytics and backup stores;
- guardian verification and minor-data handling;
- retention enforcement;
- processor agreements and subprocessor inventory;
- incident response and notification process;
- access review and operator separation of duties.

---

## 12. CI/CD and governance assessment

### 12.1 Strengths

- CI includes Postgres/pgvector and Redis service containers.
- Unit, integration, schema, OpenAPI, architecture, dependency, security, frontend and E2E workflows exist.
- Release evidence is captured as structured JSON, not only narrative documents.
- Many verifiers prohibit presence-only evidence and require command outputs.
- The PRD model clearly separates authorization from evidence.
- The current system correctly refuses production authority while gates remain red.

### 12.2 Workflow sprawl

There are **86 workflow files**. Multiple workflows overlap in:

- backend unit/integration tests;
- OpenAPI checks;
- coverage;
- dependency scans;
- architecture enforcement;
- frontend E2E;
- release-readiness evidence;
- roadmap/PRD governance.

This creates four risks:

1. Engineers cannot easily identify the canonical required check.
2. Similar checks may use different Python, Postgres, dependency or command versions.
3. Non-required red checks can accumulate while a single governance check remains green.
4. Workflow maintenance becomes a major product cost.

### 12.3 Inconsistent strictness

Examples observed:

- The main CI runs mypy with `continue-on-error: true`.
- Markdown and link checks are advisory in places.
- A separate Execution-7 contract intends mypy to be release-blocking.
- Different workflows use pgvector PostgreSQL 15 and 16.
- Workflows target combinations of `master`, `main`, `develop`, release branches and historical branches.
- Some workflows use setup-python v5 while others use v6.

The project needs one canonical CI graph with explicit job classes:

- required pull-request checks;
- required merge-to-master checks;
- scheduled advisory checks;
- manually dispatched evidence captures.

### 12.4 Governance is overrepresented

The project has invested heavily in evidence manifests, approval records and closure verifiers. This has prevented premature release claims, which is valuable. However, governance volume has outgrown the product's ability to keep canonical documents current.

Governance should now be simplified around a small number of generated truth artifacts rather than adding more hand-maintained layers.

---

## 13. Documentation and contract integrity

### 13.1 Canonical status is stale

`README.md` and `docs/current_state.md` still describe PRD-0 as active and PRD-1 as blocked. The actual register records PRD-0 through PRD-10 closed and PRD-11 Runtime Restore Execution-7 active.

`docs/current_state.md` claims to be the source of truth, but its `last_reviewed` date is 2 July 2026 and its body is materially behind the register.

This is a high-severity documentation defect because release and operational decisions explicitly depend on these documents.

### 13.2 OpenAPI artifact duplication

The generator's default canonical output is `docs/openapi.json`.

Observed committed artifacts:

- `docs/openapi.json`: 438 paths and 446 operations.
- root `openapi.json`: 416 paths and 424 operations.
- root `openapi.yaml`: byte-identical to root `openapi.json`, despite its YAML extension.

The root artifacts omit 22 newer paths, including content quality, observability, performance, privacy, security and vertical-journey routes.

This is concrete generated-artifact drift. The stale root files should be removed, redirected or generated from the same source in one atomic command.

### 13.3 Documentation volume versus utility

With more than 3,000 documentation files, the project has an information architecture problem. Historical records are useful for audit, but they should not compete with current engineering guidance.

A practical documentation structure should expose only:

1. Current state.
2. Architecture.
3. Developer setup.
4. Product/domain behavior.
5. Operations/runbooks.
6. Security/privacy.
7. Current roadmap.
8. Archived evidence.

Everything else should be moved under an immutable archive index and excluded from ordinary navigation and search.

---

## 14. Code-quality findings

### 14.1 Static compilation

All inspected Python source, tests, scripts and migrations compiled successfully. No syntax-level defect was found.

### 14.2 Complexity indicators

- 122 broad exception handlers in non-legacy application Python.
- 32 `pass` statements.
- 18 `pragma: no cover` exclusions.
- 10 TODO/HACK-style markers.
- Multiple modules over 900 lines.
- Multiple functions over 180 lines.

These counts are not failures by themselves, but they explain why whole-repository static gates remain difficult to close.

### 14.3 Inconsistent project metadata

- `pyproject.toml` says Python `>=3.11`.
- CI and documentation standardize on Python `3.12.3`.
- The audit host used Python 3.13, which is outside the proven CI target.

The project should state one supported runtime range and test all supported versions, or pin production and development to exactly 3.12.3.

### 14.4 Dependency scope bloat

The backend entrypoint states: “No Celery, no RabbitMQ, no microservices.” Yet base requirements include Celery and Flower, and TODOs in auth routes still refer to Celery tasks. The ML requirements also contain a very large GPU/transformer stack.

The dependency graph should be split into deployable profiles:

- API runtime.
- Worker runtime.
- Content/ETL tooling.
- Documentation.
- ML research/training.
- Development/test.

The production API image should not install research or unused queue dependencies.

---

## 15. Operational readiness

### Existing strengths

- `/health`, `/ready` and deep health endpoints.
- Prometheus metrics.
- Structured logging and request IDs.
- Sentry configuration hooks.
- Redis and database health checks.
- Backup and restore scripts/workflows.
- Docker Compose, Kubernetes and Bicep assets.
- Alertmanager and Grafana configuration.
- Runtime stack and DB lineage evidence recorded green.

### Remaining gaps

- Production deployment is not authorised.
- Release tag is not authorised.
- Secret, dependency and SAST gates are not green.
- No independent proof from the ZIP that infrastructure definitions match a deployed production environment.
- Disaster recovery must be proven with actual restore timing and data integrity, not only workflow contracts.
- Operational SLOs, alert thresholds and on-call ownership need live validation under representative load.
- A single-developer project has key-person risk for incident response, release approval and evidence custody.

---

## 16. Highest-priority findings

| Priority | Finding | Severity | Why it matters | Required action |
|---|---|---:|---|---|
| P0 | Execution-7 quality/security gates are not green | Critical release blocker | Production code has not passed complete coverage, static, SAST, dependency and secret assurance | Fix and rerun each gate independently; capture immutable green evidence before release authority |
| P0 | Canonical current-state documents are stale | High | Operators and developers can make decisions from PRD-0 information while the project is at PRD-11 | Generate README/current-state summaries directly from the production register |
| P0 | Frontend dependency set is not coherently aligned | High | Framework/runtime/tooling incompatibility can invalidate the recorded frontend green state after reinstall | Align Next, React, eslint-config-next and bundle analyzer; regenerate lockfiles; rerun full quality and audit |
| P1 | CI is fragmented across 86 workflows | High | Required checks and failure authority are difficult to understand or maintain | Consolidate to a small canonical workflow graph and archive historical workflows |
| P1 | OpenAPI artifacts disagree | High | Clients can generate against stale contracts and miss 22 routes | Keep one generated artifact, or generate all formats atomically and verify hashes |
| P1 | Architecture exceptions and oversized modules | High | Static/type/security convergence and future change safety are impaired | Split content factory, ETL, POPIA and generation services; remove import-linter exceptions gradually |
| P1 | Environment-sensitive MCP tests | Medium-high | Canonical dependency-complete CI can fail while local minimal environments pass | Force stub backend in stub tests and retain a separate real-backend test |
| P1 | Dependency profiles are too broad | Medium-high | Larger attack surface, image size, audit burden and install fragility | Separate API, worker, ETL, ML and dev dependency sets |
| P1 | Authorization implementations overlap | Medium-high | Policy can drift across routes and services | Establish one object-authorization service and remove compatibility copies |
| P2 | API mounted under two prefixes | Medium | Doubled contract and test surface | Select `/api/v2` as canonical and deprecate `/v2` with telemetry and deadline |
| P2 | Register summary fields disagree | Medium | Machine-readable state is ambiguous | Add schema validation ensuring top-level status derives from current truth |
| P2 | Product scope statement is inconsistent | Medium | Stakeholders may believe Grade R–7 is live | State Grade 4 Mathematics as current launch scope; label other grades as planned/review-only |

---

## 17. Recommended remediation sequence

### Phase A — Close PRD-11 Execution-7 without expanding scope

1. Repair the two MCP startup tests so the stub path is explicitly forced.
2. Run the bounded coverage suite to completion and publish the true percentage and missing-line profile.
3. Fix Ruff violations in `app` and `tests`.
4. Establish a realistic mypy baseline by package, then remove `continue-on-error` from the canonical release job.
5. Resolve Bandit findings or document narrow, reviewed suppressions.
6. Resolve Python dependency audit findings and regenerate locks.
7. Align frontend framework dependencies, run `pnpm audit --prod`, then rerun type-check, lint, tests and build.
8. Review and update `.secrets.baseline`; do not merely regenerate it without human disposition.
9. Capture independent command artifacts and close Execution-7 only when every release-blocking gate is green.

### Phase B — Restore truth and contract integrity

1. Generate `README.md` status and `docs/current_state.md` from the production register.
2. Fix the stale top-level register status.
3. Remove or regenerate root OpenAPI artifacts.
4. Add a single command that verifies register, current-state docs, route inventory and OpenAPI consistency.
5. Archive old reports and historical PRD evidence outside the default MkDocs navigation.

### Phase C — Reduce architectural risk

1. Split `content_factory.py` into thin route modules by generation, review, staging and promotion.
2. Consolidate ETL pipelines behind one versioned interface.
3. Extract long orchestration functions into typed command objects and domain services.
4. Remove direct router-to-repository exceptions.
5. Consolidate authorisation modules.
6. Retire or quarantine `app/legacy` and compatibility aliases after usage inventory.

### Phase D — Consolidate CI and dependencies

1. Replace 86 active workflows with a small set of canonical workflows:
   - PR core;
   - product/runtime integration;
   - frontend/E2E;
   - scheduled security/dependency;
   - release evidence;
   - manual operations drills.
2. Standardize Python 3.12.3, Node and pnpm versions in one toolchain file.
3. Standardize pgvector/Postgres version.
4. Formalize or remove the root/frontend dual package arrangement.
5. Split Python dependency profiles and produce lean deployment images.

### Phase E — Production authorization

Only after A–D:

1. Re-run migrations on clean and restored databases.
2. Perform backup/restore and rollback drills with measured RTO/RPO.
3. Run representative load and cost tests.
4. Validate live POPIA export/erasure across all stores.
5. Conduct external security review and penetration testing.
6. Run a time-boxed controlled-beta activation with explicit kill switch.
7. Capture release candidate evidence from the exact tagged commit.
8. Authorise production release, deployment and release tag through the PRD process.

---

## 18. Release recommendation

### Current decision: **NO-GO for production release**

The project should remain under its current operational hold.

### Current decision: **Conditional GO for continued controlled internal/staging validation**

Continued staging, test cohorts and non-public controlled validation are reasonable where:

- no live payments are processed;
- the cohort and guardian-consent boundary is enforced;
- rollback and kill-switch controls are active;
- operators understand that static/security assurance is incomplete;
- no production-readiness claim is made.

### Conditions for changing to production GO

All of the following must be true:

- Execution-7 is green and evidence-recorded.
- Canonical status documents and generated contracts agree.
- Frontend dependency alignment is corrected and freshly verified.
- Coverage is at or above the agreed threshold with no hidden collection failures.
- Ruff, mypy, Bandit, pip-audit, pnpm audit and secret review are release-green.
- Production migrations, backup/restore, rollback, load, monitoring and POPIA operations are proven against the release candidate.
- The exact release commit is protected, tagged and independently reproducible.

---

## 19. Final true-state statement

EduBoost V2 has achieved substantial engineering depth. The product vision is present in real code, not only documents: adaptive diagnostics, learning-state modelling, CAPS-grounded content, learner and parent experiences, consent/privacy controls, a runtime knowledge graph, content operations and release governance all exist.

The principal risk is no longer “Can this system be built?” The system has been built to a meaningful extent.

The principal risk is now:

> **Can this very large, fast-evolving, single-developer codebase be made internally consistent, fully testable, dependency-safe, operationally reproducible and supportable before it is exposed as a production service for children and guardians?**

The current answer is **not yet**, but the remaining blockers are identifiable and the repository's own governance model is correctly preventing an unsupported release claim.

The highest-value work is not another feature or another governance document. It is convergence: one truth source, one API contract, one supported toolchain, one set of required CI gates, one authorization model, smaller modules, and green independent evidence for the complete release candidate.

---

## Appendix A — Key evidence inspected

- `README.md`
- `docs/current_state.md`
- `docs/roadmap/production_readiness/production_readiness_register.json`
- `docs/roadmap/production_readiness/prd_1100r_runtime_restore_execution_7_coverage_static_security_green_record.json`
- `docs/release-evidence/production-readiness/prd-1100r-runtime-restore-execution-6-product-critical-flow-green/summary.json`
- `app/api_v2.py`
- `app/core/config.py`
- `app/core/database.py`
- `app/security/authorization.py`
- `app/services/runtime_kg/`
- `app/frontend/package.json`
- `app/frontend/next.config.js`
- `Makefile`
- `pytest.ini`
- `pytest-coverage.ini`
- `.coveragerc`
- `.importlinter`
- `.github/workflows/ci-core.yml`
- `.github/workflows/ci-cd.yml`
- `.github/workflows/architecture-gates.yml`
- `scripts/generate_openapi.py`
- `docs/openapi.json`
- `openapi.json`
- `openapi.yaml`
- Alembic revisions under `alembic/versions/`

## Appendix B — Commands and observations

```text
python -m compileall -q app tests scripts alembic
Result: passed

PYTHONPATH=. python scripts/roadmap_reconciliation/verify_prd1100r_runtime_restore_execution_7_coverage_static_security_green.py --json
Result: authority valid; final valid false because green evidence is absent

PYTHONPATH=. python -m pytest -c pytest.ini tests/unit/test_etl_mcp_server_startup.py -q
Result in audit environment: 2 passed

Unit collection in incomplete audit environment
Result: 2,802 tests collected; 132 collection errors caused by missing installed dependencies
```

## Appendix C — External compatibility note

The frontend dependency observation is informed by the official Next.js 16 upgrade guidance, which describes the App Router using React 19.2-era capabilities. The repository should validate its exact compatibility matrix against the installed framework release before recording a new frontend green baseline.
