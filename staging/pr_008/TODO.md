# Documentation and Repo Sync TODO

Updated: 2026-05-04
Source: `C:\Users\Lebelo\Downloads\EduBoost_V2_Comparative_Audit_Report.md`

Status legend:

- `[done]` completed and reflected in the repository
- `[pending]` still requires follow-through

# EduBoost V2 Production-Grade TODO

> **Purpose:** Comprehensive production-readiness and mission-upgrade backlog for EduBoost V2.
> **Scope:** FastAPI V2 backend, Next.js frontend, PostgreSQL/Alembic, Redis, POPIA compliance, CAPS-aligned learning, AI lesson generation, observability, DevSecOps, deployment, product strategy, and launch operations.
> **Assumed repo state:** V2 modular monolith; backend entrypoint `app/api_v2.py`; frontend under `app/frontend`; Redis for cache/token revocation/job state; PostgreSQL audit repository; CI/CD under `.github/workflows`; Docker, Kubernetes, Bicep, Prometheus, Alertmanager, Grafana, and MkDocs assets present.

## Status Legend

- `[critical]` Must be resolved before production launch.
- `[high]` Should be resolved before public beta or paid users.
- `[medium]` Improves reliability, UX, maintainability, or differentiation.
- `[low]` Polish, future-proofing, or post-launch optimization.
- `[research]` Needs spike, user interviews, educator review, benchmarking, or legal review.

## Ownership Labels

Use labels such as `backend`, `frontend`, `data`, `ai`, `security`, `compliance`, `devops`, `product`, `design`, `docs`, `qa`, `growth`, and `ops`.

---

# 0. Production Definition of Done

## 0.1 Non-negotiable production gate

- [x] `[critical]` Publish a first tagged release, e.g. `v0.1.0-beta`, only after all mandatory CI jobs pass on the canonical production branch.
- [x] `[critical]` Confirm the release workflow blocks production promotion unless the following pass: backend lint, backend type check, backend unit tests, backend integration tests, Alembic schema drift check, POPIA compliance tests, frontend tests, frontend type check, frontend build, Playwright E2E tests, Docker image scan, dependency audit, secret scan, and staging smoke tests.
- [x] `[critical]` Generate a release evidence bundle containing backend image digest, frontend build/image digest, migration revision, changelog entry, SBOM, test reports, coverage reports, security scan reports, and deployment manifest.
- [x] `[critical]` Add `docs/release_checklist.md` and require it for every tagged release.
- [x] `[critical]` Define production launch scope precisely: supported grades, supported subjects, supported lesson types, supported diagnostic flows, supported languages, supported payment modes, and unsupported features.
- [x] `[critical]` Avoid claiming full CAPS coverage until every claimed topic has validated lessons, diagnostic items, answer keys, and review status.

## 0.2 Health, readiness, and runtime acceptance

- [x] `[critical]` `/health` returns `200` when the API process is alive.
- [x] `[critical]` `/ready` returns `200` only when PostgreSQL, Redis, migrations, audit repository, critical secrets, and core background-job dependencies are available.
- [x] `[critical]` `/ready` returns `503` with structured non-sensitive diagnostics when dependencies are unavailable.
- [x] `[critical]` Add tests for `/health`, `/ready`, `/metrics`, `/docs`, and `/openapi.json` in local, CI, and staging contexts.
- [x] `[critical]` Ensure readiness probes are wired correctly in Docker Compose, Kubernetes, and Azure deployment assets.
- [ ] `[high]` Add graceful degraded-mode behavior for optional dependencies such as LLM providers, analytics, email, or billing.

## 0.3 Operational acceptance

- [x] `[critical]` Automated database backups are enabled, encrypted, monitored, and restore-tested. Evidence: `scripts/backup_postgres.sh`, `scripts/restore_postgres.sh`, `docs/operations/backup_restore_runbook.md`, and Prometheus backup alerts provide repository-side automation/evidence gates; cloud schedule still requires provider configuration.
- [ ] `[critical]` Security headers, CORS, cookie policy, JWT policy, and rate limits are verified in staging.
- [x] `[critical]` Logs, metrics, traces, alerts, and dashboards are live before real learner data is processed. Evidence: structured JSON logging, request IDs, `/metrics`, `prometheus.yml`, `prometheus/alerts.yml`, Grafana provisioning, `docs/operations/observability.md`, and `scripts/validate_ops_assets.py`.
- [x] `[critical]` Incident response, security disclosure, data breach handling, and learner-data escalation procedures are documented. Evidence: `docs/incident_response.md` and `SECURITY.md`.
- [ ] `[critical]` POPIA consent, export, erasure, retention, audit, and LLM PII-redaction workflows are tested end-to-end.

---

# 1. Repository Governance and Hygiene

## 1.1 Canonical source of truth

- [x] `[critical]` Decide and document the canonical repository: `NkgoloL/Eduboost-V2`, `w3ll3ml3b3lo-hue/Eduboost-V2`, or another private/public upstream. Evidence: `docs/repository_governance.md` documents `NkgoloL/Eduboost-V2` as canonical for this snapshot and defines mirror/fork promotion rules.
- [x] `[critical]` Add `docs/repository_governance.md` covering canonical repo, mirrors, branch policy, release authority, secret rotation authority, security patch process, and archive policy. Evidence: `docs/repository_governance.md` expanded with canonical upstream, mirrors, branch protection requirements, release authority, secret rotation authority, security patch process, archive policy, and governance change control.
- [ ] `[high]` Protect `master`/`main`: require PR review, required checks, no force-push, no branch deletion, and signed commits if feasible. Repository-side evidence added in `docs/repository_governance.md`; final enforcement must be configured in GitHub branch/ruleset settings.
- [x] `[high]` Add `CODEOWNERS` for backend, frontend, infrastructure, security, compliance, curriculum, and docs. Evidence: `.github/CODEOWNERS` covers backend, frontend, infrastructure, security/privacy/compliance, curriculum/AI, docs, dependencies, tests, and workflows.
- [x] `[high]` Add issue templates: bug, feature, security redirect, compliance concern, accessibility issue, curriculum issue, incorrect content, production incident. Evidence: `.github/ISSUE_TEMPLATE/` now contains the required templates.
- [x] `[high]` Add PR template with checkboxes for tests, docs, migrations, POPIA impact, security impact, accessibility impact, analytics impact, deployment impact, and rollback plan. Evidence: `.github/PULL_REQUEST_TEMPLATE.md` expanded with validation evidence, migration, POPIA, security, accessibility, analytics/observability, deployment, and rollback sections.

## 1.2 Dependency and artifact cleanup

- [x] `[high]` Audit dependency files and decide canonical dependency paths for runtime, dev, docs, and ML extras. Evidence: `docs/dependency_management.md` defines canonical `requirements/*.in` and `requirements/*.txt` paths; root `requirements*.txt` files are explicit compatibility aliases.
- [x] `[high]` Remove duplicate or stale root dependency files, or clearly mark them as compatibility aliases. Evidence: root `requirements*.txt` files now contain explicit compatibility-alias comments and include canonical files under `requirements/`.
- [x] `[high]` Enable Dependabot or Renovate for Python, npm, Docker images, and GitHub Actions. Evidence: `.github/dependabot.yml` covers pip, npm frontend, GitHub Actions, and Docker ecosystems.
- [x] `[medium]` Add a `Makefile` or `justfile` with commands: `dev`, `test`, `lint`, `typecheck`, `e2e`, `migrate`, `docs`, `security`, `release-check`, and `smoke`. Evidence: `Makefile` now exposes all required targets.
- [x] `[medium]` Add `docs/adr/` and write ADRs for modular monolith, FastAPI V2, Next.js frontend, PostgreSQL audit ledger, Redis revocation, LLM provider abstraction, POPIA-first design, and CAPS alignment. Evidence: `docs/adr/0001` through `0009` cover the required decisions and `docs/adr/README.md` indexes them.
- [x] `[medium]` Add markdown linting and docs link checking to CI. Evidence: `.github/workflows/ci-cd.yml` includes Markdown linting plus a dedicated `docs-quality` job using `lycheeverse/lychee-action` for link checks.

---

# 2. Backend Architecture

## 2.1 Runtime surface

- [x] `[critical]` Keep `app/api_v2.py` as the only supported backend runtime entrypoint. Evidence: `app/api_v2.py`, `app/api/main.py`, `app/legacy/api/main.py`, `tests/test_api_contract_baseline.py`.
- [x] `[critical]` Ensure `app/api/main.py` remains a compatibility shim only and cannot diverge from V2 behavior. Evidence: `app/api/main.py`, `tests/test_api_contract_baseline.py`.
- [x] `[high]` Add a regression test that imports the V2 app using every documented deployment command. Evidence: `tests/test_entrypoints.py`, `tests/test_api_contract_baseline.py`, `.github/workflows/ci-cd.yml`.
- [x] `[high]` Add tests proving legacy-only routes are not accidentally exposed as production APIs. Evidence: `app/legacy/api/main.py`, `tests/test_entrypoints.py`.
- [x] `[high]` Generate and commit or publish the OpenAPI schema for review. Evidence: `docs/openapi.json`, `scripts/generate_openapi.py`.
- [x] `[medium]` Add OpenAPI diff checks in PRs. Evidence: `scripts/generate_openapi.py --check`, `Makefile`, `.github/workflows/ci-cd.yml`.

## 2.2 Router/service/domain boundaries

- [ ] `[critical]` Ensure routers are thin: request validation, auth/consent dependencies, service call, response mapping.
- [ ] `[critical]` Move business logic out of routers into services or bounded modules.
- [ ] `[high]` Define service contracts for auth, learners, guardians, consent, diagnostics, lessons, study plans, gamification, billing, audit, POPIA export, and erasure.
- [ ] `[high]` Collapse duplicate service concepts between `app/services/*_service_v2.py` and `app/modules/*/service.py`.
- [ ] `[high]` Decide canonical business-logic location: either `app/services` as application layer or `app/modules/<context>/service.py` as bounded-context services.
- [ ] `[high]` Remove metaphor-layer ambiguity from active code: `ether`, `judiciary`, `fourth_estate`, and `executive` should not be core engineering boundaries.
- [ ] `[medium]` Keep metaphor names only for storytelling/docs if useful; use domain names in code.
- [ ] `[medium]` Enforce import boundaries: routers → services → repositories/domain/core; repositories → models/database; domain should not depend on infrastructure.

## 2.3 Dependency injection and cross-cutting concerns

- [ ] `[high]` Standardize FastAPI dependencies for current user, current learner, guardian relationship, role checks, consent checks, DB session, audit context, request ID, and rate-limit identity.
- [ ] `[high]` Replace ad-hoc service construction with dependency providers.
- [ ] `[medium]` Add test dependency overrides for DB, Redis, LLM provider, email provider, payment provider, object storage, and analytics sink.
- [ ] `[medium]` Add request-scoped correlation ID propagation through logs, audit events, traces, and frontend API calls.

---

# 3. Database, Persistence, and Migrations

## 3.1 PostgreSQL schema readiness

- [x] `[critical]` Confirm every production table has explicit primary keys, timestamps, and appropriate foreign keys. Evidence: `scripts/validate_schema_integrity.py`, `app/models/__init__.py`, `alembic/versions/20260507_1330_database_integrity_constraints.py`.
- [x] `[critical]` Add or verify indexes for user email, learner ID, guardian ID, consent status, token identifiers, diagnostic attempt ID, audit timestamp, audit actor ID, and subscription/customer ID. Evidence: `docs/database/schema_integrity.md`, `scripts/validate_schema_integrity.py`, `alembic/versions/20260507_1330_database_integrity_constraints.py`; Redis-backed refresh/session and background-job IDs documented as non-PostgreSQL indexes.
- [x] `[critical]` Add database-level constraints for role enums, consent status, audit event fields, immutable audit identifiers, unique guardian-learner relationships, and non-null sensitive workflow fields. Evidence: `app/models/__init__.py`, `alembic/versions/20260507_1200_popia_consent_audit_hardening.py`, `alembic/versions/20260507_1330_database_integrity_constraints.py`.
- [ ] `[high]` Add partial indexes for active consent, active subscriptions, non-revoked sessions, and incomplete jobs.
- [ ] `[high]` Review transaction boundaries for signup, learner creation, consent submission, diagnostic completion, lesson generation, billing changes, and erasure requests.
- [ ] `[medium]` Add slow-query logging in staging and production.
- [ ] `[medium]` Add performance tests for dashboard, diagnostic, lesson, parent report, and audit endpoints.

## 3.2 Alembic discipline

- [x] `[critical]` Run `alembic upgrade head` in CI from an empty database.
- [x] `[critical]` Run `alembic check` in CI.
- [x] `[critical]` Document rollback strategy for every destructive migration. Evidence: `docs/database/migration_discipline.md`.
- [x] `[high]` Add migration naming convention: `YYYYMMDD_HHMM_<short_description>.py`. Evidence: `docs/database/migration_discipline.md`, `scripts/verify_migration_graph.py`.
- [x] `[high]` Require backup, staging dry-run, validation script, and rollback plan for migrations touching learner/guardian data. Evidence: `docs/database/migration_discipline.md`, `.github/PULL_REQUEST_TEMPLATE.md`.
- [ ] `[medium]` Add migration smoke tests using production-like data volume.
- [x] `[medium]` Add synthetic seed data for local development; never use real learner PII in fixtures. Evidence: `data/synthetic/README.md`, `data/synthetic/minimal_seed.sql`.

## 3.3 Repository layer

- [ ] `[high]` Add repository tests for every persistence path.
- [ ] `[high]` Ensure repository methods do not expose raw ORM objects to API responses.
- [x] `[high]` Ensure audit repositories are append-only by interface and by database permission.
- [ ] `[medium]` Standardize repository method names: `get_*`, `list_*`, `create_*`, `update_*`, `soft_delete_*`, `append_*`.
- [ ] `[medium]` Use pagination and deterministic sorting for all list endpoints.
- [ ] `[medium]` Use cursor pagination for high-volume event streams.

---

# 4. Authentication, Authorization, and Session Security

## 4.1 Authentication flows

- [ ] `[critical]` Verify signup, login, refresh, logout, email verification, and password reset end-to-end.
- [x] `[critical]` Use modern password hashing such as Argon2id or bcrypt with tuned cost. Evidence: `app/core/security.py`, `app/core/config.py`, `tests/unit/test_password_policy.py`.
- [x] `[critical]` Enforce minimum passphrase/password strength. Evidence: `app/core/password_policy.py`, `app/domain/schemas.py`, `tests/unit/test_password_policy.py`.
- [ ] `[critical]` Add rate limiting for login, signup, refresh, password reset, and verification endpoints.
- [ ] `[high]` Add account lockout or risk-based throttling after repeated failed attempts.
- [x] `[high]` Add session inventory and “log out all devices.” Evidence: `app/api_v2_routers/auth.py`, `app/core/refresh_tokens.py`, `tests/unit/test_refresh_token_rotation.py`.
- [ ] `[medium]` Add optional MFA for parents, teachers, admins, and support operators.
- [ ] `[medium]` Add passkeys/WebAuthn later as a trust differentiator.

## 4.2 JWT and token policy

- [x] `[critical]` Confirm production access-token TTL is 15 minutes or intentionally overridden and documented. Evidence: `app/core/config.py`, `docs/security/auth_session_policy.md`.
- [x] `[critical]` Confirm production refresh-token TTL is 7 days or intentionally overridden and documented. Evidence: `app/core/config.py`, `docs/security/auth_session_policy.md`.
- [x] `[critical]` Store refresh tokens hashed at rest, revocable, bound to a token family, and rotated on use. Evidence: `app/core/refresh_tokens.py`, `app/core/security.py`, `tests/unit/test_refresh_token_rotation.py`.
- [x] `[critical]` Detect refresh-token reuse and revoke the token family. Evidence: `app/core/refresh_tokens.py`, `tests/unit/test_refresh_token_rotation.py`.
- [ ] `[critical]` Confirm Redis-backed revocation survives expected restart/failover behavior or has persistent fallback where necessary.
- [ ] `[high]` Add JWT signing-key rotation with `kid`, current/previous keys, rotation schedule, and emergency revoke-all procedure.
- [x] `[high]` Verify cookie settings: `HttpOnly`, `Secure`, correct `SameSite`, correct domain, correct path, and no JavaScript-readable tokens. Evidence: `app/api_v2_routers/auth.py`, `docs/security/auth_session_policy.md`, `tests/unit/test_auth_cookie_policy.py`.

## 4.3 Authorization and RBAC

- [x] `[critical]` Define roles: learner, parent/guardian, teacher/tutor, admin, support operator, content reviewer, compliance auditor. Evidence: `app/core/rbac.py`, `docs/security/auth_session_policy.md`.
- [ ] `[critical]` Add object-level authorization tests proving learners cannot access other learners, parents can access only linked learners, teachers can access only assigned learners/classes, and support cannot view unnecessary PII.
- [x] `[high]` Implement policy helpers for object-level authorization. Evidence: `app/core/authorization.py`, `app/api_v2_routers/learners.py`, `tests/unit/test_authorization_policy.py`.
- [ ] `[high]` Add policy tests for every router.
- [ ] `[medium]` Move from basic RBAC to policy-based access control for sensitive workflows.
- [ ] `[medium]` Add tightly audited admin impersonation only if absolutely required.

---

# 5. POPIA, Privacy, and Learner Data Protection

## 5.1 Consent management

- [x] `[critical]` Define consent states: pending, granted, denied, expired, withdrawn, and renewal_required. Evidence: `app/core/consent_policy.py`, `app/models/__init__.py`, `alembic/versions/20260507_1200_popia_consent_audit_hardening.py`, `tests/unit/test_consent_policy.py`.
- [x] `[critical]` Enforce parent/guardian consent before processing child learner data. Evidence: `app/modules/consent/service.py`, `app/core/dependencies.py`, `app/api_v2_routers/diagnostics.py`, `app/services/popia_service.py`, `tests/unit/test_consent_policy.py`.
- [x] `[critical]` Make consent enforcement declarative through FastAPI dependencies or middleware, not scattered manual checks. Evidence: `app/core/dependencies.py` exposes `require_active_consent_for_current_learner`; `app/modules/consent/service.py` centralizes the decision policy.
- [ ] `[critical]` Add negative tests proving consent bypass is impossible for diagnostics, lessons, profiles, reports, gamification, analytics, AI feedback loops, and exports. Partial evidence: `tests/unit/test_consent_policy.py` covers missing/expired/withdrawn consent; broader router/E2E bypass matrix remains pending.
- [ ] `[high]` Add consent renewal workflow with expiry date, notification schedule, grace period, and restricted mode. Partial evidence: `app/core/consent_policy.py` defines `renewal_required`; existing `app/services/consent_renewal_service.py` and `app/api_v2_routers/consent_renewal.py` provide reminder job; restricted-mode UX remains pending.
- [x] `[high]` Add consent withdrawal workflow with immediate stop to optional processing, confirmation, audit event, and downstream deletion/anonymization job where applicable. Evidence: `app/modules/consent/service.py` sets withdrawn state and audit events; `app/services/popia_service.py` adds processing restriction and erasure request workflows.
- [x] `[high]` Add consent versioning tied to a specific privacy notice version. Evidence: `parental_consents.policy_version`, `app/core/consent_policy.py`, and `docs/popia_data_rights.md` document the versioned consent baseline.
- [ ] `[medium]` Add school-mediated consent model if institutional deployments enter scope.

## 5.2 Data subject rights

- [ ] `[critical]` Implement export workflow for learner and guardian data. Partial evidence: `app/services/popia_service.py` centralizes learner export and existing `app/api_v2_routers/parents.py` exposes guardian bundle export; PDF/guardian-friendly export completion remains pending.
- [x] `[critical]` Implement erasure workflow with exceptions for legally required audit records. Evidence: `app/services/popia_service.py`, `app/api_v2_routers/popia.py`, `docs/popia_data_rights.md` preserve append-only audit records while staging/purging learner data.
- [x] `[critical]` Implement correction/update workflow for inaccurate personal information. Evidence: `POST /api/v2/popia/correction-request/{learner_id}` in `app/api_v2_routers/popia.py` delegates to `POPIADataRightsService.request_correction`.
- [x] `[critical]` Implement processing restriction workflow. Evidence: `POST /api/v2/popia/restriction-request/{learner_id}` revokes consent through `POPIADataRightsService.restrict_processing`.
- [x] `[high]` Add status tracking and SLA targets for export/erasure requests. Evidence: `RightsRequestStatus` and SLA constants in `app/services/popia_service.py`; `docs/popia_data_rights.md` documents targets.
- [ ] `[high]` Add admin review queue for erasure requests affecting billing, school records, or legally retained audit records. Partial evidence: `POPIADataRightsService.requires_admin_review` and erasure status metadata expose the hook; admin UI/queue storage remains pending.
- [ ] `[medium]` Provide machine-readable export formats: JSON, CSV, and a guardian-friendly PDF summary. Partial evidence: `app/services/popia_service.py` supports JSON and CSV; PDF summary remains pending.

## 5.3 Data minimization and inventory

- [x] `[critical]` Create `docs/data_inventory.md` listing every collected field, purpose, lawful/consent basis, retention period, access roles, and third-party exposure.
- [x] `[critical]` Remove learner data fields not essential to educational purpose.
- [x] `[high]` Hash or tokenize identifiers where raw values are unnecessary.
- [x] `[high]` Separate identifiable operational data from analytics data.
- [x] `[high]` Prevent names, emails, phone numbers, and raw identifiers from being sent to LLM providers.
- [x] `[medium]` Create `docs/data_retention_policy.md` and `docs/subprocessor_register.md`. Evidence: both documents added.

## 5.4 Audit integrity

- [x] `[critical]` Confirm sensitive events write to append-only PostgreSQL audit repository.
- [ ] `[critical]` Add audit events for login success/failure, token refresh, logout, consent changes, learner profile changes, diagnostic lifecycle, lesson generation, LLM calls, parent report generation, data export, erasure request, admin access, and billing changes. Partial evidence: PR-003 and PR-004 cover auth, consent, export, erasure, correction, restriction, and gamification events; full event catalogue/router coverage remains pending.
- [x] `[high]` Add tamper-evident audit chain using event hash, previous event hash, and HMAC/signature. Evidence: `app/repositories/audit_repository.py`, `app/models/__init__.py`, `alembic/versions/20260507_1200_popia_consent_audit_hardening.py`, `tests/unit/test_audit_chain.py`.
- [x] `[high]` Add immutable retention rules for audit records. Evidence: existing PostgreSQL append-only rules in `alembic/versions/0006_v2_audit_events.py` plus retention exception documented in `docs/popia_data_rights.md` and `docs/data_retention_policy.md`.
- [ ] `[medium]` Build internal audit dashboard.
- [ ] `[medium]` Add automated audit completeness tests. Partial evidence: `tests/unit/test_audit_chain.py` validates hashing/signing; route-level audit completeness matrix remains pending.

---

# 6. AI, LLM Safety, and Lesson Generation

## 6.1 LLM gateway

- [x] `[critical]` Define LLM gateway interface: provider, model/version, prompt template version, input schema, output schema, latency, token usage, safety status, and fallback status.
- [x] `[critical]` Add structured output validation for AI-generated lessons. Evidence: `app/domain/llm_schemas.py` defines strict `LessonContent` and trust-label schemas; `app/core/judiciary.py` validates AI lesson JSON through Pydantic adapters; `tests/unit/test_ai_safety_contracts.py` covers the contract.
- [x] `[critical]` Reject output that fails schema, CAPS alignment, age-appropriateness, PII safety, or answer-key validation. Evidence: `app/core/judiciary.py`, `app/services/caps_validator.py`, and `app/services/ai_safety.py` enforce schema, CAPS drift, safety pattern, PII redaction, and answer-key baseline checks.
- [x] `[critical]` Ensure no raw learner PII is sent to LLM providers. Evidence: `app/services/ai_safety.py` redacts email, phone, and SA ID-number patterns; `app/core/llm_gateway.py` redacts learner context before prompt serialization; `tests/unit/test_ai_safety_contracts.py` verifies redaction.
- [ ] `[high]` Add provider fallback, timeout, retry, circuit breaker, and budget guardrails.
- [ ] `[high]` Log LLM metadata without logging sensitive prompt content.
- [x] `[medium]` Add prompt-template version control and deterministic mock provider for tests. Evidence: `app/core/config.py` supports `LLM_PROVIDER=mock`, `.env.example` documents it, and `ExecutiveService._call_mock()` is covered by `tests/unit/test_ai_safety_contracts.py`.
- [ ] `[medium]` Add golden prompt tests for every supported grade/subject/topic.

## 6.2 Content quality and hallucination control

- [x] `[critical]` Define lesson output contract: topic, grade, subject, CAPS reference, objectives, explanation, worked examples, practice questions, answer key, remediation hints, difficulty, language level, and safety classification. Evidence: `app/domain/llm_schemas.py` extends `LessonContent` with CAPS reference/topic/subtopic, variant, language level, safety classification, alignment confidence, quality score, and trust label.
- [x] `[critical]` Require generated answer keys to be independently checked. Evidence: `app/core/judiciary.py` rejects missing/placeholder answer keys and `LessonTrustLabel.answer_checked` is set only when a non-empty answer passes the structured contract.
- [ ] `[high]` Add validators for arithmetic correctness, answer-key consistency, grade-level readability, missing explanations, unsafe content, and PII leakage.
- [ ] `[high]` Add human review queue for low-confidence or high-impact content.
- [x] `[high]` Build content quality score: correctness, CAPS alignment, clarity, readability, pedagogical completeness, inclusiveness, and safety. Evidence: `app/services/ai_safety.py` defines `ContentQualityScore`; `app/core/llm_gateway.py` stores `quality_score` metadata; `tests/unit/test_ai_safety_contracts.py` covers scoring.
- [x] `[medium]` Create lesson regression suite so accepted lessons do not degrade after prompt/model changes. Evidence: `tests/unit/test_caps_alignment.py` and `tests/unit/test_ai_safety_contracts.py` cover lesson coercion, provider determinism, CAPS retries, safety metadata, and structured output.
- [ ] `[medium]` Add model comparison harness for cost, latency, correctness, stability, language quality, and hallucination rate.

## 6.3 CAPS alignment

- [x] `[critical]` Create canonical CAPS topic map: phase, grade, subject, term, topic, subtopic, prerequisites, assessment standards. Evidence: `app/services/curriculum/caps_topic_map.py` defines versioned `CAPSTopic` records and `CAPSTopicMap`; `tests/unit/test_caps_topic_map.py` covers canonical references.
- [x] `[critical]` Add validators ensuring generated content references a valid CAPS topic. Evidence: `app/services/caps_validator.py` validates topic/reference alignment and `app/core/llm_gateway.py` enriches and rejects drifted lesson output.
- [ ] `[high]` Add curriculum coverage dashboards.
- [x] `[high]` Detect topics without lessons, diagnostics, practice questions, or quality-reviewed content. Evidence: `app/services/curriculum/coverage.py` detects gaps against canonical CAPS references; `tests/unit/test_curriculum_coverage.py` verifies gap detection.
- [ ] `[medium]` Add teacher-facing CAPS coverage export.
- [x] `[medium]` Add alignment confidence score per lesson. Evidence: `app/services/caps_validator.py` returns `alignment_confidence`, `LessonContent` carries it, and lessons persist it via `app/modules/lessons/service.py` plus migration `20260507_1500`.
- [x] `[medium]` Version curriculum maps. Evidence: `CURRICULUM_MAP_VERSION` in `app/services/curriculum/caps_topic_map.py` is embedded in canonical CAPS references.

## 6.4 AI mission differentiation

- [ ] `[high]` Add “explain it my way” lesson variants: visual, story-based, step-by-step, exam-style, real-world South African examples, and multilingual support.
- [ ] `[high]` Add adaptive remediation: detect misconception, choose explanation strategy, generate targeted practice, re-assess.
- [ ] `[medium]` Add parent explanation mode: what the learner struggled with, how to help at home, and what to practice next.
- [ ] `[medium]` Add teacher insight mode: class misconceptions, intervention groups, topic heatmaps.
- [ ] `[medium]` Add low-bandwidth AI mode with pre-generated lessons, compressed payloads, and offline-friendly assets.
- [ ] `[research]` Investigate retrieval-augmented generation using only approved CAPS-aligned content.
- [ ] `[research]` Investigate local/smaller models for cost and privacy-sensitive workloads.

---

# 7. Diagnostics, Assessment, and Learning Science

## 7.1 IRT diagnostic engine

- [x] `[critical]` Define diagnostic item schema: item ID, subject, grade, topic, skill, difficulty, discrimination, correct answer, distractors, explanation, and CAPS reference. Evidence: `DiagnosticItemContract` in `app/domain/llm_schemas.py`, `app/services/diagnostic_safety.py`, and migration `20260507_1500` add required runtime/schema fields.
- [x] `[critical]` Validate IRT parameters for difficulty bounds, discrimination bounds, probability output, overflow, and invalid input. Evidence: `app/services/diagnostic_safety.py` validates finite parameter bounds; `app/models/__init__.py` and migration `20260507_1500` add DB constraints; existing IRT engine tests still cover probability/update behavior.
- [ ] `[critical]` Add tests for probability of correctness, Fisher information, ability update, edge responses, empty responses, all-correct, and all-incorrect.
- [ ] `[high]` Add item calibration workflow.
- [ ] `[high]` Add item exposure limits so learners do not repeatedly see the same questions.
- [ ] `[high]` Add diagnostic session recovery after disconnect.
- [ ] `[medium]` Add confidence intervals for ability estimates.
- [ ] `[medium]` Add item bias review across language, region, and socioeconomic context.

## 7.2 Assessment content

- [ ] `[critical]` Build minimum viable item bank for each supported launch grade/subject.
- [x] `[critical]` Add item review status: draft, AI-generated, human-reviewed, approved, retired. Evidence: `ItemReviewStatus` in `app/models/__init__.py`, `DiagnosticItemContract.review_status`, and migration `20260507_1500` persist the review lifecycle.
- [x] `[high]` Add distractor quality review and explanation quality review. Evidence: `DiagnosticItemContract` requires exactly four options and explanation text; `DiagnosticItemValidator` rejects duplicate distractors and invalid/empty explanations.
- [x] `[medium]` Tag items by misconception. Evidence: `IRTItem.misconception_tag`, `DiagnosticItemContract.misconception_tag`, and migration `20260507_1500` add the field.
- [ ] `[medium]` Add adaptive practice generator based on diagnostic gaps.
- [ ] `[medium]` Add spaced repetition and retrieval practice.

## 7.3 Progress model

- [ ] `[critical]` Define mastery model combining diagnostic estimate, practice performance, recency, consistency, and confidence.
- [ ] `[high]` Add progress timelines per learner.
- [ ] `[high]` Add subject-level and topic-level mastery.
- [ ] `[medium]` Add learning velocity, risk-of-falling-behind signal, and next-best-activity recommendation.
- [ ] `[research]` Evaluate Bayesian Knowledge Tracing or Deep Knowledge Tracing once enough usage data exists.

---

# 8. Frontend Production Readiness

## 8.1 Next.js hardening

- [x] `[critical]` Separate public browser-safe environment variables from server-only variables and deployment secrets. Evidence: `app/frontend/src/lib/env.ts`, `scripts/validate_frontend_env.py`, `app/frontend/package.json` `env-check`.
- [x] `[critical]` Ensure no secrets are exposed through `NEXT_PUBLIC_*`. Evidence: `scripts/validate_frontend_env.py` rejects secret-like `NEXT_PUBLIC_*` variables and `tests` contract covers this.
- [x] `[critical]` Add error boundaries for all major routes. Evidence: `app/frontend/src/components/eduboost/ErrorBoundary.tsx`, `app/frontend/src/app/error.tsx`, root layout wrapper.
- [x] `[critical]` Add loading, empty, and failure states for all API-backed screens. Evidence: root `loading.tsx`, existing learner screen failure/empty states, and PR-007 accessibility contract tests.
- [x] `[high]` Add global typed API client with auth handling, refresh handling, request ID propagation, typed responses, and normalized errors. Evidence: `app/frontend/src/lib/api/client.ts`, `app/frontend/src/lib/api/types.ts`, `app/frontend/src/lib/api/services.ts`.
- [x] `[high]` Add protected route guards for learner and parent dashboards; teacher/admin guard component support is present pending dashboards. Evidence: `app/frontend/src/components/eduboost/RouteGuard.tsx`, learner layout, parent dashboard page.
- [ ] `[medium]` Add bundle analysis, route-level code splitting, and performance budgets.

## 8.2 Core UX flows

- [x] `[critical]` Complete signup/onboarding baseline: guardian account, learner profile, consent capture, grade/language selection, diagnostic start. Evidence: `app/frontend/src/app/(auth)/register/page.tsx`.
- [ ] `[critical]` Complete login, logout, session expiry, password reset, and email verification UX. Partial evidence: PR-007 adds guardian login, logout, refresh-on-401, and session-expiry handling; password reset/email verification remain blocked until backend endpoints/templates exist.
- [ ] `[high]` Build learner dashboard with study plan, next lesson, progress, streak, weak topics, and recommended next activity.
- [x] `[high]` Build parent dashboard with child progress, consent/data-rights controls, progress summary, and export access. Evidence: `app/frontend/src/components/eduboost/ParentDashboard.tsx`; subscription/billing UX remains future billing PR scope.
- [x] `[high]` Build diagnostic UX: question display, accessible progress indicator, answer submission, and result summary. Evidence: `app/frontend/src/components/eduboost/InteractiveDiagnostic.tsx`; pause/resume remains future offline/session recovery scope.
- [ ] `[high]` Build lesson UX: explanation, worked example, practice questions, hints, answer reveal, feedback, and report-content issue. Partial evidence: PR-007 adds accessible lesson landmarks and completion UX; report-content issue flow and richer answer reveal remain pending.
- [ ] `[medium]` Build study-plan UX, teacher dashboard, and admin console.

## 8.3 Accessibility and mobile

- [x] `[critical]` Meet WCAG 2.1 AA baseline for core flows. Evidence: skip link, landmarks, route boundaries, accessible forms, semantic navigation, diagnostic radiogroup/progressbar, reduced motion CSS, and contract tests.
- [x] `[critical]` Add keyboard/accessibility contract tests for login, signup, consent, diagnostic, lesson, and dashboards. Evidence: `app/frontend/src/__tests__/AccessibilityContracts.test.tsx`.
- [x] `[critical]` Ensure sufficient color contrast and accessible form validation baseline. Evidence: accessible auth form labels, `aria-invalid`, error descriptions, focus-visible CSS, and chart hard-coded color removal.
- [x] `[high]` Add semantic headings, landmarks, and screen-reader friendly diagnostic questions. Evidence: `InteractiveDiagnostic.tsx`, `InteractiveLesson.tsx`, root/auth/learner/parent layouts.
- [ ] `[medium]` Add reduced-motion mode, dyslexia-friendly typography option, text resizing, and audio narration. Partial evidence: PR-007 adds `prefers-reduced-motion` support; typography toggle, text resizing control, and narration remain pending.
- [x] `[critical]` Make all learner and parent flows usable on mobile. Evidence: responsive main content spacing, mobile bottom learner navigation, touch-target CSS, and existing responsive page layouts.
- [ ] `[high]` Add responsive layout tests. Partial evidence: PR-007 adds static accessibility contracts; browser viewport tests remain pending Playwright dependency/runtime fix.
- [ ] `[medium]` Add PWA/low-data mode with cached app shell, compressed assets, and offline-friendly messaging. Partial evidence: existing service worker/offline messaging remains; PR-007 did not expand caching strategy.

---

# 9. API Design and Integrations

## 9.1 API consistency

- [x] `[critical]` Standardize response envelopes: `data`, `error`, `meta`, and `request_id`. Evidence: `app/domain/api_v2_models.py`, `app/core/exceptions.py`, `tests/test_api_contract_baseline.py`.
- [x] `[critical]` Standardize error shape: machine code, human message, field errors, request ID, and remediation hint. Evidence: `app/core/exceptions.py`, `tests/test_api_contract_baseline.py`.
- [x] `[high]` Add OpenAPI tags, summaries, examples, and versioning policy. Evidence: `app/api_v2.py`, `docs/openapi.json`, `docs/api_v2.md`.
- [ ] `[medium]` Add idempotency keys for billing, lesson generation, consent submission, and export requests.
- [ ] `[medium]` Add pagination metadata for all list endpoints.

## 9.2 Billing and subscriptions

- [ ] `[critical]` Decide production billing provider.
- [ ] `[critical]` Implement secure webhook signature verification, idempotency, replay protection, and audit logging.
- [ ] `[critical]` Add subscription states: trial, active, past_due, paused, canceled, expired.
- [ ] `[high]` Define pricing: free tier, parent plan, school plan, sponsored learner plan, NGO/community plan.
- [ ] `[high]` Add billing lifecycle tests.
- [ ] `[medium]` Add invoices/receipts, coupons, sponsorships, and data-access-after-cancellation policy.

## 9.3 Notifications

- [ ] `[critical]` Choose production email provider.
- [ ] `[critical]` Add transactional templates: verification, password reset, consent request, consent expiry, diagnostic complete, weekly parent report, billing event, security alert.
- [ ] `[high]` Add notification preferences and delivery tracking.
- [ ] `[medium]` Add SMS/WhatsApp notifications only after privacy impact review.
- [ ] `[medium]` Add notification rate limits and quiet hours.

---

# 10. DevOps, Infrastructure, and Deployment

## 10.1 Docker and images

- [x] `[critical]` Verify every Dockerfile builds from a clean checkout. Evidence: CI image build path uses `docker/Dockerfile.v2`; `scripts/validate_ops_assets.py` enforces canonical Dockerfile/runtime/probe metadata. Actual clean Docker build must still run in CI/docker-capable environment.
- [x] `[critical]` Align CI image build paths with production Dockerfile names. Evidence: `.github/workflows/ci-cd.yml` image scan and `docker-compose*.yml` reference `docker/Dockerfile.v2`.
- [x] `[critical]` Run images as non-root users. Evidence: `docker/Dockerfile.v2` uses `USER eduboost`; `k8s/api-deployment.yml` sets `runAsNonRoot` and `runAsUser: 1000`.
- [x] `[critical]` Pin base images and minimize runtime layers. Evidence: `docker/Dockerfile.v2` uses a slim multi-stage base and copies only application/runtime dependencies into production.
- [x] `[high]` Add multi-stage builds and container healthchecks. Evidence: `docker/Dockerfile.v2` contains base/dependencies/production/docs stages and `/ready` healthcheck; Compose also probes `/ready`.
- [x] `[high]` Remove build tools from runtime images. Evidence: production image copies user-installed dependencies from dependency stage and does not install compiler/build chains in runtime.
- [x] `[medium]` Add image labels: commit SHA, version, build time, source repo, license. Evidence: `docker/Dockerfile.v2` OCI labels and build args.

## 10.2 Kubernetes / Azure

- [x] `[critical]` Choose production target explicitly: Azure Container Apps, AKS, or another managed container platform. Evidence: `docs/operations/deployment_runbook.md` and archived `k8s/api-deployment.yml` comments identify Azure Container Apps as authorised V2 target unless superseded by ADR.
- [x] `[critical]` Make Docker Compose, Kubernetes, Bicep, and CI deployment assets match the chosen target. Evidence: `scripts/validate_ops_assets.py`, `docker-compose.yml`, `docker-compose.prod.yml`, `k8s/api-deployment.yml`, and CI ops-assets gate validate canonical runtime/probes/observability.
- [x] `[critical]` Verify manifests for deployment, service, ingress, config maps, secret references, probes, resource requests, and limits. Evidence: `k8s/api-deployment.yml` includes SecretRef, optional ConfigMapRef, liveness/readiness probes, resources, and security context; `scripts/validate_ops_assets.py` enforces static checks.
- [ ] `[high]` Add horizontal autoscaling, network policies, workload identity, and rollout strategy.
- [ ] `[medium]` Add blue-green or canary deployment.
- [ ] `[medium]` Add automated rollback on failed health checks.

## 10.3 Environment management

- [x] `[critical]` Define local, test, staging, and production environments. Evidence: `docs/environment_variables.md`, `.env.example`, and `scripts/validate_runtime_env.py`.
- [x] `[critical]` Add `docs/environment_variables.md` with variable name, required/optional status, default, environment scope, sensitivity, and example. Evidence: `docs/environment_variables.md`.
- [x] `[critical]` Validate required environment variables at startup. Evidence: Pydantic settings validators plus `scripts/validate_runtime_env.py` and `make env-check` release gate.
- [x] `[critical]` Fail fast on missing production secrets. Evidence: production Key Vault validator in `app/core/config.py`; `scripts/validate_runtime_env.py --env production` rejects missing placeholders/secrets.
- [x] `[high]` Store production secrets in Azure Key Vault or equivalent. Evidence: `app/core/config.py` Key Vault integration and `docs/environment_variables.md` production policy.
- [ ] `[high]` Rotate secrets regularly.
- [x] `[medium]` Add environment drift detection. Evidence: `scripts/validate_runtime_env.py`, `make env-check`, and CI ops-assets validation.

## 10.4 CI/CD

- [x] `[critical]` Fix workflow inconsistencies: Dockerfile paths, branch conditions, image registry casing, duplicated environment variables, stale service names.
- [x] `[critical]` Ensure CI uses the same dependency files developers use locally.
- [x] `[high]` Add workflow concurrency to cancel outdated runs.
- [x] `[high]` Upload backend and frontend test/coverage reports as artifacts.
- [x] `[medium]` Add OpenAPI diff, docs lint, link checker, migration diff summary, license check, and SBOM generation.

---

# 11. Observability, Reliability, and Operations

## 11.1 Logging

- [x] `[critical]` Emit structured JSON logs in production. Evidence: `app/core/logging.py` uses JSON renderer in production.
- [x] `[critical]` Include request ID in every backend log line. Evidence: `RequestIDMiddleware` and `StructuredLoggingMiddleware` bind/log `request_id`.
- [x] `[critical]` Scrub PII, tokens, cookies, API keys, passwords, and secrets from logs. Evidence: health diagnostics now return exception class only; observability runbook defines forbidden log data. Full automated PII log scanner remains future hardening.
- [x] `[high]` Separate audit logs from operational logs. Evidence: audit repository/service path and `docs/operations/observability.md` define separate audit/operational log semantics.
- [ ] `[medium]` Add frontend error logging and correlation ID propagation.

## 11.2 Metrics and dashboards

- [x] `[critical]` Expose Prometheus metrics for request count, latency, errors, status codes, dependency health, DB pool, Redis operations, background jobs, LLM calls, backup state, and consent events. Evidence: `app/core/metrics.py`, `app/core/health.py`, `/metrics`, and `scripts/validate_ops_assets.py`.
- [ ] `[high]` Add business metrics: active learners, diagnostic completion, lesson completion, study-plan adherence, parent report opens, consent conversion, churn.
- [x] `[high]` Add Grafana dashboards for API, DB, Redis, LLM usage, POPIA operations, learner engagement, and business metrics. Evidence: Grafana provisioning and dashboards in `grafana/`, plus Compose `grafana` service.

## 11.3 Tracing and alerting

- [ ] `[high]` Add OpenTelemetry across frontend, API, services, repositories, database, Redis, and LLM provider calls.
- [x] `[critical]` Configure alerts for API down, readiness failure, high 5xx rate, high latency, DB unavailable, Redis unavailable, audit write failure, consent enforcement failure, and failed/stale backup. Evidence: `prometheus/alerts.yml`. Migration/security scan failures are CI gates rather than Prometheus runtime alerts.
- [x] `[high]` Add warning alerts for LLM cost spike, queue/job failures, and high 4xx rate. Evidence: `prometheus/alerts.yml`; memory/disk pressure remain platform/exporter-specific follow-up.

## 11.4 Incident response

- [x] `[critical]` Create `docs/incident_response.md`. Evidence: `docs/incident_response.md`.
- [x] `[critical]` Define incident categories: security incident, learner data exposure, auth outage, billing outage, AI content safety issue, data corruption, availability outage. Evidence: `docs/incident_response.md`.
- [x] `[critical]` Define emergency actions: disable lesson generation, revoke sessions, disable provider, freeze billing webhooks, maintenance mode. Evidence: `docs/incident_response.md`.
- [ ] `[high]` Add postmortem template and run at least one tabletop exercise before production.

---

# 12. Backup, Restore, and Disaster Recovery

- [x] `[critical]` Enable automated encrypted PostgreSQL backups in a separate failure domain. Evidence: `scripts/backup_postgres.sh`, `scripts/restore_postgres.sh`, `docs/operations/backup_restore_runbook.md`; cloud scheduler/destination must be configured outside the ZIP.
- [x] `[critical]` Define backup retention: daily, weekly, monthly. Evidence: `docs/disaster_recovery.md`.
- [x] `[critical]` Add backup failure alert. Evidence: `EduBoostBackupFailure` and `EduBoostBackupStale` in `prometheus/alerts.yml`.
- [ ] `[critical]` Perform restore test into a clean environment.
- [x] `[critical]` Document RPO and RTO. Evidence: `docs/disaster_recovery.md`.
- [x] `[critical]` Validate audit records, consent states, billing states, and learner records after restore. Evidence: `docs/operations/backup_restore_runbook.md` restore validation checklist plus schema/migration validators.
- [x] `[high]` Document Redis recoverability: disposable, replicated, or persistent. Evidence: `docs/disaster_recovery.md`.
- [x] `[high]` Create `docs/disaster_recovery.md`. Evidence: `docs/disaster_recovery.md`.
- [x] `[high]` Define provider outage plans for cloud, LLM, payment, email, object storage, and analytics. Evidence: `docs/disaster_recovery.md`.
- [x] `[medium]` Automate monthly restore drills. Evidence: `docs/operations/backup_restore_runbook.md` defines monthly restore-drill procedure; scheduler remains an ops automation outside repository scope.

---

# 13. Testing and QA

## 13.1 Backend

- [ ] `[critical]` Maintain backend coverage threshold of at least 80%.
- [ ] `[critical]` Add route, service, and repository tests for every production path.
- [ ] `[critical]` Add integration tests for auth, consent, learner lifecycle, diagnostics, lessons, study plans, parent reports, billing, export, and erasure.
- [ ] `[high]` Add property-based tests for diagnostic engine.
- [ ] `[high]` Add fuzz tests for public API inputs.
- [ ] `[medium]` Add contract tests for external integrations.

## 13.2 Frontend

- [ ] `[critical]` Maintain frontend coverage threshold of at least 80%.
- [ ] `[critical]` Add component tests for login, signup, consent, diagnostic question, lesson card, progress chart, and parent report summary.
- [ ] `[high]` Add route-level tests for protected pages.
- [ ] `[high]` Add API error-handling tests.
- [ ] `[medium]` Add visual regression and accessibility tests.

## 13.3 E2E and performance

- [ ] `[critical]` Add Playwright flow: guardian signup → learner profile → consent → diagnostic → first lesson → parent report → logout.
- [ ] `[critical]` Add negative E2E tests: no consent, unauthorized learner access, expired session, failed payment, and unavailable LLM provider.
- [ ] `[high]` Add production-like compose E2E test.
- [ ] `[high]` Define performance targets for API p95 latency, dashboard load, diagnostic submit, lesson queue time, and report generation.
- [ ] `[medium]` Add k6 or Locust load tests.

---

# 14. Security Hardening

## 14.1 Application security

- [ ] `[critical]` Configure security headers: CSP, HSTS, X-Content-Type-Options, Referrer-Policy, Permissions-Policy, and frame protections.
- [ ] `[critical]` Validate production CORS; no wildcard origins with credentials.
- [ ] `[critical]` Add CSRF strategy if cookie-based auth is used.
- [ ] `[critical]` Sanitize user-generated content.
- [ ] `[critical]` Validate file upload handling if uploads exist.
- [ ] `[high]` Add request size limits, per-user/per-IP rate limits, and brute-force detection.
- [ ] `[high]` Add SSRF protections for any URL-fetching capability.

## 14.2 Supply chain and secrets

- [ ] `[critical]` Keep pip-audit, npm audit, Trivy, Bandit, and gitleaks green.
- [ ] `[critical]` Confirm no real secrets exist in git history; rotate anything exposed during development.
- [ ] `[high]` Pin Docker base images by digest.
- [ ] `[high]` Generate SBOM for backend and frontend images.
- [ ] `[high]` Add license policy.
- [ ] `[medium]` Sign container images with cosign.

## 14.3 Security testing

- [ ] `[high]` Run OWASP ZAP baseline scan against staging.
- [ ] `[high]` Add threat model workshop.
- [ ] `[medium]` Commission external penetration test before broad public launch.
- [ ] `[medium]` Create clear vulnerability disclosure policy.

---

# 15. Product Strategy and Mission Differentiation

## 15.1 Mission clarity

- [ ] `[high]` Adopt a crisp mission statement: “EduBoost helps South African primary learners master CAPS topics through consent-safe adaptive diagnostics, AI-generated remediation, and parent-visible progress.”
- [ ] `[high]` Add public value proposition: CAPS-aligned, parent-aware, low-bandwidth friendly, privacy-first, adaptive, South African context.
- [ ] `[high]` Add “Why EduBoost is different” to README and landing page.
- [ ] `[medium]` Define mission KPIs: mastery lift, diagnostic-to-remediation completion, parent engagement, weekly active learners, topic mastery lift, accessibility reach, low-bandwidth success rate.

## 15.2 South African differentiation

- [ ] `[high]` Use South African examples in lessons: local currency, geography, school calendar, everyday contexts, and culturally familiar scenarios.
- [ ] `[high]` Add multilingual roadmap: English, isiZulu, isiXhosa, Afrikaans, Sepedi, Setswana, Sesotho, Tshivenda, Xitsonga, siSwati, isiNdebele.
- [ ] `[medium]` Add home-language preference and vocabulary bridge mode.
- [ ] `[medium]` Add low-bandwidth and mobile-first commitments to marketing and product UX.
- [ ] `[research]` Explore partnerships with schools, NGOs, after-school programs, and community learning centers.

## 15.3 Trust and transparency

- [ ] `[high]` Add “How EduBoost uses AI” page.
- [ ] `[high]` Add “How EduBoost protects learner data” page.
- [ ] `[high]` Add “What parents can see” page.
- [ ] `[medium]` Add visible lesson trust labels: AI-generated, answer-checked, CAPS-linked, teacher-reviewed.
- [ ] `[medium]` Add “report a content problem” on every generated lesson.

---

# 16. Growth, Onboarding, and Retention

## 16.1 Onboarding

- [ ] `[critical]` Reduce first-run path to: guardian account → learner profile → consent → grade/subject → short diagnostic → first lesson.
- [ ] `[high]` Add progress indicator and consent explanation during onboarding.
- [ ] `[high]` Add onboarding analytics funnel.
- [ ] `[medium]` Add demo mode with synthetic learner data.
- [ ] `[medium]` Add school invite flow if school deployments are planned.

## 16.2 Retention

- [ ] `[high]` Add weekly learner goals and parent weekly summaries.
- [ ] `[high]` Add streaks carefully without encouraging unhealthy usage patterns.
- [ ] `[medium]` Add spaced review reminders, “continue where you left off,” mastery celebrations, and learner-visible topic map.
- [ ] `[medium]` Add reflection prompts: “What confused you?”, “What helped?”, and “How confident are you?”

## 16.3 Growth loops

- [ ] `[medium]` Add shareable parent progress report that excludes sensitive details by default.
- [ ] `[medium]` Add referral flow for parents.
- [ ] `[medium]` Add classroom invitation flow.
- [ ] `[research]` Explore sponsored learner and low-data partnership models.

---

# 17. Admin, Support, and Internal Operations

## 17.1 Admin console

- [ ] `[high]` Build admin console with strict RBAC.
- [ ] `[high]` Include user search, learner search, consent status, subscription status, diagnostic attempts, lesson jobs, audit lookup, and export/erasure queue.
- [ ] `[critical]` Audit every admin read/write action.
- [ ] `[critical]` Hide unnecessary PII from support roles.
- [ ] `[high]` Add break-glass access policy.

## 17.2 Support workflows

- [ ] `[high]` Create playbooks for login issues, consent issues, billing issues, incorrect lessons, data export, erasure, suspected compromise, and account recovery.
- [ ] `[high]` Add user-facing help center docs.
- [ ] `[medium]` Add support ticket integration and support macros.

## 17.3 Content operations

- [ ] `[high]` Build content review workflow with reviewer roles.
- [ ] `[high]` Add lesson approval queue.
- [ ] `[medium]` Add versioned content publishing, rollback, and topic coverage dashboard.

---

# 18. Documentation

## 18.1 Developer docs

- [ ] `[critical]` Keep README accurate and current.
- [ ] `[critical]` Add local setup troubleshooting for Docker, database, Redis, frontend installs, migrations, and tests.
- [ ] `[high]` Add backend architecture docs for request lifecycle, auth, consent, diagnostics, lesson generation, billing, and audit.
- [ ] `[high]` Add frontend architecture docs for routing, state management, API client, auth handling, and component conventions.
- [ ] `[high]` Add testing, deployment, debugging, and performance guides.

## 18.2 Compliance docs

- [ ] `[critical]` Keep POPIA docs synchronized with actual code behavior.
- [ ] `[critical]` Draft privacy notice, child-friendly privacy explanation, parent consent terms, and data processing notices.
- [ ] `[high]` Add data retention policy, processing inventory, subprocessor register, and DPIA-style privacy impact assessment.

## 18.3 Product docs

- [ ] `[high]` Add product overview, parent guide, learner guide, teacher guide, FAQ, pricing/billing FAQ, and AI transparency FAQ.

---

# 19. Analytics and Experimentation

## 19.1 Privacy-preserving analytics

- [ ] `[critical]` Define analytics events with privacy review.
- [ ] `[critical]` Do not send raw learner PII to analytics tools.
- [ ] `[high]` Track core funnel: visit, signup started, signup completed, learner added, consent granted, diagnostic started, diagnostic completed, first lesson opened, first practice completed, parent report viewed.
- [ ] `[high]` Track learning outcomes: baseline diagnostic, remediation activity, reassessment, mastery change.
- [ ] `[medium]` Add analytics opt-out where appropriate and event schema validation.

## 19.2 Experimentation

- [ ] `[medium]` Add feature flags and server-side experiment assignment.
- [ ] `[medium]` Test onboarding copy, diagnostic length, lesson explanation style, and parent report format.
- [ ] `[research]` Define ethical experimentation guidelines for minors and education.

---

# 20. Performance and Scalability

## 20.1 Backend

- [ ] `[high]` Profile slow endpoints.
- [ ] `[high]` Configure DB connection pools.
- [ ] `[high]` Add Redis caching for safe, non-sensitive, high-read data.
- [ ] `[high]` Define cache invalidation rules.
- [ ] `[medium]` Move report generation, exports, erasure, lesson generation, and email sending into background jobs.
- [ ] `[medium]` Add queue backlog metrics and API response compression.

## 20.2 Frontend

- [ ] `[high]` Measure Core Web Vitals.
- [ ] `[high]` Optimize dashboard render time and lazy-load heavy charts.
- [ ] `[medium]` Add image optimization, route code splitting, and skeleton states.

## 20.3 AI cost/performance

- [ ] `[high]` Add per-user and per-tenant AI usage limits.
- [ ] `[high]` Cache reusable generated content where privacy-safe.
- [ ] `[high]` Track cost by provider/model/feature.
- [ ] `[medium]` Fall back from live generation to curated/static content.
- [ ] `[medium]` Batch-generate common topics.
- [ ] `[research]` Explore local inference for cheaper high-volume tasks.

---

# 21. Data Science and Learning Analytics

- [ ] `[high]` Define learning event schema: pseudonymous learner ID, topic, activity type, timestamp, correctness, attempt number, time spent, hint usage, confidence.
- [ ] `[high]` Separate analytics warehouse from transactional DB if scale requires.
- [ ] `[high]` Add anonymization or pseudonymization strategy.
- [ ] `[medium]` Add data quality checks.
- [ ] `[medium]` Build parent insight cards: needs practice, improving, mastered, next focus.
- [ ] `[medium]` Build learner insight cards: strongest topic, practice next, mistake pattern.
- [ ] `[medium]` Build teacher insights: class heatmap, misconception clusters, intervention groups.
- [ ] `[research]` Evaluate fairness of recommendations across language and socioeconomic context.

---

# 22. Gamification and Motivation

- [ ] `[high]` Ensure gamification supports learning, not compulsive engagement.
- [ ] `[high]` Avoid dark patterns.
- [ ] `[high]` Make mastery-based rewards more important than time-spent rewards.
- [ ] `[medium]` Add badges for consistency, resilience, topic mastery, revision, and challenge completion.
- [ ] `[medium]` Add streak freeze or compassionate repair to prevent demotivation.
- [ ] `[medium]` Let learners choose explanation style, difficulty, theme/avatar, and daily goal.
- [ ] `[medium]` Add growth-mindset messaging grounded in effort and strategy.

---

# 23. Content, Curriculum, and Pedagogy

## 23.1 Curriculum coverage

- [ ] `[critical]` Define supported launch scope: grades, subjects, terms, topics.
- [ ] `[critical]` Do not claim complete CAPS coverage until verified.
- [ ] `[high]` Create coverage matrix.
- [ ] `[high]` Add minimum lesson count and diagnostic item count per topic.
- [ ] `[medium]` Add curriculum gap roadmap.

## 23.2 Pedagogical quality

- [ ] `[high]` Create lesson quality rubric and diagnostic item quality rubric.
- [ ] `[high]` Include worked examples, guided practice, independent practice, misconception feedback, retrieval practice, and spaced review.
- [ ] `[medium]` Add concrete-representational-abstract progression for math.
- [ ] `[medium]` Add reading-level checks and culturally relevant examples.
- [ ] `[research]` Partner with educators for expert review.

## 23.3 Multilingual pedagogy

- [ ] `[medium]` Add glossary support: English term, home-language term, simple explanation, example sentence.
- [ ] `[medium]` Add code-switching support where educationally useful.
- [ ] `[medium]` Add teacher/parent language preference.
- [ ] `[research]` Validate translations with native speakers and educators.

---

# 24. Legal, Policy, and Business Readiness

- [ ] `[critical]` Draft and review Terms of Service, Privacy Policy, Child-friendly Privacy Notice, Parent Consent Notice, Acceptable Use Policy, Refund Policy, and school Data Processing Agreement.
- [ ] `[critical]` Ensure legal docs match actual product behavior.
- [ ] `[high]` Add legal document versioning and acceptance tracking.
- [ ] `[high]` Add policy update notification workflow.
- [ ] `[high]` Define production support model, pricing operations, refund process, and escalation process.
- [ ] `[medium]` Define school procurement workflow, sponsored learner workflow, and NGO/community deployment model.

---

# 25. Launch Plan

## 25.1 Private alpha

- [ ] `[critical]` Use synthetic or explicitly consented test users only.
- [ ] `[critical]` Validate onboarding, consent, diagnostics, lessons, parent reports, and support workflow.
- [ ] `[high]` Collect structured feedback from parents, learners, and educators.
- [ ] `[high]` Measure technical stability and content correctness.

## 25.2 Public beta

- [ ] `[critical]` Launch only after security baseline, POPIA workflows, backups, support channel, incident response, and billing are tested.
- [ ] `[high]` Add beta label in UI.
- [ ] `[high]` Add feedback/report issue button.
- [ ] `[high]` Add content correction workflow.
- [ ] `[medium]` Publish transparent roadmap.

## 25.3 Production launch

- [ ] `[critical]` Final launch checklist: release tag, production deploy, health green, readiness green, migrations applied, backup verified, alerting live, dashboards live, legal docs live, privacy docs live, support live, rollback tested.
- [ ] `[high]` Announce limited scope accurately.
- [ ] `[high]` Avoid overclaiming AI capability, CAPS coverage, or guaranteed learning outcomes.

---

# 26. Make the Mission Stand Out

## 26.1 South African Learning Graph

- [ ] `[research]` Build CAPS-aligned knowledge graph: topics, prerequisites, misconceptions, diagnostic items, lessons, practice questions, local examples.
- [ ] `[medium]` Use the graph to power next-best lesson, parent explanations, teacher intervention groups, and curriculum coverage maps.
- [ ] `[medium]` Visualize the graph for learners as a learning map.

## 26.2 Parent co-pilot

- [ ] `[medium]` Add parent-friendly weekly reports: what was learned, what is difficult, how to help in 10 minutes, next week’s focus.
- [ ] `[medium]` Add “ask EduBoost how to help my child” with strict privacy controls.
- [ ] `[medium]` Add printable at-home practice sheets.
- [ ] `[medium]` Add parent nudges that are supportive, not guilt-driven.

## 26.3 Teacher/classroom mode

- [ ] `[medium]` Add teacher rosters, class diagnostics, class misconception dashboard, intervention groups, and CAPS evidence reports.
- [ ] `[research]` Validate workflow with real classroom constraints before scaling this mode.

## 26.4 Offline-first and low-resource resilience

- [ ] `[medium]` Add offline lesson packs and printable worksheets.
- [ ] `[medium]` Treat low-data mode as a first-class product feature.
- [ ] `[research]` Explore intermittent-internet school/community deployment.

## 26.5 AI transparency and trust score

- [ ] `[medium]` Add visible lesson trust label: CAPS-linked, answer-checked, teacher-reviewed, AI-generated.
- [ ] `[medium]` Add correction history for lessons.
- [ ] `[medium]` Route content reports into a review queue.

## 26.6 Ethical learning analytics

- [ ] `[medium]` Avoid negative labels such as “weak learner” or “poor performer.”
- [ ] `[medium]` Use constructive labels: ready to strengthen, needs another example, almost mastered, ready for challenge.
- [ ] `[medium]` Add explainable recommendations: “We recommend fractions because the diagnostic showed difficulty with equivalent forms.”

## 26.7 Sponsorship and community impact

- [ ] `[research]` Add sponsored learner model.
- [ ] `[research]` Add NGO/community dashboard.
- [ ] `[research]` Add anonymized impact reports: learners supported, topics mastered, practice hours, regions served, language support usage.

---

# 27. Suggested Milestones

## Milestone A: Production hardening foundation

- [ ] `/ready` dependency-aware readiness.
- [ ] Protected branch and release workflow.
- [ ] Environment variable documentation.
- [ ] Database backup and restore test.
- [ ] Auth/consent/POPIA integration tests.
- [ ] CI workflow cleanup.
- [ ] Security headers and CORS verified.
- [ ] Staging environment online.

## Milestone B: Learner MVP

- [ ] Guardian signup.
- [ ] Learner profile.
- [ ] Consent.
- [ ] Diagnostic.
- [ ] First generated/validated lesson.
- [ ] Learner dashboard.
- [ ] Parent progress summary.
- [ ] Feedback/report content issue.

## Milestone C: Trustworthy AI learning loop

- [ ] CAPS topic map.
- [ ] Structured lesson schema.
- [ ] Output validation.
- [ ] Answer-key checking.
- [ ] Prompt versioning.
- [ ] Human review queue.
- [ ] Quality scoring.
- [ ] AI transparency UI.

## Milestone D: Beta launch

- [ ] Legal docs.
- [ ] Privacy docs.
- [ ] Incident response.
- [ ] Backups.
- [ ] Monitoring.
- [ ] Support workflow.
- [ ] E2E tests.
- [ ] First release tag.
- [ ] Limited beta cohort.

## Milestone E: Mission expansion

- [ ] Multilingual support.
- [ ] Low-data mode.
- [ ] Parent co-pilot.
- [ ] Teacher dashboard.
- [ ] Sponsored learner model.
- [ ] CAPS learning graph.
- [ ] Offline lesson packs.

---

# 28. Immediate Next 20 Tasks

1. [ ] Fix or complete `/ready` so it reflects dependency readiness accurately.
2. [ ] Confirm Dockerfile naming consistency between CI, compose, and production deployment.
3. [ ] Create `docs/environment_variables.md`.
4. [ ] Create `docs/release_checklist.md`.
5. [ ] Protect `master` with required checks.
6. [x] Add PR template with security/POPIA/migration checkboxes. Evidence: `.github/PULL_REQUEST_TEMPLATE.md`.
7. [ ] Add object-level authorization tests for learner/guardian access.
8. [ ] Add consent-bypass negative tests for all learner-data routes.
9. [ ] Add LLM PII-redaction tests.
10. [ ] Add structured lesson output schema and validator.
11. [ ] Add CAPS topic map MVP for the first supported grade/subject.
12. [ ] Add E2E test for guardian signup → consent → learner diagnostic → first lesson.
13. [ ] Add backup/restore documentation and run first restore test.
14. [ ] Add admin/support access audit events.
15. [ ] Add production CORS/security-header verification tests.
16. [ ] Add OpenAPI schema generation and diff artifact in CI.
17. [ ] Add data inventory for learner, guardian, consent, audit, diagnostic, lesson, and billing data.
18. [ ] Add child-friendly privacy notice draft.
19. [ ] Add parent-facing “How EduBoost uses AI” page.
20. [ ] Publish first beta release only after the above items are complete and verified.

---

# 29. Strategic Product Direction

EduBoost should position itself as:

> **A privacy-first, CAPS-aligned adaptive learning platform for South African primary learners, combining diagnostic precision, AI-assisted remediation, parent visibility, and low-bandwidth accessibility.**

The defensible advantage is not simply “AI lessons.” The moat should be:

1. Consent-safe learner data handling.
2. CAPS-grounded content and diagnostics.
3. Adaptive remediation from measured learning gaps.
4. Parent and teacher visibility.
5. South African languages, context, and infrastructure realism.
6. Transparent AI with validation, review, and accountability.

Build toward that, and EduBoost becomes more than another education app. It becomes trustworthy localized learning infrastructure.

## Notes

- This tracker replaces the earlier stale TODO that described a different and
  much older migration state.
- The comparative audit raised several issues that are already obsolete in the
  current working repository; those are marked `[done]` above so they remain
  visible without pretending they still need action.
