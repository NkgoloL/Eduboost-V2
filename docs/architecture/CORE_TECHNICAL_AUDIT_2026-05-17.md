# EduBoost V2 Core Technical Audit

Date: 2026-05-17  
Scope: backend application core, domain contracts, ORM models, modules, repositories, services, and V2 routers. Frontend and infrastructure were reviewed only where they affect core application architecture.  
Repository audited: `/home/nkgolol/Dev/Development/Eduboost-V2`  
Auditor stance: lead-developer readiness review, with priority given to runtime correctness, security, POPIA consent integrity, architecture boundaries, maintainability, and production operability.

## Executive Summary

EduBoost V2 has the right strategic direction: a FastAPI modular monolith, async SQLAlchemy persistence, Next.js frontend, POPIA-first consent flows, audit logging, Redis-backed runtime support, and domain modules for diagnostics, lessons, progress, practice, consent, and auth. The repository also contains substantial test and release-evidence scaffolding.

However, the implementation is currently in a migration-heavy state. The active V2 runtime cannot be reliably considered production-ready until several core issues are corrected:

- The V2 app import path is currently broken by `app/api_v2_routers/auth.py`, which references undefined names in route signatures and route bodies.
- Auth flows are incomplete or split between divergent service implementations.
- POPIA consent lifecycle code is duplicated and, in at least one router, wires incompatible repository and service types.
- Several learner-data routes still rely on inline authorization checks or comments instead of declarative, enforced object authorization and consent dependencies.
- Routers dynamically import repositories in many places, bypassing the repository-boundary contract declared in `.importlinter`.
- The codebase has duplicate canonical concepts: multiple `AuthService`, `ConsentService`, `LessonRepository`, `LearnerRepository`, `AuditRepository`, and diagnostic session services.
- Background job infrastructure is split between in-process FastAPI `BackgroundTasks` and ARQ worker definitions, with runtime routes using the less durable path.
- Diagnostics and lesson generation have promising domain logic, but the orchestration paths contain correctness, observability, and transaction-boundary risks.

The highest-value next move is not feature expansion. It is a consolidation sprint that restores a clean executable runtime, chooses canonical service and repository implementations, closes authorization gaps, and makes architecture contracts executable in CI.

## Evidence Collected

Commands and checks run:

- `find app -maxdepth 3 -type d`
- `rg --files app`
- `git status --short`
- `python3 -m compileall -q app/core app/domain app/models app/modules app/repositories app/services app/api_v2_routers`
- `python3 -m pytest tests/unit/test_api_v2_router_contract.py tests/unit/test_authorization_policy.py tests/unit/modules/diagnostics/test_session_lifecycle.py -q --tb=short`
- AST duplicate-class scan over `app/core`, `app/domain`, `app/models`, `app/modules`, `app/repositories`, `app/services`, and `app/api_v2_routers`
- Review of `.importlinter`, `README.md`, `docs/architecture/V2_ARCHITECTURE.md`, selected routers, repositories, services, config, database, auth, consent, diagnostics, lessons, jobs, health, and LLM gateway files.

Validation results:

- Python syntax compilation passed.
- Targeted pytest collection failed before tests executed because importing `app.api_v2` imports `app/api_v2_routers/auth.py`, where `get_db` is undefined in a route signature.
- `import-linter`, `ruff`, and `mypy` are not installed in the active WSL Python environment, though `requirements/dev.txt` lists `import-linter==2.1`.
- Existing `coverage.xml` reports backend `line-rate=0.009898`, likely stale or generated from a narrow run. Existing frontend coverage summary reports 96.82 percent line coverage.

Important audit limitation:

- The working tree was already heavily modified before this audit. Findings represent the current workspace state, not necessarily committed `master`.

## Architecture Snapshot

Active backend entrypoint:

- `app/api_v2.py`

Core backend composition:

- `app/api_v2_routers/`: HTTP route layer.
- `app/core/`: runtime kernel for config, DB sessions, security, jobs, logging, metrics, health, rate limiting, token revocation, middleware.
- `app/domain/`: schemas and domain contracts, but also compatibility exports.
- `app/models/`: canonical SQLAlchemy ORM models.
- `app/modules/`: bounded learning and operational modules.
- `app/repositories/`: persistence layer.
- `app/services/`: application workflow and migration-era compatibility services.

Observed backend size for core audit scope:

| Area | Files | Lines |
|---|---:|---:|
| `app/core` | 33 | 4,875 |
| `app/domain` | 11 | 1,195 |
| `app/models` | 3 | 1,302 |
| `app/modules` | 79 | 18,065 |
| `app/repositories` | 17 | 2,530 |
| `app/services` | 64 | 7,836 |
| `app/api_v2_routers` | 23 | 3,415 |

The codebase is large enough that informal conventions will not hold. Architecture boundaries must be enforced by tooling and tests.

## High Priority Findings

### P0 - V2 Runtime Import Is Broken

`app/api_v2.py` imports `app.api_v2_routers.auth`. During test collection, Python raises:

```text
NameError: name 'get_db' is not defined
```

Primary evidence:

- `app/api_v2_routers/auth.py:105` defines `create_dev_session(response: Response, db: AsyncSession = Depends(get_db))`.
- `AsyncSession`, `get_db`, `GuardianRepository`, `LearnerRepository`, `ConsentRepository`, `FourthEstateService`, token helpers, refresh-token helpers, `require_parent_or_admin`, and other names used later in the file are not imported in the file.
- `app/api_v2_routers/auth.py:196`, `258`, and `291` repeat the undefined `AsyncSession = Depends(get_db)` pattern.

Impact:

- The active FastAPI app cannot reliably start.
- Router contract tests cannot collect.
- OpenAPI generation and route inventory checks are blocked.

Recommendation:

- Restore explicit imports in `auth.py` or remove routes that depend on unavailable symbols.
- Add a minimal app-import smoke test in CI: `python -c "from app.api_v2 import app; print(len(app.routes))"`.
- Treat app import failure as a release blocker.

### P0 - Auth Flows Are Not Coherent

The auth router calls `AuthService()` without injecting dependencies:

- `app/api_v2_routers/auth.py:72`
- `app/api_v2_routers/auth.py:92`

But `app/services/auth_service.py` expects injected repositories and services:

- `app/services/auth_service.py:110-115`
- `guardian_signup()` calls `self._users.find_by_email(...)` at `app/services/auth_service.py:166`.
- `login()` calls `self._users.find_by_email(...)` at `app/services/auth_service.py:217`.

The router then returns dummy tokens:

- `app/api_v2_routers/auth.py:77-79`
- `app/api_v2_routers/auth.py:97-99`

There is also a separate `app/modules/auth/service.py` with a different persistence model and method names.

Impact:

- Registration and login are not production-functional through the active router.
- Token issuance behavior is split across multiple implementations.
- Security-sensitive business logic is difficult to reason about and test.

Recommendation:

- Select one canonical auth service.
- Inject explicit repositories/token store/email service via FastAPI dependency providers.
- Remove dummy token responses.
- Keep compatibility helpers only behind tests or separate legacy modules.

### P0 - POPIA Consent Lifecycle Is Wired to Incompatible Implementations

`app/api_v2_routers/popia.py` imports the consent service from `app.services.consent_service`:

- `app/api_v2_routers/popia.py:17`

That service expects:

- `app.repositories.consent_repository.ConsentRepository`, which is asyncpg/pool based and exposes `get_active_for_learner`, `create`, `update`, and `list_expiring_soon`.
- `app.repositories.audit_repository.AuditRepository`, which exposes `record`.

But the router provider returns repositories from `app.repositories.repositories`:

- `app/api_v2_routers/popia.py:33-34`

Those SQLAlchemy repositories expose different method names, such as `get_active`, `grant`, `revoke`, `renew`, and `log`.

Impact:

- `/popia/consent/grant`, `/deny`, `/withdraw`, and `/renew` are likely runtime failures.
- POPIA audit guarantees are undermined.
- The code gives a false impression of compliance coverage.

Recommendation:

- Use `app.modules.consent.service.ConsentService` consistently for SQLAlchemy V2 runtime, or rewrite `app.services.consent_service` to use the canonical SQLAlchemy repository interface.
- Add a consent lifecycle integration test that exercises the actual router dependency graph.
- Remove or archive the non-canonical consent service.

### P0 - Consent Actor Attribution Uses Random UUIDs

`app/api_v2_routers/popia.py` generates random actor IDs:

- `app/api_v2_routers/popia.py:122-123`
- `app/api_v2_routers/popia.py:138`
- `app/api_v2_routers/popia.py:154`
- `app/api_v2_routers/popia.py:167`

The file even states:

- `TODO: replace with real auth dependency that injects actor_id from JWT`

Impact:

- Audit events cannot be reliably tied to the authenticated guardian/admin.
- POPIA evidence trails can be incorrect.
- Fraud or dispute investigations lose actor accountability.

Recommendation:

- Replace random actor IDs with `actor_id_from_current_user(current_user)` or the canonical current-user dependency.
- Require object-level learner write authorization before consent state changes.
- Test that audit actor ID equals JWT subject for grant, deny, withdraw, and renew.

### P0 - Lesson Read/Complete/Sync Routes Lack Ownership and Consent Enforcement

In `app/api_v2_routers/lessons.py`, lesson generation is guarded:

- `app/api_v2_routers/lessons.py:51-54`
- `app/api_v2_routers/lessons.py:83-86`

But read, complete, and sync operations are not equivalent:

- `get_lesson()` fetches by lesson ID, then comments that the implementation trusts knowledge of `lesson_id`: `app/api_v2_routers/lessons.py:117-119`.
- `complete_lesson()` marks a lesson completed without checking learner ownership or active consent: `app/api_v2_routers/lessons.py:126-139`.
- `sync_lessons()` completes or records feedback for arbitrary lesson IDs in the request body: `app/api_v2_routers/lessons.py:142-160`.

Impact:

- A valid authenticated user who learns or guesses a lesson ID may read or mutate another learner's lesson.
- POPIA consent gating is inconsistent.
- This is a direct learner-data access control risk.

Recommendation:

- Load the lesson, load or derive its learner, then enforce object authorization and active consent before returning or mutating it.
- Prefer a dependency like `require_lesson_access_for_current_user` rather than inline comments.
- Add negative tests for cross-guardian lesson read, complete, and sync.

### P1 - Dynamic Repository Imports Bypass Architecture Contracts

`.importlinter` declares:

- Routers must not import repositories directly.
- Modules must not import routers.
- Modules must not import services.
- Repositories must not import services/modules/routers.
- Domain must not import infrastructure.
- Layered dependency chain: routers -> services/modules -> repositories -> domain/core.

But routers dynamically import repositories with `__import__`, including:

- `app/api_v2_routers/parents.py:54`, `140`, `245`, `271`, `334`
- `app/api_v2_routers/popia.py:33`
- `app/api_v2_routers/diagnostics.py:31-44`
- `app/api_v2_routers/study_plans.py:40`, `46`
- `app/api_v2_routers/gamification.py:38`, `46`, `63`, `93`, `107`
- `app/api_v2_routers/learners.py:30`, `47`, `65`, `74`, `113`, `121`, `134`, `142`, `172`
- `app/api_v2_routers/consent.py:44`, `80`, `110`
- `app/api_v2_routers/onboarding.py:36`

Impact:

- Static import rules cannot see the real dependency graph.
- Routers are taking on orchestration and repository-selection logic.
- Refactors become risky because dependency errors surface at runtime.

Recommendation:

- Replace dynamic imports with explicit service dependency providers.
- Move repository selection into services or provider functions outside routers.
- Install and run import-linter in CI.
- Add an AST check that flags `__import__("app.repositories...")` in routers.

### P1 - Duplicate Canonical Services and Repositories

AST scan found duplicate high-level concepts:

- `AuthService`: `app/modules/auth/service.py`, `app/services/auth_service.py`
- `ConsentService`: `app/modules/diagnostics/service.py`, `app/modules/consent/service.py`, `app/services/consent_service.py`
- `DiagnosticSessionService`: `app/modules/diagnostics/diagnostic_session_service.py`, `app/services/diagnostic_session_service.py`
- `AuditRepository`: `app/repositories/repositories.py`, `app/repositories/audit_repository.py`
- `ConsentRepository`: `app/repositories/repositories.py`, `app/repositories/consent_repository.py`
- `GuardianRepository`: `app/repositories/auth_repository.py`, `app/repositories/repositories.py`
- `LearnerRepository`: `app/repositories/repositories.py`, `app/repositories/learner_repository.py`
- `LessonRepository`: `app/repositories/repositories.py`, `app/repositories/lesson_repository.py`
- `DiagnosticRepository`: `app/repositories/diagnostic_repository.py`, `app/repositories/repositories.py`

Impact:

- Developers cannot easily know which implementation is canonical.
- Router/service wiring can pair incompatible interfaces.
- Tests may pass against one implementation while production routes use another.

Recommendation:

- Create a canonical inventory and mark each duplicate as keep, adapt, or delete.
- Keep one repository class per aggregate.
- Keep one application service per bounded capability.
- Preserve compatibility through adapters only when actively needed, and put them in `app/legacy` or `app/compat`.

### P1 - Authorization Helper Is Defined Twice

`app/core/authorization.py` defines `assert_can_access_learner` twice:

- First definition: `app/core/authorization.py:236`
- Second definition: `app/core/authorization.py:328`

The second definition overrides the first at import time.

Impact:

- Behavior is not the behavior documented near the first implementation.
- Tests or reviewers may inspect one function while runtime executes another.
- Policy logic becomes harder to audit.

Recommendation:

- Keep a single authorization API.
- Move compatibility behavior into a named adapter, for example `assert_can_access_learner_compat`.
- Add tests that prove guardian, learner, teacher, support, and admin access decisions.

### P1 - Transaction Boundaries Are Mixed

`app/core/database.py` commits automatically at the end of each request dependency:

- `app/core/database.py:59-69`

But services also commit internally:

- `app/modules/lessons/service.py:182-183`
- `app/modules/lessons/service.py:201-202`
- `app/modules/lessons/service.py:211-212`

Impact:

- Service methods become harder to compose transactionally.
- Partial commits can occur before later request-level work or audit work fails.
- Tests using rollback-based isolation become less reliable.

Recommendation:

- Adopt a clear unit-of-work policy.
- Prefer request-scoped commit at the boundary for HTTP requests.
- Let background workers own their own session and transaction.
- Services should flush but not commit unless explicitly designated as transaction owners.

### P1 - Background Job Runtime Is Split and Not Durable for User-Critical Work

There are two background job approaches:

- `app/core/jobs.py` uses FastAPI `BackgroundTasks` plus Redis/in-memory status tracking.
- `app/modules/jobs.py` defines ARQ jobs and worker settings.

Lesson generation uses the in-process FastAPI path:

- `app/api_v2_routers/lessons.py:61-70`
- `app/core/jobs.py:107-131`

Impact:

- Jobs can be lost on process shutdown or deploy.
- In-memory fallback is per-process only.
- Long-running lesson generation competes with web request lifecycle resources.
- The ARQ implementation exists but is not the path used by key user-facing routes.

Recommendation:

- Use ARQ for durable async operations such as lesson generation, RLHF export, backup, and diagnostic expiry.
- Have the HTTP route enqueue an ARQ job and return a job ID.
- Ensure workers create their own DB sessions and do not close over request-scoped services.

### P1 - Diagnostic Session Scoring Loses Item History

In `app/modules/diagnostics/diagnostic_session_service.py`, `submit_response()` appends only the item ID and correctness:

- `app/modules/diagnostics/diagnostic_session_service.py:112-118`

It then constructs responses by pairing every previous response with the current item:

- `responses = [(item, bool(row["correct"])) for row in snap.responses]`

The lower-level `IRTEngine` has a separate workaround using `_ItemProxy` for earlier items:

- `app/modules/diagnostics/irt_engine.py:659-671`

Impact:

- Theta estimates can be mathematically wrong because previous responses are scored against the wrong item parameters or generic proxies.
- Adaptive item selection and mastery scoring can drift.
- This directly affects learner placement and lesson remediation.

Recommendation:

- Store item parameters with each response snapshot, or rehydrate served items from the item bank repository before scoring.
- Add tests with two items of different difficulty/discrimination proving theta changes correctly based on response order and item parameters.

### P1 - Parent Dashboard Performs N Plus One Queries and Per-Learner LLM Calls

`app/api_v2_routers/parents.py` loops learners and executes multiple queries per learner:

- `app/api_v2_routers/parents.py:61-89`
- `app/api_v2_routers/parents.py:145-190`

The trust dashboard also calls `_executive.generate_progress_summary(...)` per learner:

- `app/api_v2_routers/parents.py:186-190`

Impact:

- Dashboard latency grows linearly with learner count.
- The route may trigger multiple LLM calls during a single page view.
- This risks cost spikes and poor parent-portal performance.

Recommendation:

- Replace per-learner counts with grouped aggregate queries.
- Cache progress summaries by learner/week or derive them from deterministic aggregates.
- Add latency budgets and route-level performance tests.

### P1 - Model and Repository Types Are Inconsistent

The canonical SQLAlchemy models use string IDs:

- `app/models/__init__.py:103`
- `app/models/__init__.py:166`
- `app/models/__init__.py:227` aliases `Learner = LearnerProfile`.

But generic repository code uses `UUID` typed IDs:

- `app/core/base.py:24`

`app/repositories/learner_repository.py` casts learner IDs to UUID:

- `app/repositories/learner_repository.py:31`

Impact:

- Runtime behavior can differ between repositories depending on whether they compare string columns to UUID instances or strings.
- Some repositories operate on `LearnerProfile`, others on `Learner` alias.
- This increases the risk of subtle query failures and inconsistent serialization.

Recommendation:

- Choose one ID representation across ORM models and repositories.
- Prefer UUID columns for real UUID primary keys, or consistently compare string IDs as strings.
- Add repository contract tests against the actual DB driver.

### P1 - Secrets Readiness Checks Do Not Reject Placeholder Secrets

`app/core/config.py` contains development defaults:

- `JWT_SECRET`: `CHANGE_ME_IN_PRODUCTION_AT_LEAST_32_CHARS` at `app/core/config.py:58`
- `ENCRYPTION_KEY`: placeholder at `app/core/config.py:67`
- `AUDIT_HMAC_SECRET`: `dev-audit-secret` at `app/core/config.py:72`

`check_required_secrets()` checks presence but not placeholder values:

- `app/core/health.py:82-98`

Production settings do attempt Key Vault loading:

- `app/core/config.py:191-196`

Impact:

- If production Key Vault wiring is bypassed or environment labels are wrong, placeholder values can appear healthy.
- Readiness may be green even when cryptographic material is not production-grade.

Recommendation:

- Add explicit placeholder rejection in production and staging.
- Include audit HMAC, encryption key, JWT secret, Stripe secrets, and LLM provider settings in production readiness checks.
- Add a `production-secret-placeholder-check` that runs against the effective settings object.

### P2 - Health Checks Are Serial and Can Be Faster

`gather_deep_health()` awaits checks one by one:

- `app/core/health.py:184-198`

Impact:

- Slow optional provider checks add directly to readiness latency.
- A degraded external provider can delay readiness responses.

Recommendation:

- Run independent checks with `asyncio.gather`.
- Apply short per-check timeouts.
- Keep optional checks clearly separated from critical readiness.

### P2 - LLM Gateway Implementations Are Split

There are multiple LLM paths:

- `app/core/llm_gateway.py`
- `app/modules/lessons/llm_gateway.py`
- `app/modules/lessons/llm_gateway_v2.py`
- `app/services/llm/gateway.py`

Impact:

- Provider fallback, circuit breaking, safety validation, token accounting, and caching behavior are not obviously canonical.
- Lesson generation may record provider as `"groq"` even when the source is fallback or cache:
  - `app/modules/lessons/service.py:156-175`

Recommendation:

- Pick one gateway interface and migrate callers.
- Make provider, model, fallback status, safety status, and token usage mandatory response metadata.
- Disallow static fallback in production unless explicitly configured as degraded mode and visible to users/operators.

### P2 - Generated Evidence Modules Dominate `app/modules`

Several large files under `app/modules/*/production_readiness_contracts.py` are 500 to 700 lines each. These are useful evidence artifacts but blur the line between runtime domain modules and release governance artifacts.

Impact:

- Domain package discovery becomes noisy.
- Import scans and module ownership become harder.
- New developers may confuse evidence contracts with runtime services.

Recommendation:

- Move release-evidence contracts to `docs`, `tests`, or `app/readiness` if they are not runtime dependencies.
- Keep runtime bounded contexts focused on product behavior.

## What Is Working Well

- The intended architecture is documented clearly in `docs/architecture/V2_ARCHITECTURE.md`.
- The V2 entrypoint has a clear router registry and dual prefixes for `/api/v2` and `/v2`.
- The database layer uses async SQLAlchemy and has basic slow-query instrumentation.
- The ORM schema includes many useful indexes and constraints.
- Object authorization and consent concepts exist and are tested in places.
- Lesson generation has structured output, CAPS validation, quota/caching concepts, audit logging, and LLM fallback ideas.
- Diagnostic IRT logic is substantial and includes parameter clamping, EAP estimation, and item-selection services.
- The frontend appears much healthier from the available coverage artifact than the backend runtime.

## Recommended Remediation Roadmap

### Sprint 1 - Restore Executable Runtime

Goals:

- `from app.api_v2 import app` works.
- `pytest tests/unit/test_api_v2_router_contract.py` collects and runs.
- Auth router no longer returns dummy tokens.
- POPIA consent endpoints use one compatible service/repository stack.

Actions:

- Fix `app/api_v2_routers/auth.py` imports and dependency wiring.
- Choose canonical `AuthService`.
- Choose canonical `ConsentService`.
- Remove random actor IDs from POPIA routes.
- Add startup smoke tests.

Exit criteria:

- App import smoke test passes.
- Auth register/login/refresh/logout tests pass through actual router.
- Consent grant/deny/withdraw/renew tests pass through actual router.

### Sprint 2 - Close Security and POPIA Access Gaps

Goals:

- Every learner-data route enforces object authorization and active consent.
- Lesson read/complete/sync cannot cross guardians.
- Audit actor IDs come from authenticated identity.

Actions:

- Create route dependencies for learner, lesson, diagnostic session, parent dashboard, and data rights access.
- Replace inline checks and comments with declarative dependencies where possible.
- Add negative authorization tests per route family.

Exit criteria:

- Cross-guardian lesson, diagnostic, study-plan, parent, gamification, and POPIA access tests pass.
- Consent absence and withdrawn consent tests fail closed.

### Sprint 3 - Enforce Architecture Boundaries

Goals:

- Routers no longer dynamically import repositories.
- Import-linter runs in CI.
- Duplicates are classified and reduced.

Actions:

- Install dev tooling in the active environment.
- Replace router-level repository construction with dependency-injected services.
- Add an AST guard against `__import__("app.repositories...")` in routers.
- Create a deprecation map for duplicate services and repositories.

Exit criteria:

- Import-linter contracts pass.
- No dynamic repository imports remain in routers.
- Canonical service/repository ownership is documented.

### Sprint 4 - Stabilize Transactions and Jobs

Goals:

- Services do not unexpectedly commit inside request transactions.
- Durable jobs handle lesson generation and long-running tasks.

Actions:

- Define a unit-of-work policy.
- Move lesson generation background work from FastAPI `BackgroundTasks` to ARQ.
- Ensure worker jobs create their own DB session.
- Add job retry, idempotency, and timeout policy.

Exit criteria:

- Lesson job survives web process restart.
- Failed jobs expose structured error state.
- Transaction tests prove no partial commit on downstream audit failure.

### Sprint 5 - Fix Diagnostic Scoring Fidelity

Goals:

- Adaptive scoring uses exact item parameters for the full response history.
- Mastery and gap outputs are mathematically trustworthy.

Actions:

- Persist item parameter snapshots in diagnostic session state or rehydrate served items.
- Remove `_ItemProxy` from production scoring paths.
- Add property tests and fixed vector tests for IRT/EAP behavior.

Exit criteria:

- Theta updates are deterministic and correct for mixed item difficulty/discrimination cases.
- Session recovery preserves scoring fidelity.

### Sprint 6 - Consolidate LLM Gateway and Lesson Quality Pipeline

Goals:

- One canonical gateway interface.
- Provider, model, fallback status, safety status, token usage, and validation metadata are always recorded.

Actions:

- Migrate lesson generation to canonical `LLMGateway`.
- Centralize provider fallback, static fallback, quota, token tracking, and safety checks.
- Make production fallback behavior explicit and observable.

Exit criteria:

- Lesson records accurately describe provider and fallback.
- Static fallback cannot masquerade as provider success.
- Prompt/safety/PII checks run before persistence.

## Suggested Technical North Star

Target dependency direction:

```text
api_v2_routers
  -> application services / module facades
    -> repositories
      -> models + domain contracts
core
  -> shared runtime primitives only
```

Rules:

- Routers should know HTTP, authentication dependencies, request schemas, and response schemas.
- Services should own use cases and transaction-independent business orchestration.
- Repositories should own persistence and query shape.
- Domain should own schemas, policies, and pure behavior.
- Core should own runtime primitives, not product workflows.
- Compatibility code should live in `app/legacy` or `app/compat`, not in canonical runtime paths.

## Priority Backlog

| Priority | Work Item | Impact | Effort |
|---|---|---:|---:|
| P0 | Fix `auth.py` imports and app import failure | Critical | S |
| P0 | Replace dummy register/login token responses | Critical | M |
| P0 | Fix POPIA router service/repository mismatch | Critical | M |
| P0 | Remove random consent actor IDs | Critical | S |
| P0 | Add lesson ownership and consent checks | Critical | M |
| P1 | Remove dynamic repository imports from routers | High | L |
| P1 | Pick canonical auth, consent, repository implementations | High | L |
| P1 | Restore import-linter in CI | High | S |
| P1 | Move long-running jobs to ARQ | High | M |
| P1 | Fix diagnostic response-history scoring | High | M |
| P1 | Normalize transaction ownership | High | M |
| P2 | Optimize parent dashboard aggregates | Medium | M |
| P2 | Parallelize deep health checks | Medium | S |
| P2 | Consolidate LLM gateways | Medium | L |
| P2 | Move evidence contracts out of runtime packages | Medium | M |

## Lead Developer Recommendation

Freeze broad feature work until the P0 items are closed. The codebase has good product ambition and many strong components, but it needs consolidation more than new surface area. A disciplined stabilization cycle should make the V2 runtime importable, make auth and consent trustworthy, enforce boundaries, and reduce duplicate canonical implementations.

Once those are done, the project will be in a much better position to invest in learning outcomes, diagnostics quality, lesson quality, and operational hardening without every change fighting the migration residue.
