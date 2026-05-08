# EduBoost V2 Outstanding TODOs (as of 2026-05-08)

This file lists all items from the main TODO list that remain **pending** after a full audit of the integrated codebase and documentation. Items are tracked as checkboxes and grouped by priority to help triage and execution.

---

## High Priority

### 0. Production Definition of Done
- [x] Add graceful degraded-mode behavior for optional dependencies such as LLM providers, analytics, email, or billing.
- [x] Automated database backups are enabled, encrypted, monitored, and restore-tested.
- [x] Security headers, CORS, cookie policy, JWT policy, and rate limits are verified in staging.
- [x] Logs, metrics, traces, alerts, and dashboards are live before real learner data is processed.
- [x] Incident response, security disclosure, data breach handling, and learner-data escalation procedures are documented.
- [x] POPIA consent, export, erasure, retention, audit, and LLM PII-redaction workflows are tested end-to-end.

### 3. Database, Persistence, and Migrations
- [x] Add partial indexes for active consent, active subscriptions, non-revoked sessions, and incomplete jobs.
- [x] Review transaction boundaries for all critical workflows.
- [ ] Add slow-query logging in staging and production.
- [ ] Add performance tests for all major endpoints.
- [x] Document rollback strategy for every destructive migration.
- [x] Add migration naming convention.
- [x] Require backup, staging dry-run, validation script, and rollback plan for migrations touching learner/guardian data.
- [x] Add migration smoke tests using production-like data volume.
- [x] Add repository tests for every persistence path.
- [x] Ensure repository methods do not expose raw ORM objects to API responses.
- [x] Standardize repository method names.
- [x] Use pagination and deterministic sorting for all list endpoints.
- [ ] Use cursor pagination for high-volume event streams.

### 4. Authentication, Authorization, and Session Security
- [x] Verify signup, login, refresh, logout, email verification, and password reset end-to-end.
- [x] Add rate limiting for login, signup, refresh, password reset, and verification endpoints.
- [x] Add account lockout or risk-based throttling after repeated failed attempts.
- [x] Add session inventory and “log out all devices.”
- [x] Add optional MFA for parents, teachers, admins, and support operators.
- [ ] Add passkeys/WebAuthn later as a trust differentiator.
- [x] Add JWT signing-key rotation with `kid`, current/previous keys, rotation schedule, and emergency revoke-all procedure.
- [x] Verify cookie settings: `HttpOnly`, `Secure`, correct `SameSite`, correct domain, correct path, and no JavaScript-readable tokens.
- [x] Add object-level authorization tests.
- [x] Add policy tests for every router.
- [x] Move from basic RBAC to policy-based access control for sensitive workflows.
- [x] Add tightly audited admin impersonation only if absolutely required.

### 5. POPIA, Privacy, and Learner Data Protection
- [x] Add negative tests proving consent bypass is impossible for all sensitive workflows.
- [x] Add consent renewal workflow.
- [x] Add consent withdrawal workflow.
- [x] Add consent versioning tied to a specific privacy notice version.
- [ ] Add school-mediated consent model if institutional deployments enter scope.
- [x] Implement export, erasure, correction, and restriction workflows for data subject rights.
- [x] Add status tracking and SLA targets for export/erasure requests.
- [x] Add admin review queue for erasure requests.
- [x] Provide machine-readable export formats.
- [x] Add audit events for all major actions.
- [x] Add immutable retention rules for audit records.
- [ ] Build internal audit dashboard.
- [x] Add automated audit completeness tests.

### 10. DevOps, Infrastructure, and Deployment
- [x] Add image labels to Docker images.
- [x] Add horizontal autoscaling, network policies, workload identity, and rollout strategy.
- [x] Add blue-green or canary deployment.
- [x] Add automated rollback on failed health checks.
- [x] Store production secrets in Azure Key Vault or equivalent.
- [x] Rotate secrets regularly.
- [ ] Add environment drift detection.

## Medium Priority

### 1. Repository Governance and Hygiene
- [x] Protect.*master`/`main`: require PR review, required checks, no force-push, no branch deletion, and signed commits if feasible.
- [x] Add.*CODEOWNERS` for backend, frontend, infrastructure, security, compliance, curriculum, and docs.
- [x] Add issue templates: bug, feature, security redirect, compliance concern, accessibility issue, curriculum issue, incorrect content, production incident.
- [x] Add PR template with checkboxes for tests, docs, migrations, POPIA impact, security impact, accessibility impact, analytics impact, deployment impact, and rollback plan.
- [x] Audit dependency files and decide canonical dependency paths for runtime, dev, docs, and ML extras.
- [x] Remove duplicate or stale root dependency files, or clearly mark them as compatibility aliases.
- [ ] Add `docs/adr/` and write ADRs for modular monolith, FastAPI V2, Next.js frontend, PostgreSQL audit ledger, Redis revocation, LLM provider abstraction, POPIA-first design, and CAPS alignment.
- [x] Add markdown linting and docs link checking to CI.

### 2. Backend Architecture
- [ ] Ensure `app/api/main.py` remains a compatibility shim only and cannot diverge from V2 behavior.
- [ ] Add a regression test that imports the V2 app using every documented deployment command.
- [ ] Add tests proving legacy-only routes are not accidentally exposed as production APIs.
- [ ] Add OpenAPI diff checks in PRs.
- [x] Ensure routers are thin: request validation, auth/consent dependencies, service call, response mapping.
- [x] Move business logic out of routers into services or bounded modules.
- [x] Define service contracts for all major domains.
- [ ] Collapse duplicate service concepts between `app/services/*_service_v2.py` and `app/modules/*/service.py`.
- [ ] Decide canonical business-logic location.
- [ ] Remove metaphor-layer ambiguity from active code.
- [ ] Keep metaphor names only for storytelling/docs if useful; use domain names in code.
- [x] Enforce import boundaries: routers → services → repositories/domain/core; repositories → models/database; domain should not depend on infrastructure.
- [x] Standardize FastAPI dependencies for all cross-cutting concerns.
- [x] Replace ad-hoc service construction with dependency providers.
- [x] Add test dependency overrides for all major services.
- [x] Add request-scoped correlation ID propagation.

### 9. API Design and Integrations
- [ ] Add OpenAPI tags, summaries, examples, and versioning policy.
- [ ] Add idempotency keys for critical requests.
- [x] Add pagination metadata for all list endpoints.
- [ ] Define pricing for all plans.
- [ ] Add billing lifecycle tests.
- [ ] Add invoices/receipts, coupons, sponsorships, and data-access-after-cancellation policy.
- [ ] Choose production email provider.
- [ ] Add transactional templates for all notifications.
- [ ] Add notification preferences and delivery tracking.
- [ ] Add SMS/WhatsApp notifications.
- [ ] Add notification rate limits and quiet hours.

## Low Priority

### 6. AI, LLM Safety, and Lesson Generation
- [x] Add provider fallback, timeout, retry, circuit breaker, and budget guardrails.
- [x] Log LLM metadata without logging sensitive prompt content.
- [x] Add prompt-template version control and deterministic mock provider for tests.
- [ ] Add golden prompt tests for every supported grade/subject/topic.
- [x] Define lesson output contract.
- [ ] Require generated answer keys to be independently checked.
- [ ] Add validators for content quality.
- [ ] Add human review queue for low-confidence content.
- [ ] Build content quality score.
- [ ] Create lesson regression suite.
- [ ] Add model comparison harness.
- [x] Create canonical CAPS topic map.
- [x] Add validators for CAPS topic references.
- [ ] Add curriculum coverage dashboards.
- [x] Detect topics without lessons or quality-reviewed content.
- [ ] Add teacher-facing CAPS coverage export.
- [ ] Add alignment confidence score per lesson.
- [ ] Version curriculum maps.
- [x] Add.*explain it my way” lesson variants.
- [x] Add adaptive remediation.
- [ ] Add parent explanation mode.
- [ ] Add teacher insight mode.
- [ ] Add low-bandwidth AI mode.
- [ ] Investigate retrieval-augmented generation.
- [ ] Investigate local/smaller models.

### 7. Diagnostics, Assessment, and Learning Science
- [ ] Add item calibration workflow.
- [ ] Add item exposure limits.
- [ ] Add diagnostic session recovery.
- [ ] Add confidence intervals for ability estimates.
- [ ] Add item bias review.
- [ ] Build minimum viable item bank.
- [ ] Add item review status.
- [ ] Add distractor and explanation quality review.
- [ ] Tag items by misconception.
- [ ] Add adaptive practice generator.
- [ ] Add spaced repetition and retrieval practice.
- [ ] Define mastery model.
- [ ] Add progress timelines.
- [ ] Add subject/topic-level mastery.
- [ ] Add learning velocity, risk-of-falling-behind, and next-best-activity recommendation.
- [ ] Evaluate Bayesian/Deep Knowledge Tracing.

### 8. Frontend Production Readiness
- [x] Add bundle analysis, route-level code splitting, and performance budgets.
- [x] Build study-plan UX, teacher dashboard, and admin console.
- [x] Add reduced-motion mode, dyslexia-friendly typography, text resizing, and audio narration.
- [x] Add PWA/low-data mode.

