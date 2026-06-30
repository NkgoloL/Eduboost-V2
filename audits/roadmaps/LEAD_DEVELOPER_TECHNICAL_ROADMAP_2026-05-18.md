# EduBoost V2 Lead Developer Technical Roadmap

Date: 2026-05-18
Repository: `/home/nkgolol/Dev/SandBox/dev/Eduboost-V2`
Purpose: comprehensive TODO list to implement the recent-change audit recommendations and the broader improvements I would prioritize as lead developer.

## Operating principles

- Runtime proof beats static proof.
- Canonical services should own domain behavior; routers should orchestrate HTTP only.
- Security and POPIA compliance issues get priority over cleanup.
- Compatibility adapters are acceptable as short-lived migration tools, not permanent architecture.
- A task is not closed unless the relevant tests run and pass without skips.

## Proof status model

Use this model for all roadmap items:

- `not-started`: no implementation.
- `static-passing`: source or import checks pass only.
- `runtime-passing`: direct module import/runtime smoke passes.
- `integration-passing`: HTTP, DB, or worker integration proof passes.
- `production-ready`: documented, observable, configured, deployable, and covered by CI.

## Phase 0 - Evidence and release gate cleanup

Goal: make the audit evidence trustworthy before more closure claims are made.

### TODO

- [ ] Create a single evidence status registry under `docs/release` that maps every audit finding to proof status.
- [ ] Mark skipped integration tests as `not proven`, not passing.
- [ ] Update check scripts that still assert stale source text.
- [ ] Make evidence-generating scripts opt-in for file writes, or write only under a temp/evidence output directory during tests.
- [ ] Add CI job that runs:
  - [ ] compileall on backend packages.
  - [ ] focused Ruff runtime-symbol checks.
  - [ ] import-linter contracts.
  - [ ] backend runtime import smoke tests.
  - [ ] core HTTP integration tests.
- [ ] Split checks into `static`, `runtime`, `integration`, and `release` make targets.
- [ ] Add a release rule: no P0/P1 item can be closed by static evidence alone.

### Acceptance criteria

- [ ] All current stale/contradictory checks are either updated or explicitly quarantined.
- [ ] Routine test runs do not dirty docs unless an evidence-generation flag is set.
- [ ] CI reports proof status by category.

## Phase 1 - P0/P1 runtime blockers

Goal: eliminate the concrete runtime risks found during the recent-change audit.

### 1. JWT keyring fallback safety

- [ ] Update `app/services/jwt_keyring.py` so fallback uses the same configured secret path as `app.core.config.settings.JWT_SECRET`.
- [ ] Decide canonical env names:
  - [ ] Preferred: `JWT_KEYRING`.
  - [ ] Supported legacy: `JWT_SECRET` and `JWT_SECRET_KEY`.
- [ ] Add production guard that refuses `dev-insecure-secret-change-me`.
- [ ] Add test for `JWT_SECRET`-only configuration.
- [ ] Add test for `JWT_SECRET_KEY` legacy fallback.
- [ ] Add test for `JWT_KEYRING` current/previous decode behavior.
- [ ] Update `docs/security/jwt_rotation_plan.md`.

Acceptance criteria:

- [ ] `current_jwt_signing_key()` never returns the dev fallback when `JWT_SECRET` is configured.
- [ ] Production startup fails fast on placeholder JWT secrets.
- [ ] JWT rotation tests pass in CI.

### 2. ARQ worker import and job runtime proof

- [ ] Add `arq` to `requirements/base.in`.
- [ ] Regenerate `requirements/base.txt` and `requirements/dev.txt`.
- [ ] Add runtime smoke test: `import app.modules.jobs`.
- [ ] Add unit test that `WorkerSettings.functions` includes consent reminder functions.
- [ ] Add integration-style test for `run_consent_reminder_cycle` with fake session/service.
- [ ] Update stale diagnostics/jobs integrity checks to verify `job_dependency_factory` behavior.
- [ ] Document ARQ worker startup command and Redis requirements.

Acceptance criteria:

- [ ] `python3 -c "import app.modules.jobs"` passes from a clean install.
- [ ] WorkerSettings exposes expected functions and cron jobs.
- [ ] CI proves job payload validation and dependency construction.

### 3. POPIA consent lifecycle response contracts

- [ ] Decide canonical response model for POPIA lifecycle routes.
- [ ] Add canonical `deny` and `withdraw` methods to `app/modules/consent/service.py`, or adjust router outputs to canonical service behavior.
- [ ] Ensure grant, deny, withdraw, and renew return response shapes that match FastAPI response models.
- [ ] Add HTTP integration tests for all lifecycle routes.
- [ ] Add negative tests for unauthorized learner consent mutation.
- [ ] Add audit event assertions for each lifecycle transition.
- [ ] Remove stale TODO comments in `app/api_v2_routers/popia.py`.

Acceptance criteria:

- [ ] POPIA lifecycle HTTP tests pass without skipped cases.
- [ ] No lifecycle route can return `int` where `ConsentRecord` is declared.
- [ ] Audit events exist for grant, deny, withdraw, and renew.

## Phase 2 - Auth service consolidation

Goal: turn auth from a repaired router boundary into a clean application service.

### TODO

- [ ] Move `register`, `login`, `refresh`, and `create_dev_session` directly into `AuthApplicationService`.
- [ ] Remove monkey-patching from `app/services/auth_application_service.py`.
- [ ] Decide whether `AuthRuntimeContext` remains or is replaced by a typed service dependency bundle.
- [ ] Remove route-level dependency on `auth_runtime` once service owns the boundary.
- [ ] Move `_set_refresh_cookie` into a cookie/session policy helper shared by router and service.
- [ ] Align refresh cookie `max_age` with `REFRESH_TOKEN_EXPIRE_DAYS`.
- [ ] Remove unused/noisy imports from `auth.py`.
- [ ] Move `logout`, `sessions`, and `revoke-all` into the auth service or a session service.
- [ ] Add service-level tests for:
  - [ ] register success.
  - [ ] duplicate register.
  - [ ] login success.
  - [ ] wrong password.
  - [ ] refresh success with learner scope.
  - [ ] inactive account refresh rejection.
  - [ ] logout current session.
  - [ ] revoke all sessions.
- [ ] Add HTTP tests with dependency overrides proving non-500 failures.

Acceptance criteria:

- [ ] `AuthApplicationService` owns auth lifecycle methods directly.
- [ ] Auth router contains no repository or runtime bundle logic.
- [ ] Refresh preserves `guardian_learner_ids`.
- [ ] Register/login/refresh/logout paths pass HTTP integration tests.

## Phase 3 - Diagnostics and assessment integrity

Goal: prevent answer/session tampering and make diagnostic scoring auditable.

### TODO

- [ ] Persist served item ids for adaptive diagnostic sessions.
- [ ] Wire `validate_session_served_item_binding` into `diagnostic_respond`.
- [ ] Bind `diagnostic_next_item` to recovered session `caps_ref`; reject mismatched query caps.
- [ ] Ensure diagnostic submit scores only administered items, not the full grade bank.
- [ ] Add negative tests for:
  - [ ] duplicate answer item ids.
  - [ ] empty answer payload.
  - [ ] item id not served in session.
  - [ ] item id from another learner/session.
  - [ ] caps_ref mismatch.
- [ ] Add audit/event logging for diagnostic session start, item served, response submitted, and session completed.
- [ ] Review theta update validation for maximum delta and numeric safety.
- [ ] Add property-based tests for diagnostic payload validation.

Acceptance criteria:

- [ ] Adaptive diagnostic session cannot accept unserved item responses.
- [ ] Batch diagnostic scoring uses the administered set.
- [ ] Diagnostic integrity tests pass at unit and integration levels.

## Phase 4 - POPIA and privacy compliance hardening

Goal: make POPIA behavior canonical, auditable, and easy to reason about.

### TODO

- [ ] Consolidate deprecated `app/services/consent_service.py` into canonical `app/modules/consent/service.py` or fully remove remaining call sites.
- [ ] Define canonical consent aggregate and repository API.
- [ ] Ensure all learner data routes use centralized active-consent dependencies.
- [ ] Prove denial paths:
  - [ ] pending consent blocks.
  - [ ] denied consent blocks.
  - [ ] withdrawn consent blocks.
  - [ ] expired consent blocks.
- [ ] Implement retention policy checks for withdrawn/erasure-requested learner data.
- [ ] Add data export integration tests with authorization and consent boundaries.
- [ ] Add erasure request, cancel, approve, and execute integration tests.
- [ ] Add correction/restriction lifecycle tests.
- [ ] Produce a POPIA evidence matrix mapping legal obligations to routes, services, tests, and audit events.

Acceptance criteria:

- [ ] Single canonical consent service family.
- [ ] Every learner-data access route has explicit consent behavior.
- [ ] POPIA lifecycle and data subject rights have passing runtime tests.

## Phase 5 - Authorization and object boundary completion

Goal: finish object-level authorization across the API.

### TODO

- [ ] Expand import-linter router repository boundary from selected routers to all v2 routers.
- [ ] Reduce broad ignore list in `.importlinter`.
- [ ] Replace dynamic authorization helper imports with typed imports after canonical modules settle.
- [ ] Add object authorization for:
  - [ ] assessments.
  - [ ] diagnostics sessions.
  - [ ] gamification profile/xp.
  - [ ] study plans.
  - [ ] parent dashboards.
  - [ ] learner mastery.
  - [ ] exports/erasure/correction/restriction resources.
- [ ] Generate and maintain learner authorization matrix in CI.
- [ ] Add negative HTTP tests for cross-guardian access on each learner-owned resource.

Acceptance criteria:

- [ ] No router performs direct repository lookup before authorization when object ownership is required.
- [ ] Cross-guardian access is denied across all learner-owned resources.
- [ ] Import-linter router repository boundary applies broadly with minimal exceptions.

## Phase 6 - Service and repository architecture cleanup

Goal: reduce duplicated service families and compatibility shims.

### TODO

- [ ] Build a canonical service map for auth, consent, diagnostics, lessons, parents, billing, notifications, and audit.
- [ ] Mark each duplicate service as:
  - [ ] canonical.
  - [ ] compatibility shim.
  - [ ] deprecated.
  - [ ] removal candidate.
- [ ] Remove dynamic constructor probes where canonical constructors are known.
- [ ] Standardize repository constructor shape.
- [ ] Standardize service constructor shape.
- [ ] Move transaction ownership to service/application layer.
- [ ] Add transaction-bound integration tests for multi-write operations.
- [ ] Define dependency injection policy for FastAPI routes.
- [ ] Add ADR documenting service/module ownership.

Acceptance criteria:

- [ ] Service family map has one canonical owner per domain.
- [ ] Routers do not construct repositories directly.
- [ ] Compatibility adapters have removal dates and tracked owners.

## Phase 7 - Database, transactions, and data integrity

Goal: make multi-step domain operations atomic and recoverable.

### TODO

- [ ] Audit all multi-write operations for transaction boundaries.
- [ ] Wrap auth register/dev-session flows in transaction-safe unit of work.
- [ ] Wrap POPIA lifecycle transitions and audit writes atomically.
- [ ] Wrap diagnostic session response and mastery updates atomically.
- [ ] Wrap lesson completion and gamification updates atomically.
- [ ] Add DB constraints for critical uniqueness/integrity rules.
- [ ] Add migration smoke tests against disposable Postgres.
- [ ] Add idempotency keys for externally retried operations.
- [ ] Add optimistic locking or version checks for mutable session/consent records.

Acceptance criteria:

- [ ] No high-risk multi-write path can partially persist without audit/event consistency.
- [ ] Disposable DB proof runs in CI.
- [ ] Migration head applies and rolls forward cleanly.

## Phase 8 - Performance and scalability

Goal: reduce latency, N+1 queries, and operational cost.

### TODO

- [ ] Profile parent dashboard endpoints for N+1 behavior.
- [ ] Add query-count tests for high-traffic endpoints.
- [ ] Add read models for dashboard aggregates where appropriate.
- [ ] Cache stable curriculum/CAPS/item-bank metadata.
- [ ] Add pagination and limits to list endpoints without hard caps.
- [ ] Review item-bank queries and indexes.
- [ ] Review learner progress queries and indexes.
- [ ] Add slow query logging thresholds to staging.
- [ ] Add load test scenarios:
  - [ ] auth login/refresh.
  - [ ] learner dashboard.
  - [ ] diagnostic session.
  - [ ] lesson generation.
  - [ ] POPIA export.

Acceptance criteria:

- [ ] Key endpoints have baseline latency budgets.
- [ ] High-traffic endpoints have query-count guardrails.
- [ ] Slow query evidence is captured in staging.

## Phase 9 - Observability and operations

Goal: make production behavior observable and supportable.

### TODO

- [ ] Add structured request logging with correlation/request ids.
- [ ] Add metrics for auth failures, refresh reuse, consent denials, diagnostic errors, job failures, and LLM provider failures.
- [ ] Add health/readiness checks for:
  - [ ] database.
  - [ ] Redis.
  - [ ] ARQ worker dependency.
  - [ ] keyring configuration.
  - [ ] migration head.
- [ ] Add Sentry or equivalent exception reporting with PII scrubbing.
- [ ] Add alert rules for:
  - [ ] elevated 401/403 rates.
  - [ ] token decode failures.
  - [ ] consent denial spikes.
  - [ ] job failures.
  - [ ] DB connectivity.
  - [ ] LLM provider fallback exhaustion.
- [ ] Add runbooks for auth incident, consent incident, diagnostic integrity incident, and job backlog incident.

Acceptance criteria:

- [ ] Staging exposes actionable metrics and logs.
- [ ] Runbooks map alerts to investigation steps.
- [ ] PII scrubbing is verified.

## Phase 10 - Security hardening

Goal: reduce practical attack surface before production.

### TODO

- [ ] Enforce production secret validation for all placeholder secrets.
- [ ] Add token reuse detection for refresh-token rotation.
- [ ] Ensure refresh tokens are stored hashed, not raw, if not already.
- [ ] Add session/device metadata with privacy-safe handling.
- [ ] Review cookie policy for domain, secure, same-site, path, and max-age.
- [ ] Add rate limit coverage for auth, consent mutation, exports, and lesson generation.
- [ ] Add dependency vulnerability scanning.
- [ ] Add secrets scanning.
- [ ] Add security headers middleware review.
- [ ] Review CORS production allowlist.
- [ ] Add threat model for guardian/learner account takeover and data export abuse.

Acceptance criteria:

- [ ] Production cannot boot with placeholder secrets.
- [ ] Auth/session security tests pass.
- [ ] Security scan results are tracked and triaged.

## Phase 11 - AI, lesson generation, and content safety

Goal: make generated learning content reliable, safe, and curriculum-aligned.

### TODO

- [ ] Define canonical prompt/input schema for lesson generation.
- [ ] Add output schema validation and retry/fallback behavior.
- [ ] Add CAPS alignment checks for generated content.
- [ ] Add age-appropriate safety checks.
- [ ] Add hallucination/refusal fixtures for LLM outputs.
- [ ] Add provider fallback tests.
- [ ] Add cost controls per tier and per learner.
- [ ] Add content review workflow for high-risk generated content.
- [ ] Add telemetry for provider latency, cost, fallback, and refusal.

Acceptance criteria:

- [ ] Lesson generation has schema, safety, and CAPS validation.
- [ ] Provider fallback is deterministic and monitored.
- [ ] Cost controls are enforced and observable.

## Phase 12 - Frontend/backend contract reliability

Goal: make the frontend consume stable, tested API contracts.

### TODO

- [ ] Generate OpenAPI contract and publish it as a CI artifact.
- [ ] Add frontend contract tests against mocked and real backend envelopes.
- [ ] Verify auth refresh behavior in frontend.
- [ ] Verify consent-denied UI paths.
- [ ] Verify diagnostic session tamper rejection UX.
- [ ] Add Playwright smoke tests for guardian onboarding, learner selection, diagnostic, lesson flow, and consent withdrawal.
- [ ] Remove hardcoded dev-session assumptions from production builds.

Acceptance criteria:

- [ ] Frontend e2e smoke passes against local backend.
- [ ] API envelope and error shape mismatches are caught before release.

## Phase 13 - Product and domain improvements

Goal: improve EduBoost as a product, not just as a codebase.

### TODO

- [ ] Define learner progress model with explainable mastery changes.
- [ ] Add parent-facing explanations for gaps, recommendations, and progress.
- [ ] Add teacher/admin analytics boundaries if roles are retained.
- [ ] Add intervention recommendation engine based on diagnostic gaps.
- [ ] Add content quality feedback loop.
- [ ] Add learner streak/reward rules as explicit domain policies.
- [ ] Add feature flags for beta rollouts.
- [ ] Add usage analytics that avoid storing unnecessary PII.
- [ ] Add accessibility review for learner-facing flows.
- [ ] Add offline/low-bandwidth considerations for South African usage contexts.

Acceptance criteria:

- [ ] Product metrics and domain policies are explicit.
- [ ] User-facing learning outcomes are explainable.
- [ ] Accessibility and low-bandwidth paths are tested.

## Phase 14 - Documentation and maintainability

Goal: reduce future audit drift and onboarding cost.

### TODO

- [ ] Write ADR for canonical backend module boundaries.
- [ ] Write ADR for consent lifecycle architecture.
- [ ] Write ADR for auth/session architecture.
- [ ] Write ADR for diagnostic session integrity.
- [ ] Keep `docs/architecture/service_family_map.md` current.
- [ ] Add "how to run backend locally" with exact env, DB, Redis, worker, and tests.
- [ ] Add "how to prove release readiness" guide.
- [ ] Add "how to add a new route safely" guide covering auth, consent, audit, envelope, tests.
- [ ] Archive stale generated reports or label them historical.

Acceptance criteria:

- [ ] New developer can run and validate core backend flows from docs.
- [ ] Architecture docs match code.
- [ ] Historical evidence is clearly separated from current release evidence.

## Suggested implementation order

1. JWT fallback safety.
2. ARQ dependency/import proof.
3. POPIA lifecycle response-contract proof.
4. Evidence suite cleanup.
5. Auth service consolidation.
6. Diagnostics served-item integrity.
7. Authorization matrix expansion.
8. Service/repository consolidation.
9. Transaction and DB integrity hardening.
10. Observability, security, frontend contracts, and product optimizations.

## Definition of done for this roadmap

- [ ] All P0/P1 runtime blockers are fixed and covered by CI.
- [ ] All recent audit findings are mapped to proof statuses.
- [ ] No closure claim relies only on static source inspection.
- [ ] Core auth, POPIA, diagnostics, lessons, and job flows have runtime or integration proof.
- [ ] Architecture boundaries are enforced with minimal ignores.
- [ ] Production readiness evidence is current, reproducible, and clean.
