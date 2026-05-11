# EduBoost V2 — Complete Outstanding Production Readiness TODO

**Purpose:** Replace the root `TODO.md` with a granular implementation backlog.  
**Scope:** All outstanding work required to move EduBoost V2 from the latest integrated `master` state to a production-ready, public-beta-safe platform.  
**Freshness marker:** this TODO assumes the repository state containing:

```text
Merge pull request #52 from NkgoloL/chore/slow-query-logging
```

**Canonical production branch:** `master`  
**Primary runtime:** `app.api_v2:app`  
**Frontend:** `app/frontend`  
**Production-readiness rule:** no item is considered complete unless there is implementation evidence and verification evidence.

---

## Status legend

- `[ ]` Not complete.
- `[x]` Complete and verified.
- `[blocked]` Blocked; add blocker note inline.
- `[verify]` Implemented but not yet verified.

## Priority legend

- `P0` — Release blocker. Required before handling real learner data or public beta.
- `P1` — Required before paid users, school pilots, or broad pilot rollout.
- `P2` — Important hardening, maintainability, UX, reliability, or scale work.
- `P3` — Later optimization or product expansion.
- `Research` — Requires spike, benchmark, legal review, educator review, or user research.

## Completion rule

For each completed task, add a reference to one or more of:

- source file
- test file
- migration
- CI job
- OpenAPI diff
- runbook
- staging evidence
- release evidence bundle
- security/compliance review
- legal review

---

# 0. Repository state and canonical source of truth

## 0.1 Canonical repo, fork, and branch policy

- [ ] `P0` Confirm canonical source repo in `docs/repository_governance.md`.
- [ ] `P0` Confirm active branch is `master`.
- [ ] `P0` Confirm latest valid repo state is identified by the commit message containing `Merge pull request #52`.
- [ ] `P0` Document relationship between `NkgoloL/Eduboost-V2` and `userxrebornbackup-ux/Eduboost-V2`.
- [ ] `P0` Document which repo produces official releases.
- [ ] `P0` Document which repo is allowed to receive production hotfixes.
- [ ] `P0` Document whether the backup fork is temporary, permanent mirror, or recovery source.
- [ ] `P0` Stop using raw commit count as the canonical freshness signal.
- [ ] `P0` Use head SHA + merge marker + release tag + CI evidence as freshness criteria.
- [ ] `P1` Add mirror-sync policy.
- [ ] `P1` Add fork divergence-detection policy.
- [ ] `P1` Add fork recovery procedure.
- [ ] `P1` Add release authority section.
- [ ] `P1` Add security patch authority section.
- [ ] `P1` Add archive/deprecation policy for stale forks.
- [ ] `P2` Add branch naming conventions.
- [ ] `P2` Add PR naming conventions.
- [ ] `P2` Add issue labels for `backend`, `frontend`, `security`, `compliance`, `ai`, `curriculum`, `devops`, `docs`, `qa`, `ops`, and `product`.

## 0.2 Repo-state verification automation

- [ ] `P0` Add `scripts/verify_repo_state.py`.
- [ ] `P0` Script must verify current git branch is `master`.
- [ ] `P0` Script must verify remote URL matches accepted canonical or recovery repo.
- [ ] `P0` Script must verify latest commit message contains the accepted freshness marker.
- [ ] `P0` Script must print current head SHA.
- [ ] `P0` Script must fail if working tree is dirty unless `--allow-dirty` is passed.
- [ ] `P0` Script must fail if run from the wrong repo.
- [ ] `P1` Add `make verify-repo-state`.
- [ ] `P1` Add CI step for repo-state verification.
- [ ] `P1` Add repo-state verification output to release evidence bundle.
- [ ] `P2` Add JSON output mode to `scripts/verify_repo_state.py`.

## 0.3 Branch protection and governance

- [ ] `P0` Protect `master`.
- [ ] `P0` Require pull request review before merge to `master`.
- [ ] `P0` Require required checks before merge to `master`.
- [ ] `P0` Disable force-push on `master`.
- [ ] `P0` Disable branch deletion on `master`.
- [ ] `P1` Require signed commits where feasible.
- [ ] `P1` Require linear history or document why merge commits are accepted.
- [ ] `P1` Add CODEOWNERS for backend.
- [ ] `P1` Add CODEOWNERS for frontend.
- [ ] `P1` Add CODEOWNERS for infrastructure.
- [ ] `P1` Add CODEOWNERS for security.
- [ ] `P1` Add CODEOWNERS for compliance.
- [ ] `P1` Add CODEOWNERS for curriculum/CAPS.
- [ ] `P1` Add CODEOWNERS for AI safety.
- [ ] `P1` Add CODEOWNERS for docs.
- [ ] `P1` Require security owner review for auth, secrets, crypto, authorization, and infra changes.
- [ ] `P1` Require compliance owner review for consent, POPIA, audit, export, erasure, and learner data changes.
- [ ] `P1` Require AI safety owner review for LLM prompts, lesson generation, RLHF, and content validation.
- [ ] `P1` Require curriculum owner review for CAPS map and diagnostic content.

---

# 1. PR-002R replacement — backend runtime and API contract baseline

## 1.1 PR-002R governance

- [ ] `P0` Create recovery document `docs/pr/PR-002R_BACKEND_RUNTIME_API_CONTRACT.md`.
- [ ] `P0` Explain why PR-002R exists.
- [ ] `P0` List original PR-002 expected deliverables if known.
- [ ] `P0` Mark PR-002R as replacement implementation, not a placeholder.
- [ ] `P0` Add PR-002R to `PR_INTEGRATION_SUMMARY.md`.
- [ ] `P0` Add PR-002R to release evidence bundle.
- [ ] `P1` Create issue `PR-002R Backend Runtime/API Contract Baseline`.
- [ ] `P1` Link all PR-002R commits to the issue.
- [ ] `P1` Add acceptance checklist to the PR template for API contract changes.

## 1.2 Canonical runtime

- [ ] `P0` Confirm production runtime is `app.api_v2:app`.
- [ ] `P0` Update all docs to reference `app.api_v2:app`.
- [ ] `P0` Update Dockerfile command to reference `app.api_v2:app`.
- [ ] `P0` Update docker-compose command to reference `app.api_v2:app` if command is explicit.
- [ ] `P0` Update CI smoke test to import `app.api_v2`.
- [ ] `P0` Update release checklist to require `app.api_v2:app`.
- [ ] `P0` Add `tests/test_runtime_entrypoints.py`.
- [ ] `P0` Add test importing `app.api_v2:app`.
- [ ] `P0` Add test importing `app.api.main:app`.
- [ ] `P0` Add test importing `app.legacy.api.main:app`, if legacy shim is retained.
- [ ] `P0` Ensure compatibility imports resolve to the V2 app or documented shim.
- [ ] `P0` Test that compatibility shim title/version matches V2 app.
- [ ] `P0` Test that compatibility shim exposes the same `/health` behavior.
- [ ] `P0` Test that compatibility shim exposes the same `/ready` behavior.
- [ ] `P1` Add `scripts/check_runtime_entrypoints.py`.
- [ ] `P1` Add `make runtime-check`.
- [ ] `P1` Add runtime check to CI.

## 1.3 Fix `app/api_v2.py` router registration

- [ ] `P0` Remove duplicate router import blocks from `app/api_v2.py`.
- [ ] `P0` Move `system.router` registration into the actual router-registration loop.
- [ ] `P0` Confirm `system.router` is registered under `/api/v2`.
- [ ] `P0` Confirm `system.router` is registered under `/v2`.
- [ ] `P0` Remove unreachable/dead router-registration code.
- [ ] `P0` Add regression test for system routes.
- [ ] `P0` Add import smoke test:
  ```bash
  python -c "from app.api_v2 import app; print(app.title)"
  ```
- [ ] `P0` Add test ensuring all router modules import without side effects.
- [ ] `P1` Add route inventory test that snapshots all registered routes.
- [ ] `P1` Commit route inventory artifact under `docs/route_inventory.md`.

## 1.4 Legacy route exclusion

- [ ] `P0` Define which routes are V2 production routes.
- [ ] `P0` Define which routes are legacy-only and forbidden in production.
- [ ] `P0` Add test proving legacy-only routes are not exposed by `app.api_v2:app`.
- [ ] `P0` Add test proving archived `app/legacy` code is not mounted.
- [ ] `P0` Add test proving V1 routers are not included accidentally.
- [ ] `P1` Add CI job `legacy-route-guard`.
- [ ] `P1` Add `docs/legacy_compatibility.md`.
- [ ] `P2` Remove stale V1 docs or mark them archived.

## 1.5 API response envelope

- [ ] `P0` Create `app/domain/api_v2_models.py`.
- [ ] `P0` Define `ApiMeta` model.
- [ ] `P0` Define `ApiError` model.
- [ ] `P0` Define `ApiEnvelope[T]` model.
- [ ] `P0` Define `PaginationMeta` model.
- [ ] `P0` Define success envelope helper `ok`.
- [ ] `P0` Define error envelope helper `fail`.
- [ ] `P0` Define pagination envelope helper `paginated`.
- [ ] `P0` Include `request_id` in every envelope.
- [ ] `P0` Include `api_version` in every envelope.
- [ ] `P0` Ensure `error` is `null` on success.
- [ ] `P0` Ensure `data` is `null` on error.
- [ ] `P0` Add unit tests for `ok`.
- [ ] `P0` Add unit tests for `fail`.
- [ ] `P0` Add unit tests for `paginated`.
- [ ] `P0` Apply envelope to auth router.
- [ ] `P0` Apply envelope to learners router.
- [ ] `P0` Apply envelope to lessons router.
- [ ] `P0` Apply envelope to study plans router.
- [ ] `P0` Apply envelope to diagnostics router.
- [ ] `P0` Apply envelope to gamification router.
- [ ] `P0` Apply envelope to onboarding router.
- [ ] `P0` Apply envelope to parents router.
- [ ] `P0` Apply envelope to billing router.
- [ ] `P0` Apply envelope to consent router.
- [ ] `P0` Apply envelope to consent renewal router.
- [ ] `P0` Apply envelope to POPIA router.
- [ ] `P0` Apply envelope to jobs router.
- [ ] `P0` Apply envelope to system router.
- [ ] `P1` Add lint/test rule preventing raw dict responses from production routers unless explicitly exempted.
- [ ] `P1` Add docs examples for success envelope.
- [ ] `P1` Add docs examples for error envelope.
- [ ] `P1` Add docs examples for pagination envelope.

## 1.6 API error contract

- [ ] `P0` Update `app/core/exceptions.py` to emit canonical error envelope.
- [ ] `P0` Include machine-readable error code.
- [ ] `P0` Include human-readable message.
- [ ] `P0` Include field errors when validation fails.
- [ ] `P0` Include remediation hint when useful.
- [ ] `P0` Include request ID.
- [ ] `P0` Prevent sensitive exception details from leaking.
- [ ] `P0` Implement error code `validation_error`.
- [ ] `P0` Implement error code `unauthorized`.
- [ ] `P0` Implement error code `forbidden`.
- [ ] `P0` Implement error code `not_found`.
- [ ] `P0` Implement error code `conflict`.
- [ ] `P0` Implement error code `rate_limited`.
- [ ] `P0` Implement error code `consent_required`.
- [ ] `P0` Implement error code `consent_expired`.
- [ ] `P0` Implement error code `dependency_unavailable`.
- [ ] `P0` Implement error code `internal_error`.
- [ ] `P0` Add tests for all error codes.
- [ ] `P0` Add tests for validation errors.
- [ ] `P0` Add tests for auth errors.
- [ ] `P0` Add tests for authorization errors.
- [ ] `P0` Add tests for consent errors.
- [ ] `P0` Add tests for rate-limit errors.
- [ ] `P0` Add tests proving internal exceptions hide details in production.
- [ ] `P1` Add `docs/error_contract.md`.

## 1.7 OpenAPI generation and contract

- [ ] `P0` Add `scripts/generate_openapi.py`.
- [ ] `P0` Ensure script imports `app.api_v2:app`.
- [ ] `P0` Ensure script writes `docs/openapi.json`.
- [ ] `P0` Generate `docs/openapi.json`.
- [ ] `P0` Add `make openapi`.
- [ ] `P0` Add `make openapi-check`.
- [ ] `P0` Add CI job `openapi-contract`.
- [ ] `P0` CI must fail if generated schema differs from committed schema.
- [ ] `P0` Add OpenAPI tags for ops.
- [ ] `P0` Add OpenAPI tags for auth.
- [ ] `P0` Add OpenAPI tags for learners.
- [ ] `P0` Add OpenAPI tags for consent.
- [ ] `P0` Add OpenAPI tags for diagnostics.
- [ ] `P0` Add OpenAPI tags for lessons.
- [ ] `P0` Add OpenAPI tags for study plans.
- [ ] `P0` Add OpenAPI tags for gamification.
- [ ] `P0` Add OpenAPI tags for parents.
- [ ] `P0` Add OpenAPI tags for POPIA.
- [ ] `P0` Add OpenAPI tags for billing.
- [ ] `P0` Add OpenAPI tags for jobs.
- [ ] `P0` Add OpenAPI tags for system.
- [ ] `P0` Add summaries for all production endpoints.
- [ ] `P0` Add descriptions for all production endpoints.
- [ ] `P0` Add examples for major request models.
- [ ] `P0` Add examples for major response models.
- [ ] `P1` Add breaking-change detection for OpenAPI diffs.
- [ ] `P1` Add PR label requirement for breaking API changes.
- [ ] `P1` Add `docs/api_v2.md`.
- [ ] `P1` Add `docs/api_versioning_policy.md`.
- [ ] `P2` Publish generated API docs through MkDocs/Sphinx.

## 1.8 PR-002R acceptance evidence

- [ ] `P0` PR-002R tests pass locally.
- [ ] `P0` PR-002R tests pass in CI.
- [ ] `P0` Runtime import test is included in release evidence bundle.
- [ ] `P0` OpenAPI schema hash is included in release evidence bundle.
- [ ] `P0` Route inventory is included in release evidence bundle.
- [ ] `P0` Error-envelope test output is included in release evidence bundle.
- [ ] `P0` Add PR-002R completion note to `docs/project_status.md`.
- [ ] `P0` Add PR-002R completion note to `PR_INTEGRATION_SUMMARY.md`.

---

# 2. Backend architecture, modular monolith, and dependency boundaries

## 2.1 Canonical architecture

- [ ] `P0` Reconfirm V2 is a modular monolith.
- [ ] `P0` Reconfirm no production microservices except explicitly documented inference sidecar if retained.
- [ ] `P0` Reconfirm no Celery/RabbitMQ for new V2 work unless explicitly re-approved.
- [ ] `P0` Reconcile docs that say “no microservices” with any inference sidecar.
- [ ] `P0` Reconcile docs that say “V1 fully deleted” with actual legacy shim/archive state.
- [ ] `P1` Update architecture diagram.
- [ ] `P1` Add `docs/backend_architecture.md`.
- [ ] `P1` Add `docs/architecture_decisions.md` index.
- [ ] `P1` Document bounded contexts:
  - auth
  - learners
  - consent
  - diagnostics
  - lessons
  - study plans
  - gamification
  - parent portal
  - POPIA
  - billing
  - jobs
  - observability
- [ ] `P2` Generate module dependency graph.

## 2.2 Business logic location

- [ ] `P0` Decide canonical business-logic location.
- [ ] `P0` Choose between `app/services` and `app/modules/<context>/service.py`.
- [ ] `P0` Write ADR `docs/adr/0010-business-logic-location.md`.
- [ ] `P1` Inventory all files in `app/services`.
- [ ] `P1` Inventory all files in `app/modules`.
- [ ] `P1` Identify duplicate service concepts.
- [ ] `P1` Collapse duplicate auth service concepts.
- [ ] `P1` Collapse duplicate consent service concepts.
- [ ] `P1` Collapse duplicate diagnostic service concepts.
- [ ] `P1` Collapse duplicate lesson service concepts.
- [ ] `P1` Collapse duplicate study-plan service concepts.
- [ ] `P1` Collapse duplicate parent-portal service concepts.
- [ ] `P1` Collapse duplicate billing service concepts.
- [ ] `P1` Mark deprecated service paths with deprecation notices.
- [ ] `P2` Add migration guide for service path changes.

## 2.3 Router thinness

- [ ] `P1` Audit auth router for business logic.
- [ ] `P1` Audit learners router for business logic.
- [ ] `P1` Audit lessons router for business logic.
- [ ] `P1` Audit study plans router for business logic.
- [ ] `P1` Audit diagnostics router for business logic.
- [ ] `P1` Audit gamification router for business logic.
- [ ] `P1` Audit onboarding router for business logic.
- [ ] `P1` Audit parents router for business logic.
- [ ] `P1` Audit billing router for business logic.
- [ ] `P1` Audit consent router for business logic.
- [ ] `P1` Audit consent renewal router for business logic.
- [ ] `P1` Audit POPIA router for business logic.
- [ ] `P1` Audit jobs router for business logic.
- [ ] `P1` Move business logic out of routers.
- [ ] `P1` Keep routers limited to validation, dependencies, service calls, and response mapping.
- [ ] `P1` Add code-review checklist item: “Router contains no business logic.”
- [ ] `P2` Add static complexity threshold for router functions.

## 2.4 Import boundaries

- [ ] `P1` Add `import-linter` configuration.
- [ ] `P1` Enforce `routers -> services/modules`.
- [ ] `P1` Enforce `services/modules -> repositories`.
- [ ] `P1` Enforce `repositories -> models/database`.
- [ ] `P1` Enforce `domain` has no infrastructure imports.
- [ ] `P1` Enforce repositories never import routers.
- [ ] `P1` Enforce services never depend on FastAPI `Request` unless explicitly justified.
- [ ] `P1` Add `lint-imports` to CI.
- [ ] `P1` Add import boundary check to required branch protection.
- [ ] `P2` Add docs explaining import boundaries.

## 2.5 Metaphor-layer cleanup

- [ ] `P1` Inventory active-code references to `executive`.
- [ ] `P1` Inventory active-code references to `judiciary`.
- [ ] `P1` Inventory active-code references to `fourth_estate`.
- [ ] `P1` Inventory active-code references to `ether`.
- [ ] `P1` Rename active engineering boundaries to domain names.
- [ ] `P1` Move metaphor language to product/storytelling docs only, if retained.
- [ ] `P2` Add glossary mapping old metaphor names to new domain names.
- [ ] `P2` Remove metaphor terminology from onboarding docs for new engineers.

---

# 3. Authentication, sessions, RBAC, and object-level authorization

## 3.1 Authentication flows

- [ ] `P0` Verify guardian signup success path.
- [ ] `P0` Verify guardian signup validation errors.
- [ ] `P0` Verify duplicate email handling.
- [ ] `P0` Verify login success path.
- [ ] `P0` Verify login invalid password path.
- [ ] `P0` Verify login nonexistent account path.
- [ ] `P0` Verify logout revokes current token.
- [ ] `P0` Verify logout clears refresh cookie where applicable.
- [ ] `P0` Verify refresh-token success path.
- [ ] `P0` Verify refresh-token expired path.
- [ ] `P0` Verify refresh-token reuse detection.
- [ ] `P0` Verify refresh-token family revocation.
- [ ] `P0` Verify email verification flow.
- [ ] `P0` Verify password reset request.
- [ ] `P0` Verify password reset token expiry.
- [ ] `P0` Verify password reset completion.
- [ ] `P0` Verify password reset invalid token behavior.
- [ ] `P1` Add account lockout or risk-based throttling after repeated failures.
- [ ] `P1` Add security alert event for suspicious auth behavior.
- [ ] `P1` Add tests for all auth abuse paths.

## 3.2 Password security

- [ ] `P0` Verify password hashing uses bcrypt or Argon2id with tuned cost.
- [ ] `P0` Verify configured bcrypt rounds are production-safe.
- [ ] `P0` Verify password strength policy.
- [ ] `P0` Add password strength tests.
- [ ] `P1` Add breached-password check if feasible.
- [ ] `P1` Add password change flow.
- [ ] `P1` Add password change audit event.
- [ ] `P2` Add optional passphrase guidance.

## 3.3 Token policy

- [ ] `P0` Confirm access-token TTL is 15 minutes or documented override.
- [ ] `P0` Confirm refresh-token TTL is 7 days or documented override.
- [ ] `P0` Verify refresh tokens are hashed at rest.
- [ ] `P0` Verify refresh tokens are revocable.
- [ ] `P0` Verify refresh tokens are bound to token family.
- [ ] `P0` Verify refresh-token rotation on use.
- [ ] `P0` Verify token-family reuse detection.
- [ ] `P0` Verify Redis-backed revocation.
- [ ] `P0` Decide behavior when Redis revocation store is unavailable.
- [ ] `P1` Add persistent fallback for revocation if required.
- [ ] `P1` Add JWT signing-key rotation with `kid`.
- [ ] `P1` Add current signing key.
- [ ] `P1` Add previous signing key validation window.
- [ ] `P1` Add emergency revoke-all procedure.
- [ ] `P1` Add tests for `kid` rotation.
- [ ] `P1` Add tests for emergency revoke-all.

## 3.4 Cookie security

- [ ] `P0` Verify cookies are `HttpOnly`.
- [ ] `P0` Verify cookies are `Secure` in production.
- [ ] `P0` Verify cookies use correct `SameSite`.
- [ ] `P0` Verify cookie domain is correct per environment.
- [ ] `P0` Verify cookie path is correct.
- [ ] `P0` Verify no refresh token is JavaScript-readable.
- [ ] `P0` Verify no access token is stored insecurely in frontend.
- [ ] `P1` Add cookie policy tests.
- [ ] `P1` Document cookie strategy.

## 3.5 RBAC and roles

- [ ] `P0` Define role `learner`.
- [ ] `P0` Define role `parent` or `guardian`.
- [ ] `P0` Define role `teacher`.
- [ ] `P0` Define role `admin`.
- [ ] `P0` Define role `support_operator`.
- [ ] `P0` Define role `content_reviewer`.
- [ ] `P0` Define role `compliance_auditor`.
- [ ] `P1` Document role permissions.
- [ ] `P1` Add tests for each role.
- [ ] `P1` Add route policy matrix.

## 3.6 Object-level authorization

- [ ] `P0` Add policy helper `can_view_learner`.
- [ ] `P0` Add policy helper `can_update_learner`.
- [ ] `P0` Add policy helper `can_generate_lesson_for_learner`.
- [ ] `P0` Add policy helper `can_start_diagnostic_for_learner`.
- [ ] `P0` Add policy helper `can_view_study_plan`.
- [ ] `P0` Add policy helper `can_view_parent_report`.
- [ ] `P0` Add policy helper `can_export_learner_data`.
- [ ] `P0` Add policy helper `can_request_erasure`.
- [ ] `P0` Add policy helper `can_view_billing`.
- [ ] `P0` Add test that learner cannot access another learner.
- [ ] `P0` Add test that guardian can access only linked learners.
- [ ] `P0` Add test that teacher can access only assigned learners/classes.
- [ ] `P0` Add test that support cannot view unnecessary PII.
- [ ] `P0` Add test that compliance auditor can view audit records without broad data mutation rights.
- [ ] `P0` Add audit events for privileged access.
- [ ] `P1` Add policy tests for every router.
- [ ] `P1` Move from basic RBAC to policy-based authorization for sensitive workflows.
- [ ] `P2` Add tightly audited admin impersonation only if absolutely required.

## 3.7 Rate limiting and abuse prevention

- [ ] `P0` Add rate limit to login.
- [ ] `P0` Add rate limit to signup.
- [ ] `P0` Add rate limit to refresh.
- [ ] `P0` Add rate limit to password reset.
- [ ] `P0` Add rate limit to email verification.
- [ ] `P0` Add rate limit to LLM lesson generation.
- [ ] `P0` Add rate limit to data export.
- [ ] `P0` Add rate limit to billing webhook endpoints if applicable.
- [ ] `P1` Add account-level throttling.
- [ ] `P1` Add IP-level throttling.
- [ ] `P1` Add risk-based throttling.
- [ ] `P1` Add rate-limit tests.

---

# 4. POPIA consent, privacy, data-subject rights, and audit

## 4.1 Consent lifecycle

- [ ] `P0` Define consent state `pending`.
- [ ] `P0` Define consent state `granted`.
- [ ] `P0` Define consent state `denied`.
- [ ] `P0` Define consent state `expired`.
- [ ] `P0` Define consent state `withdrawn`.
- [ ] `P0` Define consent state `renewal_required`.
- [ ] `P0` Implement consent grant flow.
- [ ] `P0` Implement consent denial flow.
- [ ] `P0` Implement consent withdrawal flow.
- [ ] `P0` Implement consent renewal flow.
- [ ] `P0` Implement consent expiry handling.
- [ ] `P0` Implement restricted mode after consent expiry if applicable.
- [ ] `P0` Tie consent to privacy notice version.
- [ ] `P0` Tie consent to guardian identity.
- [ ] `P0` Tie consent to learner identity.
- [ ] `P0` Audit every consent state change.
- [ ] `P1` Add consent expiry notification schedule.
- [ ] `P1` Add grace period policy if required.
- [ ] `P1` Add consent status dashboard for guardians.
- [ ] `P2` Add school-mediated consent model if institutional deployments enter scope.

## 4.2 Declarative consent enforcement

- [ ] `P0` Make consent enforcement declarative through FastAPI dependency or middleware.
- [ ] `P0` Add `scripts/check_consent_gates.py`.
- [ ] `P0` Identify all learner-data routes.
- [ ] `P0` Mark consent-required route patterns.
- [ ] `P0` Fail CI if consent-required route lacks consent gate.
- [ ] `P0` Add negative test for diagnostics without consent.
- [ ] `P0` Add negative test for lessons without consent.
- [ ] `P0` Add negative test for learner profile access without consent.
- [ ] `P0` Add negative test for study plan access without consent.
- [ ] `P0` Add negative test for gamification without consent.
- [ ] `P0` Add negative test for analytics processing without consent.
- [ ] `P0` Add negative test for RLHF feedback without consent.
- [ ] `P0` Add negative test for parent reports without consent.
- [ ] `P0` Add negative test for data export without consent/authority.
- [ ] `P0` Add negative test for erasure request without authority.
- [ ] `P1` Add route-level consent policy documentation.

## 4.3 Data subject rights

- [ ] `P0` Implement data export request creation.
- [ ] `P0` Implement data export status endpoint.
- [ ] `P0` Implement data export download endpoint.
- [ ] `P0` Implement machine-readable JSON export.
- [ ] `P0` Implement machine-readable CSV export.
- [ ] `P1` Implement guardian-friendly PDF export summary.
- [ ] `P0` Implement erasure request creation.
- [ ] `P0` Implement erasure status endpoint.
- [ ] `P0` Implement erasure approval/review queue.
- [ ] `P0` Implement erasure execution with audit-retention exceptions.
- [ ] `P0` Implement correction/update workflow.
- [ ] `P0` Implement processing restriction workflow.
- [ ] `P0` Implement SLA tracking for export requests.
- [ ] `P0` Implement SLA tracking for erasure requests.
- [ ] `P1` Add admin review queue for billing/school/legal-retention conflicts.
- [ ] `P1` Add notification to guardian when export is ready.
- [ ] `P1` Add notification to guardian when erasure completes.
- [ ] `P1` Add tests for export workflow.
- [ ] `P1` Add tests for erasure workflow.
- [ ] `P1` Add tests for correction workflow.
- [ ] `P1` Add tests for restriction workflow.

## 4.4 Data minimization and inventory

- [ ] `P0` Create or update `docs/data_inventory.md`.
- [ ] `P0` List every collected learner field.
- [ ] `P0` List every collected guardian field.
- [ ] `P0` List every collected diagnostic field.
- [ ] `P0` List every collected lesson/AI field.
- [ ] `P0` List every collected billing field.
- [ ] `P0` List purpose for each field.
- [ ] `P0` List lawful/consent basis for each field.
- [ ] `P0` List retention period for each field.
- [ ] `P0` List access roles for each field.
- [ ] `P0` List third-party exposure for each field.
- [ ] `P0` Remove non-essential learner data fields.
- [ ] `P0` Hash or tokenize identifiers where raw values are unnecessary.
- [ ] `P0` Separate identifiable operational data from analytics data.
- [ ] `P0` Prevent names, emails, phone numbers, and raw identifiers from LLM prompts.
- [ ] `P1` Create or update `docs/data_retention_policy.md`.
- [ ] `P1` Create or update `docs/subprocessor_register.md`.

## 4.5 Audit integrity

- [ ] `P0` Confirm sensitive events write to append-only PostgreSQL audit repository.
- [ ] `P0` Prevent application update/delete operations on audit records.
- [ ] `P0` Prevent database role update/delete on audit records where feasible.
- [ ] `P0` Add event hash to audit records.
- [ ] `P0` Add previous event hash to audit records.
- [ ] `P0` Add HMAC/signature to audit records.
- [ ] `P0` Add audit-chain verification script.
- [ ] `P0` Add audit event for login success.
- [ ] `P0` Add audit event for login failure.
- [ ] `P0` Add audit event for token refresh.
- [ ] `P0` Add audit event for logout.
- [ ] `P0` Add audit event for consent grant.
- [ ] `P0` Add audit event for consent renewal.
- [ ] `P0` Add audit event for consent withdrawal.
- [ ] `P0` Add audit event for consent expiry.
- [ ] `P0` Add audit event for learner profile create/update/delete.
- [ ] `P0` Add audit event for diagnostic start.
- [ ] `P0` Add audit event for diagnostic answer submission.
- [ ] `P0` Add audit event for diagnostic completion.
- [ ] `P0` Add audit event for lesson generation.
- [ ] `P0` Add audit event for LLM provider call.
- [ ] `P0` Add audit event for parent report generation.
- [ ] `P0` Add audit event for data export request.
- [ ] `P0` Add audit event for data export download.
- [ ] `P0` Add audit event for erasure request.
- [ ] `P0` Add audit event for erasure execution.
- [ ] `P0` Add audit event for admin access.
- [ ] `P0` Add audit event for billing changes.
- [ ] `P1` Add immutable retention rules for audit records.
- [ ] `P1` Add automated audit completeness tests.
- [ ] `P1` Build internal audit dashboard.

## 4.6 Legal/privacy docs

- [ ] `P0` Draft Privacy Policy.
- [ ] `P0` Draft Terms of Service.
- [ ] `P0` Draft Parent Consent Notice.
- [ ] `P0` Draft Child-friendly Privacy Notice.
- [ ] `P0` Draft Security Disclosure Policy.
- [ ] `P1` Complete DPIA-style privacy impact assessment.
- [ ] `P1` Conduct legal review of Privacy Policy.
- [ ] `P1` Conduct legal review of Terms of Service.
- [ ] `P1` Conduct legal review of Parent Consent Notice.
- [ ] `P1` Conduct legal review of Child-friendly Privacy Notice.
- [ ] `P1` Conduct legal review of data retention policy.
- [ ] `P1` Conduct legal review of subprocessor register.

---

# 5. Database, persistence, migrations, and performance

## 5.1 Schema readiness

- [ ] `P0` Confirm every production table has explicit primary key.
- [ ] `P0` Confirm every production table has timestamps.
- [ ] `P0` Confirm every relationship has appropriate foreign key.
- [ ] `P0` Confirm role enum constraints.
- [ ] `P0` Confirm consent status constraints.
- [ ] `P0` Confirm audit event constraints.
- [ ] `P0` Confirm immutable audit identifier constraints.
- [ ] `P0` Confirm unique guardian-learner relationship constraints.
- [ ] `P0` Confirm non-null constraints for sensitive workflow fields.
- [ ] `P0` Verify index on user email hash.
- [ ] `P0` Verify index on learner ID.
- [ ] `P0` Verify index on guardian ID.
- [ ] `P0` Verify index on consent status.
- [ ] `P0` Verify index on token identifiers.
- [ ] `P0` Verify index on diagnostic attempt/session ID.
- [ ] `P0` Verify index on lesson generation job ID.
- [ ] `P0` Verify index on audit timestamp.
- [ ] `P0` Verify index on audit actor ID.
- [ ] `P0` Verify index on subscription/customer ID.
- [ ] `P1` Add partial index for active consent.
- [ ] `P1` Add partial index for active subscriptions.
- [ ] `P1` Add partial index for non-revoked sessions.
- [ ] `P1` Add partial index for incomplete jobs.

## 5.2 Migration discipline

- [ ] `P0` Ensure `alembic upgrade head` runs in CI from empty DB.
- [ ] `P0` Ensure `alembic check` runs in CI.
- [ ] `P0` Add migration graph validation.
- [ ] `P0` Add schema integrity validation.
- [ ] `P0` Document rollback for every destructive migration.
- [ ] `P0` Require backup plan for migrations touching learner/guardian data.
- [ ] `P0` Require staging dry run for migrations touching learner/guardian data.
- [ ] `P0` Require validation script for migrations touching learner/guardian data.
- [ ] `P0` Require rollback plan for migrations touching learner/guardian data.
- [ ] `P1` Enforce migration naming convention:
  ```text
  YYYYMMDD_HHMM_<short_description>.py
  ```
- [ ] `P1` Add migration smoke test using production-like data volume.
- [ ] `P1` Add synthetic seed data for local development.
- [ ] `P1` Ensure no real learner PII appears in fixtures.
- [ ] `P2` Add migration-diff summary artifact in CI.

## 5.3 Transaction boundaries

- [ ] `P1` Review transaction boundary for signup.
- [ ] `P1` Review transaction boundary for learner creation.
- [ ] `P1` Review transaction boundary for consent submission.
- [ ] `P1` Review transaction boundary for diagnostic completion.
- [ ] `P1` Review transaction boundary for lesson generation.
- [ ] `P1` Review transaction boundary for billing changes.
- [ ] `P1` Review transaction boundary for erasure requests.
- [ ] `P1` Add tests for rollback on partial failure.
- [ ] `P1` Add tests for idempotent retries where appropriate.

## 5.4 Repository layer

- [ ] `P1` Add repository tests for guardian repository.
- [ ] `P1` Add repository tests for learner repository.
- [ ] `P1` Add repository tests for consent repository.
- [ ] `P1` Add repository tests for diagnostic repository.
- [ ] `P1` Add repository tests for lesson repository.
- [ ] `P1` Add repository tests for study-plan repository.
- [ ] `P1` Add repository tests for gamification repository.
- [ ] `P1` Add repository tests for audit repository.
- [ ] `P1` Add repository tests for billing repository.
- [ ] `P1` Ensure repositories do not expose raw ORM objects to API responses.
- [ ] `P1` Standardize repository method prefixes:
  - `get_*`
  - `list_*`
  - `create_*`
  - `update_*`
  - `soft_delete_*`
  - `append_*`
- [ ] `P1` Add pagination to all list queries.
- [ ] `P1` Add deterministic sorting to all list queries.
- [ ] `P2` Add cursor pagination for high-volume audit/event streams.

## 5.5 Performance

- [ ] `P1` Add slow-query logging in staging.
- [ ] `P1` Add slow-query logging in production.
- [ ] `P1` Add performance test for dashboard endpoints.
- [ ] `P1` Add performance test for diagnostic endpoints.
- [ ] `P1` Add performance test for lesson-generation endpoints.
- [ ] `P1` Add performance test for parent-report endpoints.
- [ ] `P1` Add performance test for audit endpoints.
- [ ] `P1` Add performance test for POPIA export endpoints.
- [ ] `P2` Define query latency budgets.
- [ ] `P2` Add DB connection pool monitoring.
- [ ] `P2` Add N+1 query checks for dashboard flows.

---

# 6. AI, LLM safety, lesson generation, and CAPS validation

## 6.1 LLM gateway

- [ ] `P0` Define canonical LLM gateway interface.
- [ ] `P0` Include provider name in gateway metadata.
- [ ] `P0` Include model/version in gateway metadata.
- [ ] `P0` Include prompt template version in gateway metadata.
- [ ] `P0` Include input schema in gateway metadata.
- [ ] `P0` Include output schema in gateway metadata.
- [ ] `P0` Include latency in gateway metadata.
- [ ] `P0` Include token usage in gateway metadata.
- [ ] `P0` Include safety status in gateway metadata.
- [ ] `P0` Include fallback status in gateway metadata.
- [ ] `P1` Add provider fallback.
- [ ] `P1` Add timeout per provider.
- [ ] `P1` Add retry policy per provider.
- [ ] `P1` Add circuit breaker.
- [ ] `P1` Add budget guardrails.
- [ ] `P1` Add deterministic mock provider.
- [ ] `P1` Add local/offline fallback for development only.
- [ ] `P1` Add provider health checks.
- [ ] `P1` Add emergency flag `DISABLE_LESSON_GENERATION`.
- [ ] `P2` Add model comparison harness.

## 6.2 PII safety in LLM calls

- [ ] `P0` Ensure no raw learner name enters prompts.
- [ ] `P0` Ensure no guardian name enters prompts.
- [ ] `P0` Ensure no email enters prompts.
- [ ] `P0` Ensure no phone number enters prompts.
- [ ] `P0` Ensure no address enters prompts.
- [ ] `P0` Ensure no raw learner UUID enters external prompts if pseudonym is available.
- [ ] `P0` Ensure `pseudonym_id` is used for LLM context.
- [ ] `P0` Expand `scripts/popia_sweep.py`.
- [ ] `P0` Add PII seeded tests for lesson generation.
- [ ] `P0` Add PII seeded tests for parent summaries.
- [ ] `P0` Add PII seeded tests for RLHF feedback.
- [ ] `P0` Add PII seeded tests for logs.
- [ ] `P0` Fail CI if PII is detected in prompt paths.
- [ ] `P1` Add PII redaction metrics.
- [ ] `P1` Add redaction failure alerts.

## 6.3 Structured lesson output

- [ ] `P0` Define lesson output field `topic`.
- [ ] `P0` Define lesson output field `grade`.
- [ ] `P0` Define lesson output field `subject`.
- [ ] `P0` Define lesson output field `CAPS reference`.
- [ ] `P0` Define lesson output field `objectives`.
- [ ] `P0` Define lesson output field `explanation`.
- [ ] `P0` Define lesson output field `worked examples`.
- [ ] `P0` Define lesson output field `practice questions`.
- [ ] `P0` Define lesson output field `answer key`.
- [ ] `P0` Define lesson output field `remediation hints`.
- [ ] `P0` Define lesson output field `difficulty`.
- [ ] `P0` Define lesson output field `language level`.
- [ ] `P0` Define lesson output field `safety classification`.
- [ ] `P0` Define lesson output field `alignment confidence`.
- [ ] `P0` Define lesson output field `quality score`.
- [ ] `P0` Reject generated lesson if schema invalid.
- [ ] `P0` Reject generated lesson if CAPS alignment invalid.
- [ ] `P0` Reject generated lesson if age-inappropriate.
- [ ] `P0` Reject generated lesson if unsafe.
- [ ] `P0` Reject generated lesson if PII detected.
- [ ] `P0` Reject generated lesson if answer key missing.
- [ ] `P0` Reject generated lesson if answer key inconsistent.
- [ ] `P1` Add schema examples to OpenAPI.
- [ ] `P1` Add lesson schema documentation.

## 6.4 Content correctness validators

- [ ] `P0` Add arithmetic correctness validator.
- [ ] `P0` Add answer-key consistency validator.
- [ ] `P0` Add grade-level readability validator.
- [ ] `P0` Add missing-explanation validator.
- [ ] `P0` Add unsafe-content validator.
- [ ] `P0` Add PII-leakage validator.
- [ ] `P0` Add independent answer-key checking.
- [ ] `P1` Add content quality score.
- [ ] `P1` Add quality score threshold.
- [ ] `P1` Add low-confidence rejection path.
- [ ] `P1` Add low-confidence human-review path.
- [ ] `P2` Add lesson regression suite.
- [ ] `P2` Add accepted lesson snapshot tests.
- [ ] `P2` Add prompt regression tests.

## 6.5 Golden prompt coverage

- [ ] `P1` Add golden prompt test for each supported grade.
- [ ] `P1` Add golden prompt test for each supported subject.
- [ ] `P1` Add golden prompt test for each launch topic.
- [ ] `P1` Add golden prompt test for English.
- [ ] `P1` Add golden prompt test for isiZulu.
- [ ] `P1` Add golden prompt test for Afrikaans.
- [ ] `P1` Add golden prompt test for isiXhosa.
- [ ] `P1` Add golden prompt test for standard lesson variant.
- [ ] `P1` Add golden prompt test for visual variant.
- [ ] `P1` Add golden prompt test for story-based variant.
- [ ] `P1` Add golden prompt test for step-by-step variant.
- [ ] `P1` Add golden prompt test for exam-style variant.
- [ ] `P1` Add golden prompt test for real-world South African examples.
- [ ] `P2` Add golden prompt report artifact.

## 6.6 CAPS alignment

- [ ] `P0` Create canonical CAPS topic map.
- [ ] `P0` Include phase.
- [ ] `P0` Include grade.
- [ ] `P0` Include subject.
- [ ] `P0` Include term.
- [ ] `P0` Include topic.
- [ ] `P0` Include subtopic.
- [ ] `P0` Include prerequisites.
- [ ] `P0` Include assessment standards.
- [ ] `P0` Validate generated content references a valid CAPS topic.
- [ ] `P0` Prevent claims of full CAPS coverage until coverage is validated.
- [ ] `P1` Add curriculum coverage dashboard.
- [ ] `P1` Detect topics without lessons.
- [ ] `P1` Detect topics without diagnostics.
- [ ] `P1` Detect topics without practice questions.
- [ ] `P1` Detect topics without quality-reviewed content.
- [ ] `P1` Add alignment confidence score per lesson.
- [ ] `P2` Add teacher-facing CAPS coverage export.
- [ ] `P2` Version curriculum maps.

## 6.7 RLHF and feedback loop

- [ ] `P1` Verify RLHF feedback capture.
- [ ] `P1` Verify PII scrubbing before RLHF storage.
- [ ] `P1` Verify PII scrubbing before RLHF export.
- [ ] `P1` Add RLHF export format for OpenAI preference datasets if retained.
- [ ] `P1` Add RLHF export format for Anthropic preference datasets if retained.
- [ ] `P1` Add consent check before RLHF processing.
- [ ] `P1` Add guardian/learner feedback issue-reporting flow.
- [ ] `P2` Add RLHF quality analytics.
- [ ] `P2` Add feedback moderation queue.
- [ ] `P2` Add educator review workflow.

---

# 7. Diagnostics, assessment, item bank, and mastery model

## 7.1 IRT engine validation

- [ ] `[critical]` Define diagnostic item schema: item ID, subject, grade, topic, skill, difficulty, discrimination, correct answer, distractors, explanation, and CAPS reference.
- [x] `[critical]` Validate IRT parameters for difficulty bounds, discrimination bounds, probability output, overflow, and invalid input.
- [x] `[critical]` Add tests for probability of correctness, Fisher information, ability update, edge responses, empty responses, all-correct, and all-incorrect.
- [x] `[high]` Add item calibration workflow.
- [x] `[high]` Add item exposure limits so learners do not repeatedly see the same questions.
- [x] `[high]` Add diagnostic session recovery after disconnect.
- [x] `[medium]` Add confidence intervals for ability estimates.
- [x] `[medium]` Add item bias review across language, region, and socioeconomic context.

Granular verification backlog:

- [ ] `P0` Define diagnostic item schema.
- [ ] `P0` Include item ID.
- [ ] `P0` Include subject.
- [ ] `P0` Include grade.
- [ ] `P0` Include topic.
- [ ] `P0` Include skill.
- [ ] `P0` Include difficulty parameter.
- [ ] `P0` Include discrimination parameter.
- [ ] `P0` Include correct answer.
- [ ] `P0` Include distractors.
- [ ] `P0` Include explanation.
- [ ] `P0` Include CAPS reference.
- [ ] `P0` Validate theta bounds.
- [ ] `P0` Validate discrimination bounds.
- [ ] `P0` Validate difficulty bounds.
- [ ] `P0` Validate probability output.
- [ ] `P0` Validate overflow safety.
- [ ] `P0` Validate invalid input handling.
- [ ] `P0` Add test for probability of correctness.
- [ ] `P0` Add test for Fisher information.
- [ ] `P0` Add test for ability update.
- [ ] `P0` Add test for EAP estimate.
- [ ] `P0` Add test for empty responses.
- [ ] `P0` Add test for all-correct responses.
- [ ] `P0` Add test for all-incorrect responses.
- [ ] `P0` Add test for stopping criteria.
- [ ] `P0` Add test for grade-equivalent mapping.
- [ ] `P1` Add test for item selection by Fisher information.
- [ ] `P1` Add test for gap identification.

## 7.2 Item bank

- [ ] `[critical]` Build minimum viable item bank for each supported launch grade/subject.
- [ ] `[critical]` Add item review status: draft, AI-generated, human-reviewed, approved, retired.
- [ ] `[high]` Add distractor quality review and explanation quality review.
- [ ] `[medium]` Tag items by misconception.
- [x] `[medium]` Add adaptive practice generator based on diagnostic gaps.
- [x] `[medium]` Add spaced repetition and retrieval practice.

Granular item-bank backlog:

- [ ] `P0` Build minimum viable item bank for each launch grade.
- [ ] `P0` Build minimum viable item bank for each launch subject.
- [ ] `P0` Add item review status `draft`.
- [ ] `P0` Add item review status `AI-generated`.
- [ ] `P0` Add item review status `human-reviewed`.
- [ ] `P0` Add item review status `approved`.
- [ ] `P0` Add item review status `retired`.
- [ ] `P1` Add item calibration workflow.
- [ ] `P1` Add item exposure limits.
- [ ] `P1` Add item reuse policy.
- [ ] `P1` Add item retirement workflow.
- [ ] `P1` Add item import/export tooling.
- [ ] `P2` Add item authoring interface.
- [ ] `P2` Add item analytics dashboard.

## 7.3 Diagnostic session lifecycle

- [x] `[critical]` Define mastery model combining diagnostic estimate, practice performance, recency, consistency, and confidence.
- [x] `[high]` Add progress timelines per learner.
- [x] `[high]` Add subject-level and topic-level mastery.
- [x] `[medium]` Add learning velocity, risk-of-falling-behind signal, and next-best-activity recommendation.
- [ ] `[research]` Evaluate Bayesian Knowledge Tracing or Deep Knowledge Tracing once enough usage data exists.

Granular diagnostic-session backlog:

- [ ] `P0` Implement diagnostic session start.
- [ ] `P0` Implement question serving.
- [ ] `P0` Implement answer submission.
- [ ] `P0` Implement ability update.
- [ ] `P0` Implement result retrieval.
- [ ] `P0` Implement consent check before diagnostic.
- [ ] `P0` Implement object authorization check before diagnostic.
- [ ] `P1` Add diagnostic pause/resume.
- [ ] `P1` Add diagnostic session recovery after disconnect.
- [ ] `P1` Add maximum item cap.
- [ ] `P1` Add minimum evidence threshold before final result.
- [ ] `P1` Add confidence interval.
- [ ] `P2` Add diagnostic review by educator.

## 7.4 Bias, quality, and fairness

- [ ] `P1` Add item bias review across language.
- [ ] `P1` Add item bias review across region.
- [ ] `P1` Add item bias review across socioeconomic context.
- [ ] `P1` Add distractor quality review.
- [ ] `P1` Add explanation quality review.
- [ ] `P1` Tag items by misconception.
- [ ] `P2` Add bias-review dashboard.
- [ ] `P2` Add educator sign-off process.

## 7.5 Mastery and remediation

- [ ] `P1` Define mastery model.
- [ ] `P1` Combine diagnostic estimate into mastery.
- [ ] `P1` Combine practice performance into mastery.
- [ ] `P1` Combine recency into mastery.
- [ ] `P1` Combine consistency into mastery.
- [ ] `P1` Combine confidence into mastery.
- [ ] `P1` Add topic-level mastery.
- [ ] `P1` Add subject-level mastery.
- [ ] `P1` Add progress timelines.
- [ ] `P1` Add adaptive practice generator.
- [ ] `P1` Add remediation based on misconception.
- [ ] `P2` Add spaced repetition.
- [ ] `P2` Add retrieval practice.
- [ ] `P2` Add learning velocity.
- [ ] `P2` Add risk-of-falling-behind signal.
- [ ] `P2` Add next-best-activity recommendation.
- [ ] `Research` Evaluate Bayesian Knowledge Tracing after sufficient data exists.
- [ ] `Research` Evaluate Deep Knowledge Tracing after sufficient data exists.

---

# 8. Frontend production readiness and UX

## 8.1 Environment and frontend security

- [ ] `P0` Separate browser-safe environment variables from server-only secrets.
- [ ] `P0` Ensure no secrets are exposed through `NEXT_PUBLIC_*`.
- [ ] `P0` Add frontend env validation script to CI.
- [ ] `P0` Add safe public API URL configuration.
- [ ] `P0` Add typed environment schema.
- [ ] `P1` Add staging frontend env validation.
- [ ] `P1` Add production frontend env validation.
- [ ] `P1` Document frontend environment variables.

## 8.2 API client

- [ ] `P0` Update typed API client to consume canonical PR-002R envelope.
- [ ] `P0` Normalize error handling against canonical error envelope.
- [ ] `P0` Add auth token handling.
- [ ] `P0` Add refresh handling.
- [ ] `P0` Add request ID propagation.
- [ ] `P0` Add typed response parsing.
- [ ] `P0` Add typed error parsing.
- [ ] `P1` Add retry behavior for safe idempotent requests.
- [ ] `P1` Add network-offline detection.
- [ ] `P1` Add stale-data handling.
- [ ] `P1` Add API client tests.

## 8.3 Auth and onboarding UX

- [ ] `P0` Complete guardian signup screen.
- [ ] `P0` Complete guardian login screen.
- [ ] `P0` Complete logout UX.
- [ ] `P0` Complete session-expiry UX.
- [ ] `P0` Complete password reset request screen.
- [ ] `P0` Complete password reset completion screen.
- [ ] `P0` Complete email verification UX.
- [ ] `P0` Complete learner profile creation.
- [ ] `P0` Complete grade selection.
- [ ] `P0` Complete subject selection.
- [ ] `P0` Complete parental consent capture.
- [ ] `P0` Complete onboarding completion route.
- [ ] `P1` Add onboarding progress indicator.
- [ ] `P1` Add recoverable onboarding state.
- [ ] `P1` Add onboarding E2E test.

## 8.4 Protected routes

- [ ] `P0` Add protected route guard for learner dashboard.
- [ ] `P0` Add protected route guard for parent dashboard.
- [ ] `P0` Add protected route guard for teacher dashboard.
- [ ] `P0` Add protected route guard for admin dashboard.
- [ ] `P0` Add role-based redirect rules.
- [ ] `P0` Add unauthorized state.
- [ ] `P0` Add forbidden state.
- [ ] `P1` Add tests for route guards.

## 8.5 Learner UX

- [ ] `P0` Complete learner dashboard.
- [ ] `P0` Show study plan.
- [ ] `P0` Show next recommended lesson.
- [ ] `P0` Show progress.
- [ ] `P0` Show streak if gamification enabled.
- [ ] `P0` Show weak topics.
- [ ] `P0` Show recommended next activity.
- [ ] `P0` Complete diagnostic question display.
- [ ] `P0` Complete diagnostic progress indicator.
- [ ] `P0` Complete diagnostic answer submission.
- [ ] `P0` Complete diagnostic result summary.
- [ ] `P0` Complete lesson explanation view.
- [ ] `P0` Complete worked example view.
- [ ] `P0` Complete practice question interaction.
- [ ] `P0` Complete hints.
- [ ] `P0` Complete answer reveal.
- [ ] `P0` Complete feedback capture.
- [ ] `P0` Complete report-content issue flow.
- [ ] `P1` Add pause/resume diagnostic UX.
- [ ] `P1` Add offline-friendly lesson state.
- [ ] `P2` Add learner personalization settings.

## 8.6 Parent/guardian UX

- [ ] `P0` Complete parent dashboard.
- [ ] `P0` Show child progress.
- [ ] `P0` Show consent status.
- [ ] `P0` Show recommended support actions.
- [ ] `P0` Show reports.
- [ ] `P0` Show privacy controls.
- [ ] `P0` Add data export request UI.
- [ ] `P0` Add erasure request UI.
- [ ] `P0` Add data correction request UI.
- [ ] `P0` Add processing restriction request UI.
- [ ] `P1` Add subscription/billing UI.
- [ ] `P1` Add consent renewal UI.
- [ ] `P1` Add notification preferences UI.
- [ ] `P2` Add weekly parent report view.
- [ ] `P2` Add “how to help at home” guidance.

## 8.7 Teacher/admin UX

- [ ] `P1` Build teacher dashboard if in beta scope.
- [ ] `P1` Build admin console if in beta scope.
- [ ] `P1` Build audit dashboard.
- [ ] `P1` Build content review queue.
- [ ] `P2` Build class-level diagnostics.
- [ ] `P2` Build intervention groups.
- [ ] `P2` Build topic heatmaps.
- [ ] `P2` Build curriculum coverage admin view.

## 8.8 Accessibility and mobile

- [ ] `P0` Meet WCAG 2.1 AA for signup.
- [ ] `P0` Meet WCAG 2.1 AA for login.
- [ ] `P0` Meet WCAG 2.1 AA for consent.
- [ ] `P0` Meet WCAG 2.1 AA for diagnostic.
- [ ] `P0` Meet WCAG 2.1 AA for lesson.
- [ ] `P0` Meet WCAG 2.1 AA for dashboards.
- [ ] `P0` Add keyboard navigation tests.
- [ ] `P0` Ensure sufficient color contrast.
- [ ] `P0` Add accessible form validation.
- [ ] `P0` Add semantic headings.
- [ ] `P0` Add landmarks.
- [ ] `P0` Add screen-reader friendly diagnostic questions.
- [ ] `P0` Make all learner flows usable on mobile.
- [ ] `P0` Make all parent flows usable on mobile.
- [ ] `P1` Add responsive layout tests.
- [ ] `P1` Add reduced-motion mode.
- [ ] `P1` Add dyslexia-friendly typography option.
- [ ] `P1` Add text resizing.
- [ ] `P2` Add audio narration if product scope supports it.

## 8.9 PWA and low-data mode

- [ ] `P1` Add or verify service worker.
- [ ] `P1` Add or verify manifest.
- [ ] `P1` Cache app shell.
- [ ] `P1` Add offline-friendly lesson content.
- [ ] `P1` Add offline messaging.
- [ ] `P1` Add compressed assets.
- [ ] `P1` Add low-data mode.
- [ ] `P1` Add PWA installability test.
- [ ] `P1` Add offline E2E test.
- [ ] `P2` Add offline feedback queue.
- [ ] `P2` Add sync-on-reconnect behavior.

---

# 9. Billing, subscriptions, payments, and monetization

## 9.1 Provider and architecture

- [ ] `P0` Decide production billing provider.
- [ ] `P0` Document billing provider decision in ADR.
- [ ] `P0` Document billing architecture.
- [ ] `P0` Define billing data model.
- [ ] `P0` Define subscription state machine.
- [ ] `P0` Define state `trial`.
- [ ] `P0` Define state `active`.
- [ ] `P0` Define state `past_due`.
- [ ] `P0` Define state `paused`.
- [ ] `P0` Define state `canceled`.
- [ ] `P0` Define state `expired`.
- [ ] `P1` Define sponsorship state if sponsored learner model is in scope.
- [ ] `P1` Define school-plan billing model if schools are in scope.

## 9.2 Webhooks

- [ ] `P0` Implement webhook signature verification.
- [ ] `P0` Implement webhook idempotency.
- [ ] `P0` Implement webhook replay protection.
- [ ] `P0` Implement webhook audit logging.
- [ ] `P0` Add webhook tests for valid signature.
- [ ] `P0` Add webhook tests for invalid signature.
- [ ] `P0` Add webhook tests for replay.
- [ ] `P0` Add webhook tests for duplicate event.
- [ ] `P0` Add webhook tests for out-of-order events.
- [ ] `P1` Add webhook dead-letter handling.
- [ ] `P1` Add webhook retry/backoff.
- [ ] `P1` Add webhook dashboard.

## 9.3 Pricing and product rules

- [ ] `P1` Define free tier.
- [ ] `P1` Define parent plan.
- [ ] `P1` Define school plan.
- [ ] `P1` Define sponsored learner plan.
- [ ] `P1` Define NGO/community plan.
- [ ] `P1` Define trial length.
- [ ] `P1` Define payment failure policy.
- [ ] `P1` Define cancellation policy.
- [ ] `P1` Define refund policy.
- [ ] `P1` Define data-access-after-cancellation policy.
- [ ] `P1` Add invoices.
- [ ] `P1` Add receipts.
- [ ] `P1` Add coupons.
- [ ] `P1` Add sponsorships.
- [ ] `P2` Add pricing admin config.

## 9.4 Billing UX and tests

- [ ] `P1` Add parent billing page.
- [ ] `P1` Add subscription status display.
- [ ] `P1` Add invoice history.
- [ ] `P1` Add cancel subscription flow.
- [ ] `P1` Add payment failure state.
- [ ] `P1` Add billing lifecycle tests.
- [ ] `P1` Add billing audit tests.
- [ ] `P2` Add billing metrics.
- [ ] `P2` Add churn metrics.

---

# 10. Notifications and communication

## 10.1 Provider selection

- [ ] `P0` Choose production email provider.
- [ ] `P0` Write ADR for notification provider.
- [ ] `P0` Document notification architecture.
- [ ] `P0` Document email domain/authentication requirements.
- [ ] `P1` Add provider sandbox for staging.
- [ ] `P1` Add provider failover plan if required.

## 10.2 Transactional templates

- [ ] `P0` Add email verification template.
- [ ] `P0` Add password reset template.
- [ ] `P0` Add consent request template.
- [ ] `P0` Add consent expiry template.
- [ ] `P0` Add diagnostic complete template.
- [ ] `P0` Add weekly parent report template.
- [ ] `P0` Add billing event template.
- [ ] `P0` Add security alert template.
- [ ] `P1` Add erasure request received template.
- [ ] `P1` Add erasure completed template.
- [ ] `P1` Add export ready template.
- [ ] `P1` Add account lockout template.
- [ ] `P1` Add template preview tests.
- [ ] `P1` Add localization plan for templates.

## 10.3 Delivery controls

- [ ] `P0` Add notification audit events.
- [ ] `P0` Add delivery tracking.
- [ ] `P0` Add retry/backoff.
- [ ] `P0` Add bounce handling.
- [ ] `P0` Add complaint handling.
- [ ] `P1` Add notification preferences.
- [ ] `P1` Add quiet hours.
- [ ] `P1` Add rate limits.
- [ ] `P1` Add unsubscribe rules where appropriate.
- [ ] `P1` Add failed delivery dashboard.
- [ ] `P2` Evaluate SMS after privacy impact review.
- [ ] `P2` Evaluate WhatsApp after privacy impact review.

---

# 11. Observability, metrics, logging, tracing, and alerting

## 11.1 Metrics

- [ ] `P0` Verify `/metrics` endpoint works.
- [ ] `P0` Add HTTP request count metric.
- [ ] `P0` Add HTTP latency metric.
- [ ] `P0` Add HTTP error-rate metric.
- [ ] `P0` Add status-code metric.
- [ ] `P0` Add dependency health metric.
- [ ] `P0` Add DB pool metric.
- [ ] `P0` Add Redis operation metric.
- [ ] `P0` Add background job metric.
- [ ] `P0` Add LLM call count metric.
- [ ] `P0` Add LLM latency metric.
- [ ] `P0` Add LLM token usage metric.
- [ ] `P0` Add LLM fallback metric.
- [ ] `P0` Add billing webhook metric.
- [ ] `P0` Add consent lifecycle metric.
- [ ] `P0` Add diagnostic session metric.
- [ ] `P0` Add lesson generation metric.
- [ ] `P0` Add backup success/failure metric.
- [ ] `P0` Add audit write failure metric.
- [ ] `P1` Add active learners metric.
- [ ] `P1` Add lesson completion metric.
- [ ] `P1` Add study-plan adherence metric.
- [ ] `P1` Add parent report open metric.
- [ ] `P1` Add consent conversion metric.
- [ ] `P1` Add churn metric if billing enabled.

## 11.2 Dashboards

- [ ] `P0` Build API dashboard.
- [ ] `P0` Build database dashboard.
- [ ] `P0` Build Redis dashboard.
- [ ] `P0` Build LLM provider dashboard.
- [ ] `P0` Build POPIA operations dashboard.
- [ ] `P0` Build learner journey dashboard.
- [ ] `P0` Build audit dashboard.
- [ ] `P0` Build backup/restore dashboard.
- [ ] `P1` Build billing dashboard.
- [ ] `P1` Build frontend error dashboard.
- [ ] `P1` Build business metrics dashboard.
- [ ] `P2` Build curriculum coverage dashboard.
- [ ] `P2` Build content quality dashboard.

## 11.3 Alerts

- [ ] `P0` Alert when API is down.
- [ ] `P0` Alert on readiness failure.
- [ ] `P0` Alert on high 5xx rate.
- [ ] `P0` Alert on high latency.
- [ ] `P0` Alert when DB unavailable.
- [ ] `P0` Alert when Redis unavailable.
- [ ] `P0` Alert on migration failure.
- [ ] `P0` Alert on audit write failure.
- [ ] `P0` Alert on consent enforcement failure.
- [ ] `P0` Alert on failed backup.
- [ ] `P0` Alert on failed security scan.
- [ ] `P1` Alert on LLM cost spike.
- [ ] `P1` Alert on LLM error spike.
- [ ] `P1` Alert on queue backlog.
- [ ] `P1` Alert on high 4xx rate.
- [ ] `P1` Alert on memory pressure.
- [ ] `P1` Alert on disk pressure.
- [ ] `P1` Alert on abnormal auth failures.
- [ ] `P1` Alert on webhook failure spike.

## 11.4 Logging

- [ ] `P0` Emit structured JSON logs in production.
- [ ] `P0` Include request ID in every backend log.
- [ ] `P0` Include user/actor pseudonymous identifier where safe.
- [ ] `P0` Scrub PII from logs.
- [ ] `P0` Scrub tokens from logs.
- [ ] `P0` Scrub cookies from logs.
- [ ] `P0` Scrub API keys from logs.
- [ ] `P0` Scrub passwords from logs.
- [ ] `P0` Scrub secrets from logs.
- [ ] `P1` Separate audit logs from operational logs.
- [ ] `P1` Add frontend error logging.
- [ ] `P1` Add log retention policy.
- [ ] `P1` Add log access policy.

## 11.5 Tracing

- [ ] `P1` Add OpenTelemetry to frontend.
- [ ] `P1` Add OpenTelemetry to API.
- [ ] `P1` Add OpenTelemetry to service layer.
- [ ] `P1` Add OpenTelemetry to repositories.
- [ ] `P1` Add OpenTelemetry to database calls.
- [ ] `P1` Add OpenTelemetry to Redis calls.
- [ ] `P1` Add OpenTelemetry to LLM provider calls.
- [ ] `P2` Correlate traces with audit events where safe.
- [ ] `P2` Add trace sampling policy.

---

# 12. CI/CD, infrastructure, deployment, Docker, and environments

## 12.1 CI correctness

- [ ] `P0` Fix CI branch assumptions to support `master`.
- [ ] `P0` Ensure image scan runs on `master`.
- [ ] `P0` Ensure production gates run for release tags from `master`.
- [ ] `P0` Ensure CI uses same dependency files as local dev.
- [ ] `P0` Ensure backend lint runs.
- [ ] `P0` Ensure backend type check runs.
- [ ] `P0` Ensure backend unit tests run.
- [ ] `P0` Ensure backend integration tests run.
- [ ] `P0` Ensure Alembic migration check runs.
- [ ] `P0` Ensure POPIA tests run.
- [ ] `P0` Ensure frontend tests run.
- [ ] `P0` Ensure frontend type check runs.
- [ ] `P0` Ensure frontend build runs.
- [ ] `P0` Ensure Playwright E2E runs.
- [ ] `P0` Ensure Docker image scan runs.
- [ ] `P0` Ensure dependency audit runs.
- [ ] `P0` Ensure secret scan runs.
- [ ] `P0` Ensure staging smoke tests run before production promotion.
- [ ] `P1` Add workflow concurrency to cancel stale runs.
- [ ] `P1` Upload backend test reports.
- [ ] `P1` Upload frontend test reports.
- [ ] `P1` Upload coverage reports.
- [ ] `P1` Upload security scan reports.
- [ ] `P1` Upload OpenAPI diff artifact.
- [ ] `P1` Upload SBOM artifact.

## 12.2 Deployment target alignment

- [ ] `P0` Decide production deployment target.
- [ ] `P0` Reconcile Azure Container Apps docs with Kubernetes deployment commands.
- [ ] `P0` If ACA is target, remove or archive Kubernetes production deployment from CI.
- [ ] `P0` If AKS is target, update architecture docs to say AKS.
- [ ] `P0` Align Docker Compose with chosen target.
- [ ] `P0` Align Bicep with chosen target.
- [ ] `P0` Align Kubernetes manifests with chosen target or mark future-only.
- [ ] `P0` Align runbooks with chosen target.
- [ ] `P1` Add staging deployment workflow.
- [ ] `P1` Add production promotion workflow.
- [ ] `P1` Add deployment rollback workflow.
- [ ] `P2` Add blue-green deployment.
- [ ] `P2` Add canary deployment.
- [ ] `P2` Add automated rollback on failed health checks.

## 12.3 Docker and images

- [ ] `P0` Verify API Dockerfile builds from clean checkout.
- [ ] `P0` Verify frontend Dockerfile builds from clean checkout.
- [ ] `P0` Verify docs Dockerfile target builds from clean checkout.
- [ ] `P0` Align CI build paths with Dockerfile names.
- [ ] `P0` Run images as non-root.
- [ ] `P0` Pin base images.
- [ ] `P0` Minimize runtime layers.
- [ ] `P0` Add healthcheck to API image.
- [ ] `P0` Add healthcheck to frontend image if applicable.
- [ ] `P1` Remove build tools from runtime image.
- [ ] `P1` Add OCI image label for commit SHA.
- [ ] `P1` Add OCI image label for version.
- [ ] `P1` Add OCI image label for build time.
- [ ] `P1` Add OCI image label for source repo.
- [ ] `P1` Add OCI image label for license.
- [ ] `P1` Generate SBOM.
- [ ] `P1` Scan SBOM.
- [ ] `P2` Add image signing.

## 12.4 Environment management

- [ ] `P0` Define local environment.
- [ ] `P0` Define test environment.
- [ ] `P0` Define staging environment.
- [ ] `P0` Define production environment.
- [ ] `P0` Add `docs/environment_variables.md`.
- [ ] `P0` Document every env var name.
- [ ] `P0` Document whether each env var is required.
- [ ] `P0` Document default value if any.
- [ ] `P0` Document environment scope.
- [ ] `P0` Document sensitivity.
- [ ] `P0` Document example value.
- [ ] `P0` Validate required env vars at startup.
- [ ] `P0` Fail fast on missing production secrets.
- [ ] `P0` Store production secrets in Azure Key Vault or equivalent.
- [ ] `P1` Add secret rotation procedure.
- [ ] `P1` Add environment drift detection.
- [ ] `P1` Add staging env validation.
- [ ] `P1` Add production env validation.

## 12.5 Staging

- [ ] `P0` Provision staging environment.
- [ ] `P0` Configure staging database.
- [ ] `P0` Configure staging Redis.
- [ ] `P0` Configure staging secrets.
- [ ] `P0` Configure staging frontend.
- [ ] `P0` Configure staging API.
- [ ] `P0` Use synthetic data only in staging.
- [ ] `P0` Run smoke tests against staging.
- [ ] `P0` Run Playwright against staging.
- [ ] `P0` Run POPIA tests against staging-safe data.
- [ ] `P0` Run backup/restore drill against staging.
- [ ] `P0` Run security scan against staging.
- [ ] `P1` Run load smoke test against staging.
- [ ] `P0` Produce staging acceptance report.

---

# 13. Backup, restore, and disaster recovery

## 13.1 PostgreSQL backups

- [ ] `P0` Enable automated PostgreSQL backups.
- [ ] `P0` Encrypt PostgreSQL backups.
- [ ] `P0` Store backups in separate failure domain.
- [ ] `P0` Define daily retention.
- [ ] `P0` Define weekly retention.
- [ ] `P0` Define monthly retention.
- [ ] `P0` Add backup success metric.
- [ ] `P0` Add backup failure metric.
- [ ] `P0` Add backup failure alert.
- [ ] `P0` Document backup configuration.
- [ ] `P0` Add backup runbook.
- [ ] `P1` Add backup integrity verification.
- [ ] `P1` Add backup cost monitoring.

## 13.2 Restore tests

- [ ] `P0` Perform restore test into clean environment.
- [ ] `P0` Validate guardian records after restore.
- [ ] `P0` Validate learner records after restore.
- [ ] `P0` Validate consent states after restore.
- [ ] `P0` Validate audit records after restore.
- [ ] `P0` Validate billing states after restore.
- [ ] `P0` Validate diagnostic records after restore.
- [ ] `P0` Validate lesson metadata after restore.
- [ ] `P0` Validate Alembic version after restore.
- [ ] `P0` Record restore duration.
- [ ] `P0` Record restore evidence.
- [ ] `P1` Automate restore test in staging on schedule.

## 13.3 RPO/RTO and DR

- [ ] `P0` Define RPO.
- [ ] `P0` Define RTO.
- [ ] `P0` Create `docs/disaster_recovery.md`.
- [ ] `P0` Add restore runbook.
- [ ] `P0` Add failover runbook.
- [ ] `P0` Add rollback runbook.
- [ ] `P0` Add emergency contacts.
- [ ] `P0` Add disaster declaration criteria.
- [ ] `P1` Run disaster recovery tabletop exercise.
- [ ] `P1` Add post-DR validation checklist.
- [ ] `P2` Add cross-region recovery plan if required.

## 13.4 Redis recoverability

- [ ] `P1` Decide Redis recoverability model.
- [ ] `P1` Document whether Redis is disposable.
- [ ] `P1` Document token revocation impact if Redis is lost.
- [ ] `P1` Document cache impact if Redis is lost.
- [ ] `P1` Document job status impact if Redis is lost.
- [ ] `P1` Document rate-limit impact if Redis is lost.
- [ ] `P1` Add Redis outage test.
- [ ] `P1` Add degraded-mode behavior for Redis outage.
- [ ] `P2` Add Redis failover test if using managed failover.

---

# 14. Testing, release evidence, and quality gates

## 14.1 Backend tests

- [ ] `P0` Maintain backend unit coverage at or above 80%.
- [ ] `P0` Add unit tests for API envelope.
- [ ] `P0` Add unit tests for error contract.
- [ ] `P0` Add unit tests for auth security helpers.
- [ ] `P0` Add unit tests for token revocation.
- [ ] `P0` Add unit tests for consent policy.
- [ ] `P0` Add unit tests for LLM PII redaction.
- [ ] `P0` Add unit tests for CAPS validator.
- [ ] `P0` Add unit tests for IRT engine.
- [ ] `P0` Add unit tests for repository layer.
- [ ] `P0` Add integration tests for auth flows.
- [ ] `P0` Add integration tests for consent flows.
- [ ] `P0` Add integration tests for POPIA workflows.
- [ ] `P0` Add integration tests for diagnostics.
- [ ] `P0` Add integration tests for lesson generation.
- [ ] `P0` Add integration tests for billing webhooks.
- [ ] `P0` Add integration tests for audit trail.
- [ ] `P0` Add smoke tests for `/health`.
- [ ] `P0` Add smoke tests for `/ready`.
- [ ] `P0` Add smoke tests for `/metrics`.
- [ ] `P0` Add smoke tests for `/docs`.
- [ ] `P0` Add smoke tests for `/openapi.json`.

## 14.2 Frontend tests

- [ ] `P0` Maintain frontend coverage at or above agreed threshold.
- [ ] `P0` Add component tests for signup.
- [ ] `P0` Add component tests for login.
- [ ] `P0` Add component tests for consent.
- [ ] `P0` Add component tests for diagnostic.
- [ ] `P0` Add component tests for lesson view.
- [ ] `P0` Add component tests for parent dashboard.
- [ ] `P0` Add tests for API client envelope parsing.
- [ ] `P0` Add tests for API client error parsing.
- [ ] `P0` Add tests for route guards.
- [ ] `P1` Add tests for loading states.
- [ ] `P1` Add tests for empty states.
- [ ] `P1` Add tests for failure states.
- [ ] `P1` Add tests for retry states.
- [ ] `P1` Add mobile viewport tests.
- [ ] `P1` Add accessibility tests.
- [ ] `P1` Add PWA/offline tests.

## 14.3 E2E tests

- [ ] `P0` Add Playwright E2E for guardian signup.
- [ ] `P0` Add Playwright E2E for learner profile creation.
- [ ] `P0` Add Playwright E2E for consent capture.
- [ ] `P0` Add Playwright E2E for diagnostic session.
- [ ] `P0` Add Playwright E2E for study plan.
- [ ] `P0` Add Playwright E2E for lesson completion.
- [ ] `P0` Add Playwright E2E for parent report.
- [ ] `P0` Add Playwright E2E for POPIA export request.
- [ ] `P0` Add Playwright E2E for erasure request.
- [ ] `P1` Add Playwright E2E for billing subscription if billing in beta scope.
- [ ] `P1` Add Playwright E2E for password reset.
- [ ] `P1` Add Playwright E2E for session expiry.
- [ ] `P1` Add Playwright E2E for mobile viewport.

## 14.4 Security tests

- [ ] `P0` Run SAST.
- [ ] `P0` Run Python dependency audit.
- [ ] `P0` Run npm dependency audit.
- [ ] `P0` Run Docker image scan.
- [ ] `P0` Run secrets scan.
- [ ] `P0` Add CORS tests.
- [ ] `P0` Add CSRF tests.
- [ ] `P0` Add cookie policy tests.
- [ ] `P0` Add rate-limit tests.
- [ ] `P0` Add object-authorization tests.
- [ ] `P0` Add consent-bypass tests.
- [ ] `P1` Run penetration-test checklist.
- [ ] `P1` Add abuse-case tests.

## 14.5 Release evidence

- [ ] `P0` Generate backend image digest.
- [ ] `P0` Generate frontend build/image digest.
- [ ] `P0` Record migration revision.
- [ ] `P0` Generate changelog entry.
- [ ] `P0` Generate SBOM.
- [ ] `P0` Attach backend test reports.
- [ ] `P0` Attach frontend test reports.
- [ ] `P0` Attach coverage reports.
- [ ] `P0` Attach security scan reports.
- [ ] `P0` Attach OpenAPI schema hash.
- [ ] `P0` Attach deployment manifest.
- [ ] `P0` Attach rollback plan.
- [ ] `P0` Attach repo-state verification.
- [ ] `P0` Attach staging acceptance report.
- [ ] `P0` Block production promotion if evidence bundle missing.
- [ ] `P1` Add `scripts/build_release_evidence.py` if not complete.
- [ ] `P1` Add release evidence validation script.

---

# 15. Security posture and threat modeling

## 15.1 Security headers, CORS, and CSRF

- [ ] `P0` Verify security headers in staging.
- [ ] `P0` Verify HSTS where TLS is terminated.
- [ ] `P0` Verify `X-Content-Type-Options`.
- [ ] `P0` Verify frame-ancestors or X-Frame-Options.
- [ ] `P0` Verify CSP if feasible.
- [ ] `P0` Verify production CORS allowlist.
- [ ] `P0` Remove wildcard origins in production.
- [ ] `P0` Define CSRF strategy for cookie-based auth.
- [ ] `P0` Add CSRF tests.
- [ ] `P1` Add security-header tests.
- [ ] `P1` Document browser security model.

## 15.2 Secrets

- [ ] `P0` Run gitleaks on full history.
- [ ] `P0` Run detect-secrets or equivalent.
- [ ] `P0` Verify no real secrets remain active from git history.
- [ ] `P0` Rotate any exposed or possibly exposed secrets.
- [ ] `P0` Store production secrets in Key Vault or equivalent.
- [ ] `P0` Ensure local `.env` is ignored.
- [ ] `P0` Ensure `.env.example` has no real secrets.
- [ ] `P1` Add secret rotation schedule.
- [ ] `P1` Add secret access audit.
- [ ] `P1` Add emergency secret rotation runbook.

## 15.3 Threat model

- [ ] `P1` Create `docs/threat_model.md`.
- [ ] `P1` Model learner data exposure.
- [ ] `P1` Model consent bypass.
- [ ] `P1` Model account takeover.
- [ ] `P1` Model prompt injection.
- [ ] `P1` Model LLM PII leakage.
- [ ] `P1` Model billing webhook replay.
- [ ] `P1` Model data export abuse.
- [ ] `P1` Model admin misuse.
- [ ] `P1` Model audit tampering.
- [ ] `P1` Model dependency supply-chain compromise.
- [ ] `P1` Add mitigations for each threat.
- [ ] `P1` Add tests or controls for high-risk threats.
- [ ] `P2` Review threat model every release.

## 15.4 Pen-test readiness

- [ ] `P1` Finalize penetration-test checklist.
- [ ] `P1` Run auth pen-test checks.
- [ ] `P1` Run authorization pen-test checks.
- [ ] `P1` Run POPIA workflow abuse checks.
- [ ] `P1` Run API input validation checks.
- [ ] `P1` Run rate-limit abuse checks.
- [ ] `P1` Run LLM prompt-injection checks.
- [ ] `P1` Run file/export abuse checks.
- [ ] `P1` Run admin access checks.
- [ ] `P1` Record findings.
- [ ] `P1` Fix critical/high findings before beta.
- [ ] `P2` Schedule recurring security scans.

---

# 16. Incident response, operations, and support

## 16.1 Incident response docs

- [ ] `P0` Create `docs/incident_response.md`.
- [ ] `P0` Define incident severity levels.
- [ ] `P0` Define incident commander role.
- [ ] `P0` Define escalation contacts.
- [ ] `P0` Define security incident workflow.
- [ ] `P0` Define learner data exposure workflow.
- [ ] `P0` Define auth outage workflow.
- [ ] `P0` Define billing outage workflow.
- [ ] `P0` Define AI content safety incident workflow.
- [ ] `P0` Define data corruption workflow.
- [ ] `P0` Define availability outage workflow.
- [ ] `P0` Define compliance request failure workflow.
- [ ] `P0` Add breach response procedure.
- [ ] `P0` Add postmortem template.
- [ ] `P1` Run incident tabletop exercise.
- [ ] `P1` Record tabletop results.
- [ ] `P1` Fix gaps found in tabletop.

## 16.2 Emergency controls

- [ ] `P0` Add ability to disable lesson generation.
- [ ] `P0` Add ability to revoke all sessions.
- [ ] `P0` Add ability to disable an LLM provider.
- [ ] `P0` Add ability to freeze billing webhooks.
- [ ] `P0` Add maintenance mode.
- [ ] `P0` Add ability to pause data exports during incident if legally permissible.
- [ ] `P0` Add ability to disable new signups.
- [ ] `P0` Audit all emergency actions.
- [ ] `P1` Add admin UI or runbook commands for emergency actions.
- [ ] `P1` Test emergency actions in staging.

## 16.3 Support workflows

- [ ] `P1` Create support runbook for failed login.
- [ ] `P1` Create support runbook for consent issue.
- [ ] `P1` Create support runbook for data export request.
- [ ] `P1` Create support runbook for erasure request.
- [ ] `P1` Create support runbook for lesson quality complaint.
- [ ] `P1` Create support runbook for billing dispute.
- [ ] `P1` Create support runbook for parent account recovery.
- [ ] `P1` Add support escalation labels.
- [ ] `P1` Add support SLA targets.
- [ ] `P2` Build support dashboard.

---

# 17. Documentation, ADRs, and claim discipline

## 17.1 Required production docs

- [ ] `P0` Update `README.md`.
- [ ] `P0` Update `docs/project_status.md`.
- [ ] `P0` Add or update `docs/api_v2.md`.
- [ ] `P0` Commit `docs/openapi.json`.
- [ ] `P0` Add or update `docs/environment_variables.md`.
- [ ] `P0` Add or update `docs/release_checklist.md`.
- [ ] `P0` Add or update `docs/repository_governance.md`.
- [ ] `P0` Add or update `SECURITY.md`.
- [ ] `P0` Add or update `docs/incident_response.md`.
- [ ] `P0` Add or update `docs/disaster_recovery.md`.
- [ ] `P0` Add or update `docs/popia_compliance.md`.
- [ ] `P0` Add or update `docs/data_inventory.md`.
- [ ] `P0` Add or update `docs/data_retention_policy.md`.
- [ ] `P0` Add or update `docs/subprocessor_register.md`.
- [ ] `P1` Add or update `docs/testing_strategy.md`.
- [ ] `P1` Add or update `docs/deployment.md`.
- [ ] `P1` Add or update `docs/observability.md`.

## 17.2 ADRs

- [ ] `P1` Write ADR for modular monolith.
- [ ] `P1` Write ADR for FastAPI V2.
- [ ] `P1` Write ADR for Next.js frontend.
- [ ] `P1` Write ADR for PostgreSQL audit ledger.
- [ ] `P1` Write ADR for Redis revocation/job state.
- [ ] `P1` Write ADR for LLM provider abstraction.
- [ ] `P1` Write ADR for POPIA-first design.
- [ ] `P1` Write ADR for CAPS alignment.
- [ ] `P1` Write ADR for production deployment target.
- [ ] `P1` Write ADR for billing provider.
- [ ] `P1` Write ADR for notification provider.
- [ ] `P1` Write ADR for observability stack.
- [ ] `P1` Write ADR for business-logic location.
- [ ] `P1` Write ADR for API envelope.
- [ ] `P1` Write ADR for OpenAPI contract governance.

## 17.3 Claim discipline

- [ ] `P0` Remove or correct “V1 fully deleted” if legacy shims/archive remain.
- [ ] `P0` Remove or correct “no microservices” if inference sidecar remains.
- [ ] `P0` Remove or correct “ACA target” vs Kubernetes deployment mismatch.
- [ ] `P0` Remove or correct “production-ready” unless all release gates pass.
- [ ] `P0` Avoid claiming full CAPS coverage until validated.
- [ ] `P0` Avoid claiming full POPIA compliance until tests/legal docs pass.
- [ ] `P0` Label claims as `implemented`.
- [ ] `P0` Label claims as `tested`.
- [ ] `P0` Label claims as `CI verified`.
- [ ] `P0` Label claims as `staging verified`.
- [ ] `P0` Label claims as `production verified`.
- [ ] `P0` Label claims as `planned`.
- [ ] `P0` Label claims as `blocked`.
- [ ] `P1` Add docs linting to CI.
- [ ] `P1` Add docs link checker to CI.
- [ ] `P1` Add docs owner review requirement.

---

# 18. Beta launch, staging acceptance, and product scope

## 18.1 Staging acceptance

- [ ] `P0` Deploy staging environment.
- [ ] `P0` Use synthetic data only in staging.
- [ ] `P0` Run backend smoke tests against staging.
- [ ] `P0` Run frontend Playwright tests against staging.
- [ ] `P0` Run POPIA workflows against staging.
- [ ] `P0` Run backup/restore drill against staging.
- [ ] `P0` Run security scan against staging.
- [ ] `P0` Run load smoke test against staging.
- [ ] `P0` Verify dashboards in staging.
- [ ] `P0` Verify alerts in staging.
- [ ] `P0` Verify incident runbook against staging.
- [ ] `P0` Produce staging acceptance report.
- [ ] `P0` Add staging acceptance report to release evidence bundle.

## 18.2 Public beta scope

- [ ] `P0` Define supported grades.
- [ ] `P0` Define supported subjects.
- [ ] `P0` Define supported languages.
- [ ] `P0` Define supported lesson types.
- [ ] `P0` Define supported diagnostic flows.
- [ ] `P0` Define supported payment modes.
- [ ] `P0` Define unsupported features.
- [ ] `P0` Define pilot user count.
- [ ] `P0` Define parent consent onboarding script.
- [ ] `P0` Define support escalation path.
- [ ] `P0` Define feedback collection process.
- [ ] `P0` Define AI-content issue-reporting flow.
- [ ] `P0` Define manual content review SLA.
- [ ] `P0` Define go/no-go criteria.
- [ ] `P0` Hold go/no-go review.
- [ ] `P0` Record go/no-go decision.

## 18.3 Release and rollback

- [ ] `P0` Generate release evidence bundle.
- [ ] `P0` Create signed release tag.
- [ ] `P0` Deploy release candidate to staging.
- [ ] `P0` Run smoke tests.
- [ ] `P0` Test rollback.
- [ ] `P0` Document rollback result.
- [ ] `P0` Approve production promotion only if all release blockers pass.
- [ ] `P1` Add post-release monitoring checklist.
- [ ] `P1` Add first-24-hours monitoring schedule.

---

# 19. Roadmap after production-readiness baseline

## 19.1 Product expansion

- [ ] `P2` Add teacher dashboard if not in beta scope.
- [ ] `P2` Add classroom diagnostics.
- [ ] `P2` Add class intervention groups.
- [ ] `P2` Add teacher-facing CAPS coverage export.
- [ ] `P2` Add parent co-pilot weekly guidance.
- [ ] `P2` Add sponsored learner model.
- [ ] `P2` Add NGO/community partnership workflows.
- [ ] `P2` Add printable worksheets.
- [ ] `P2` Add offline lesson packs.
- [ ] `P3` Add all 11 official South African languages.
- [ ] `P3` Add advanced analytics for learning velocity.
- [ ] `P3` Add curriculum graph visualization.

## 19.2 Technical scale

- [ ] `P2` Add load testing suite.
- [ ] `P2` Define concurrency targets.
- [ ] `P2` Define learner journey SLOs.
- [ ] `P2` Define LLM latency SLOs.
- [ ] `P2` Define diagnostic latency SLOs.
- [ ] `P2` Add autoscaling policy.
- [ ] `P2` Add cache hit-rate goals.
- [ ] `P2` Add cost-per-lesson metric.
- [ ] `P3` Split inference service only if load evidence demands it.
- [ ] `P3` Consider diagnostics service split only if load evidence demands it.

## 19.3 Research

- [ ] `Research` Investigate retrieval-augmented generation using approved CAPS content only.
- [ ] `Research` Investigate local/smaller models.
- [ ] `Research` Investigate Bayesian Knowledge Tracing.
- [ ] `Research` Investigate Deep Knowledge Tracing.
- [ ] `Research` Conduct educator review of generated lessons.
- [ ] `Research` Conduct parent usability interviews.
- [ ] `Research` Conduct learner usability testing with consent.
- [ ] `Research` Conduct low-bandwidth UX testing.

---

# 20. Final release-blocker checklist

All items below must be complete before public beta or production use with real learner data.

```text
[ ] Latest repo head verified by merge marker and SHA
[ ] Canonical repo/branch/release authority documented
[ ] PR-002R implemented and verified
[ ] app.api_v2 imports cleanly
[ ] app/api_v2.py router-registration defect fixed
[ ] /health passes
[ ] /ready passes with real dependencies
[ ] /metrics exposes Prometheus metrics
[ ] /docs loads
[ ] /openapi.json loads
[ ] OpenAPI schema committed
[ ] OpenAPI drift check passes
[ ] API response envelope standardized
[ ] API error envelope standardized
[ ] Legacy routes excluded
[ ] Auth flows pass
[ ] Token rotation/revocation verified
[ ] Cookie policy verified
[ ] Object-level authorization tests pass
[ ] Consent gate check script passes
[ ] Consent bypass negative tests pass
[ ] POPIA export workflow tested
[ ] POPIA erasure workflow tested
[ ] POPIA correction workflow tested
[ ] POPIA restriction workflow tested
[ ] Audit chain verified
[ ] Audit completeness tests pass
[ ] LLM PII sweep passes
[ ] AI output validators pass
[ ] Independent answer-key checking implemented
[ ] CAPS topic map MVP validated
[ ] CAPS claims reviewed and limited to evidence
[ ] Diagnostic IRT tests pass
[ ] Minimum item bank exists for launch scope
[ ] Database migrations pass from empty DB
[ ] Schema integrity validation passes
[ ] Backup/restore drill completed
[ ] RPO/RTO documented
[ ] CI branch/deployment contradictions resolved
[ ] Docker images build cleanly
[ ] Docker images run as non-root
[ ] Production secrets stored outside repo
[ ] Security scans pass or have accepted risk records
[ ] Staging deployment completed
[ ] Staging smoke tests pass
[ ] Playwright E2E passes against staging
[ ] Dashboards live
[ ] Alerts live
[ ] Incident response runbook complete
[ ] Tabletop exercise completed
[ ] Privacy Policy drafted and reviewed
[ ] Terms of Service drafted and reviewed
[ ] Parent Consent Notice drafted and reviewed
[ ] Child-friendly Privacy Notice drafted and reviewed
[ ] Release evidence bundle generated
[ ] Rollback tested
[ ] Go/no-go review completed
```

---

## Execution recommendation

Execute in this order:

1. **PR-002R runtime/API contract baseline**
2. **Security and POPIA negative tests**
3. **CI/CD and deployment target alignment**
4. **Database migration and backup/restore proof**
5. **AI/CAPS validation and diagnostic item-bank proof**
6. **Frontend E2E, accessibility, and parent/learner journeys**
7. **Staging acceptance, incident response, and release evidence**
8. **Controlled public beta**

This TODO intentionally favors evidence over optimism. EduBoost V2 should only claim production readiness where code, tests, CI, staging, and operational runbooks prove it.
