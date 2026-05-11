# TODO.md Repository Audit

Generated from `TODO.md` against the current uploaded repository snapshot. Ignored `.git`, `.venv`, caches, frontend `node_modules`, lockfiles, temp files, and coverage artifacts.

## Status semantics

- **Done**: strong repo evidence or TODO already checked.
- **Partial**: related implementation/config/docs exist, but scope is incomplete or unverified.
- **Missing**: no meaningful evidence found.
- **Blocked**: needs GitHub/cloud/staging/ops access.
- **Human-decision**: requires product/legal/business/education decision or research.

## Summary

| Status | Count |
|---|---:|
| Done | 36 |
| Partial | 193 |
| Missing | 161 |
| Blocked | 7 |
| Human-decision | 29 |

## Priority × repo status

| Priority | Done | Partial | Missing | Blocked | Human-decision | Total |
|---|---:|---:|---:|---:|---:|---:|
| critical | 21 | 80 | 32 | 4 | 3 | 140 |
| high | 11 | 67 | 68 | 2 | 6 | 154 |
| medium | 3 | 46 | 61 | 1 | 4 | 115 |
| research | 0 | 0 | 0 | 0 | 16 | 16 |

## Highest-risk open items

| Rank | ID | Priority | Status | Owner | Task | Evidence |
|---:|---|---|---|---|---|---|
| 1 | TODO-016 | critical | Partial | security/backend | Incident response, security disclosure, data breach handling, and learner-data escalation procedures are documented. | docs/incident_response.md; SECURITY.md |
| 2 | TODO-017 | critical | Partial | compliance/backend | POPIA consent, export, erasure, retention, audit, and LLM PII-redaction workflows are tested end-to-end. | app/services/pii_sweep.py; scripts/popia_sweep.py; tests/popia |
| 3 | TODO-052 | critical | Partial | backend/data | Confirm every production table has explicit primary keys, timestamps, and appropriate foreign keys. | app/models; alembic/versions |
| 4 | TODO-080 | critical | Partial | security/backend | Confirm production access-token TTL is 15 minutes or intentionally overridden and documented. | app/core/config.py |
| 5 | TODO-081 | critical | Partial | security/backend | Confirm production refresh-token TTL is 7 days or intentionally overridden and documented. | app/core/config.py |
| 6 | TODO-115 | critical | Partial | compliance/backend | Add audit events for login success/failure, token refresh, logout, consent changes, learner profile changes, diagnostic lifecycle, lesson generation, LLM calls, parent report generation, data export, erasure request, admin access, and billing changes. | app/services/fourth_estate.py; app/services/audit_service.py; app/repositories/audit_repository.py |
| 7 | TODO-175 | critical | Partial | frontend | Complete signup/onboarding: guardian account, learner profile, consent capture, grade/subject selection, diagnostic start. | app/api_v2_routers/onboarding.py; app/frontend/src/components/eduboost/EntryScreens.tsx |
| 8 | TODO-183 | critical | Partial | frontend | Add keyboard navigation tests for login, signup, consent, diagnostic, lesson, and dashboards. | app/frontend/src/__tests__; playwright.config.ts |
| 9 | TODO-196 | critical | Partial | product/integrations | Implement secure webhook signature verification, idempotency, replay protection, and audit logging. | app/api_v2_routers/billing.py; app/api_v2_routers/lessons.py |
| 10 | TODO-202 | critical | Partial | security/backend | Add transactional templates: verification, password reset, consent request, consent expiry, diagnostic complete, weekly parent report, billing event, security alert. | app/services; docs |
| 11 | TODO-236 | critical | Partial | frontend | Expose Prometheus metrics for request count, latency, errors, status codes, dependency health, DB pool, Redis operations, background jobs, LLM calls, billing webhooks, and consent events. | prometheus.yml; prometheus/alerts.yml; app/core/metrics.py |
| 12 | TODO-243 | critical | Partial | security/backend | Define incident categories: security incident, learner data exposure, auth outage, billing outage, AI content safety issue, data corruption, availability outage. | docs/incident_response.md; SECURITY.md |
| 13 | TODO-251 | critical | Partial | compliance/backend | Validate audit records, consent states, billing states, and learner records after restore. | app/services/consent.py; app/modules/consent; app/domain/schemas.py |
| 14 | TODO-398 | critical | Partial | security/backend | Launch only after security baseline, POPIA workflows, backups, support channel, incident response, and billing are tested. | docs/incident_response.md; SECURITY.md |
| 15 | TODO-403 | critical | Partial | frontend | Final launch checklist: release tag, production deploy, health green, readiness green, migrations applied, backup verified, alerting live, dashboards live, legal docs live, privacy docs live, support live, rollback tested. | scripts/backup_postgres.sh; scripts/db_backup.sh; scripts/db_restore.sh |
| 16 | TODO-258 | critical | Missing | security/backend | Add integration tests for auth, consent, learner lifecycle, diagnostics, lessons, study plans, parent reports, billing, export, and erasure. | pytest.ini; CODE_OF_CONDUCT.md; CONTRIBUTING.md; EduBoost_Technical_Status_Report.md; playwright.config.ts; README.md; SECURITY.md; LLM_Integration_Roadmap.md |
| 17 | TODO-273 | critical | Missing | security/backend | Validate production CORS; no wildcard origins with credentials. | wsl_copilot.sh; EduBoost_Technical_Status_Report.md; SECURITY.md; LLM_Integration_Roadmap.md; CHANGELOG.md; RoadMap.md; .env.example; .github/PULL_REQUEST_TEMPLATE.md |
| 18 | TODO-040 | critical | Partial | security/backend | Ensure routers are thin: request validation, auth/consent dependencies, service call, response mapping. | app/api_v2_routers |
| 19 | TODO-053 | critical | Partial | compliance/backend | Add or verify indexes for user email, learner ID, guardian ID, consent status, token identifiers, diagnostic attempt ID, lesson generation job ID, audit timestamp, audit actor ID, and subscription/customer ID. | alembic/versions/20260505_1734_add_missing_production_indexes.py |
| 20 | TODO-054 | critical | Partial | compliance/backend | Add database-level constraints for role enums, consent status, audit event fields, immutable audit identifiers, unique guardian-learner relationships, and non-null sensitive workflow fields. | alembic/versions; app/models |
| 21 | TODO-061 | critical | Partial | backend/data | Document rollback strategy for every destructive migration. | docs/db_rollback.md |
| 22 | TODO-072 | critical | Partial | security/backend | Verify signup, login, refresh, logout, email verification, and password reset end-to-end. | app/api_v2_routers/auth.py; app/modules/auth/service.py; tests |
| 23 | TODO-073 | critical | Partial | security/backend | Use modern password hashing such as Argon2id or bcrypt with tuned cost. | app/services/auth_service.py; app/core/security.py; tests/unit/test_v2_services_full.py |
| 24 | TODO-074 | critical | Partial | security/backend | Enforce minimum passphrase/password strength. | app/modules/auth/service.py; app/services/auth_service.py |
| 25 | TODO-075 | critical | Partial | security/backend | Add rate limiting for login, signup, refresh, password reset, and verification endpoints. | app/core/rate_limit.py; app/api_v2.py; app/api_v2_routers/lessons.py |
| 26 | TODO-082 | critical | Partial | security/backend | Store refresh tokens hashed at rest, revocable, bound to a token family, and rotated on use. | app/modules/auth/service.py; app/services/auth_service.py |
| 27 | TODO-083 | critical | Partial | security/backend | Detect refresh-token reuse and revoke the token family. | app/modules/auth/service.py; app/services/auth_service.py |
| 28 | TODO-084 | critical | Partial | security/backend | Confirm Redis-backed revocation survives expected restart/failover behavior or has persistent fallback where necessary. | app/core/security.py; app/core/redis.py; .env.example |
| 29 | TODO-087 | critical | Partial | security/backend | Define roles: learner, parent/guardian, teacher/tutor, admin, support operator, content reviewer, compliance auditor. | app/core/security.py; app/core/dependencies.py; app/domain/schemas.py |
| 30 | TODO-088 | critical | Partial | security/backend | Add object-level authorization tests proving learners cannot access other learners, parents can access only linked learners, teachers can access only assigned learners/classes, and support cannot view unnecessary PII. | app/api_v2_routers/learners.py; app/core/security.py |
| 31 | TODO-093 | critical | Partial | compliance/backend | Define consent states: pending, granted, denied, expired, withdrawn, and renewal_required. | app/services/consent.py; app/modules/consent; app/domain/schemas.py |
| 32 | TODO-094 | critical | Partial | compliance/backend | Enforce parent/guardian consent before processing child learner data. | app/services/consent.py; tests/popia |
| 33 | TODO-095 | critical | Partial | compliance/backend | Make consent enforcement declarative through FastAPI dependencies or middleware, not scattered manual checks. | app/core/dependencies.py; app/core/security.py |
| 34 | TODO-096 | critical | Partial | compliance/backend | Add negative tests proving consent bypass is impossible for diagnostics, lessons, profiles, reports, gamification, analytics, AI feedback loops, and exports. | tests/popia; tests/test_popia_end_to_end.py |
| 35 | TODO-101 | critical | Partial | compliance/backend | Implement export workflow for learner and guardian data. | app/api_v2_routers/popia.py; app/services/popia_service.py |
| 36 | TODO-102 | critical | Partial | compliance/backend | Implement erasure workflow with exceptions for legally required audit records. | app/api_v2_routers/popia.py; app/services/popia_service.py; docs/popia_erasure.md |
| 37 | TODO-103 | critical | Partial | compliance/backend | Implement correction/update workflow for inaccurate personal information. | app/services/popia_service.py; app/api_v2_routers/popia.py |
| 38 | TODO-104 | critical | Partial | compliance/backend | Implement processing restriction workflow. | app/services/popia_service.py; app/api_v2_routers/popia.py |
| 39 | TODO-240 | critical | Partial | security/backend | Configure alerts for API down, readiness failure, high 5xx rate, high latency, DB unavailable, Redis unavailable, migration failure, audit write failure, consent enforcement failure, failed security scan, and failed backup. | scripts/backup_postgres.sh; scripts/db_backup.sh; scripts/db_restore.sh |
| 40 | TODO-246 | critical | Partial | ai/curriculum/backend | Enable automated encrypted PostgreSQL backups in a separate failure domain. | scripts/backup_postgres.sh; scripts/db_backup.sh; scripts/db_restore.sh |

## PR-sized backlog buckets


### PR-001 Repo governance and backlog hygiene

Open items: 8 — Partial 6, Missing 0, Blocked 1, Human-decision 1.

| ID | Priority | Status | Task | Evidence |
|---|---|---|---|---|
| TODO-026 | high | Partial | Add issue templates: bug, feature, security redirect, compliance concern, accessibility issue, curriculum issue, incorrect content, production incident. | .github/ISSUE_TEMPLATE/bug_report.yml; .github/ISSUE_TEMPLATE/feature_request.yml |
| TODO-025 | high | Partial | Add `CODEOWNERS` for backend, frontend, infrastructure, security, compliance, curriculum, and docs. | .github/CODEOWNERS |
| TODO-027 | high | Partial | Add PR template with checkboxes for tests, docs, migrations, POPIA impact, security impact, accessibility impact, analytics impact, deployment impact, and rollback plan. | .github/PULL_REQUEST_TEMPLATE.md |
| TODO-029 | high | Partial | Remove duplicate or stale root dependency files, or clearly mark them as compatibility aliases. | requirements.txt; requirements-dev.txt; requirements-docs.txt; requirements-ml.txt |
| TODO-032 | medium | Partial | Add `docs/adr/` and write ADRs for modular monolith, FastAPI V2, Next.js frontend, PostgreSQL audit ledger, Redis revocation, LLM provider abstraction, POPIA-first design, and CAPS alignment. | docs/adr |
| TODO-028 | high | Human-decision | Audit dependency files and decide canonical dependency paths for runtime, dev, docs, and ML extras. | wsl_copilot.sh; requirements.txt; pytest.ini; Makefile; requirements-docs.txt; prometheus.yml; .agent.md; CONTRIBUTING.md |
| TODO-024 | high | Blocked | Protect `master`/`main`: require PR review, required checks, no force-push, no branch deletion, and signed commits if feasible. | .github/workflows/ci-cd.yml |
| TODO-033 | medium | Partial | Add markdown linting and docs link checking to CI. | .github/workflows/ci-cd.yml |

### PR-002 Backend runtime/API contract baseline

Open items: 22 — Partial 19, Missing 2, Blocked 0, Human-decision 1.

| ID | Priority | Status | Task | Evidence |
|---|---|---|---|---|
| TODO-040 | critical | Partial | Ensure routers are thin: request validation, auth/consent dependencies, service call, response mapping. | app/api_v2_routers |
| TODO-034 | critical | Partial | Keep `app/api_v2.py` as the only supported backend runtime entrypoint. | app/api_v2.py |
| TODO-041 | critical | Partial | Move business logic out of routers into services or bounded modules. | app/api_v2_routers; app/services; app/modules |
| TODO-042 | high | Partial | Define service contracts for auth, learners, guardians, consent, diagnostics, lessons, study plans, gamification, billing, audit, POPIA export, and erasure. | app/services; app/modules |
| TODO-190 | critical | Partial | Standardize response envelopes: `data`, `error`, `meta`, and `request_id`. | app/core/exceptions.py; app/domain/api_v2_models.py |
| TODO-191 | critical | Partial | Standardize error shape: machine code, human message, field errors, request ID, and remediation hint. | app/core/exceptions.py |
| TODO-035 | critical | Missing | Ensure `app/legacy/api/main.py` remains a compatibility shim only and cannot diverge from V2 behavior. | — |
| TODO-048 | high | Partial | Standardize FastAPI dependencies for current user, current learner, guardian relationship, role checks, consent checks, DB session, audit context, request ID, and rate-limit identity. | app/core/dependencies.py; app/core/security.py |
| TODO-037 | high | Partial | Add tests proving legacy-only routes are not accidentally exposed as production APIs. | tests/legacy |
| TODO-036 | high | Partial | Add a regression test that imports the V2 app using every documented deployment command. | tests/test_entrypoints.py; .github/workflows/ci-cd.yml |
| TODO-043 | high | Partial | Collapse duplicate service concepts between `app/services/*_service_v2.py` and `app/modules/*/service.py`. | app/services; app/modules |
| TODO-045 | high | Partial | Remove metaphor-layer ambiguity from active code: `ether`, `judiciary`, `fourth_estate`, and `executive` should not be core engineering boundaries. | app/services/ether.py; app/services/judiciary.py; app/services/fourth_estate.py; app/services/executive.py |
| TODO-049 | high | Partial | Replace ad-hoc service construction with dependency providers. | app/api_v2_routers |
| TODO-192 | high | Partial | Add OpenAPI tags, summaries, examples, and versioning policy. | docs/openapi.json; app/api_v2_routers |
| TODO-193 | medium | Partial | Add idempotency keys for billing, lesson generation, consent submission, and export requests. | app/api_v2_routers/billing.py; app/api_v2_routers/lessons.py |
| TODO-047 | medium | Partial | Enforce import boundaries: routers → services → repositories/domain/core; repositories → models/database; domain should not depend on infrastructure. | .importlinter; .github/workflows/ci-cd.yml |
| TODO-051 | medium | Partial | Add request-scoped correlation ID propagation through logs, audit events, traces, and frontend API calls. | app/core/middleware.py; app/core/logging.py; app/frontend/src/lib/api/client.ts |
| TODO-039 | medium | Partial | Add OpenAPI diff checks in PRs. | .github/workflows/ci-cd.yml |

_Additional items in CSV: 4._


### PR-003 Auth/session/RBAC hardening

Open items: 26 — Partial 22, Missing 3, Blocked 1, Human-decision 0.

| ID | Priority | Status | Task | Evidence |
|---|---|---|---|---|
| TODO-080 | critical | Partial | Confirm production access-token TTL is 15 minutes or intentionally overridden and documented. | app/core/config.py |
| TODO-081 | critical | Partial | Confirm production refresh-token TTL is 7 days or intentionally overridden and documented. | app/core/config.py |
| TODO-202 | critical | Partial | Add transactional templates: verification, password reset, consent request, consent expiry, diagnostic complete, weekly parent report, billing event, security alert. | app/services; docs |
| TODO-072 | critical | Partial | Verify signup, login, refresh, logout, email verification, and password reset end-to-end. | app/api_v2_routers/auth.py; app/modules/auth/service.py; tests |
| TODO-073 | critical | Partial | Use modern password hashing such as Argon2id or bcrypt with tuned cost. | app/services/auth_service.py; app/core/security.py; tests/unit/test_v2_services_full.py |
| TODO-074 | critical | Partial | Enforce minimum passphrase/password strength. | app/modules/auth/service.py; app/services/auth_service.py |
| TODO-075 | critical | Partial | Add rate limiting for login, signup, refresh, password reset, and verification endpoints. | app/core/rate_limit.py; app/api_v2.py; app/api_v2_routers/lessons.py |
| TODO-082 | critical | Partial | Store refresh tokens hashed at rest, revocable, bound to a token family, and rotated on use. | app/modules/auth/service.py; app/services/auth_service.py |
| TODO-083 | critical | Partial | Detect refresh-token reuse and revoke the token family. | app/modules/auth/service.py; app/services/auth_service.py |
| TODO-084 | critical | Partial | Confirm Redis-backed revocation survives expected restart/failover behavior or has persistent fallback where necessary. | app/core/security.py; app/core/redis.py; .env.example |
| TODO-087 | critical | Partial | Define roles: learner, parent/guardian, teacher/tutor, admin, support operator, content reviewer, compliance auditor. | app/core/security.py; app/core/dependencies.py; app/domain/schemas.py |
| TODO-088 | critical | Partial | Add object-level authorization tests proving learners cannot access other learners, parents can access only linked learners, teachers can access only assigned learners/classes, and support cannot view unnecessary PII. | app/api_v2_routers/learners.py; app/core/security.py |
| TODO-176 | critical | Partial | Complete login, logout, session expiry, password reset, and email verification UX. | app/frontend/src/components/eduboost/EntryScreens.tsx; app/api_v2_routers/auth.py |
| TODO-014 | critical | Blocked | Security headers, CORS, cookie policy, JWT policy, and rate limits are verified in staging. | wsl_copilot.sh; CODE_OF_CONDUCT.md; Makefile; CONTRIBUTING.md; EduBoost_Technical_Status_Report.md; playwright.config.ts; README.md; SECURITY.md |
| TODO-233 | critical | Missing | Scrub PII, tokens, cookies, API keys, passwords, and secrets from logs. | wsl_copilot.sh; alembic.ini; docker-compose.prod.yml; EduBoost_Technical_Status_Report.md; README.md; SECURITY.md; CHANGELOG.md; RoadMap.md |
| TODO-076 | high | Partial | Add account lockout or risk-based throttling after repeated failed attempts. | app/modules/auth/service.py |
| TODO-077 | high | Partial | Add session inventory and “log out all devices.” | app/modules/auth/service.py |
| TODO-085 | high | Partial | Add JWT signing-key rotation with `kid`, current/previous keys, rotation schedule, and emergency revoke-all procedure. | app/core/secret_rotation.py |

_Additional items in CSV: 8._


### PR-004 POPIA consent/data-rights/audit

Open items: 51 — Partial 33, Missing 17, Blocked 0, Human-decision 1.

| ID | Priority | Status | Task | Evidence |
|---|---|---|---|---|
| TODO-017 | critical | Partial | POPIA consent, export, erasure, retention, audit, and LLM PII-redaction workflows are tested end-to-end. | app/services/pii_sweep.py; scripts/popia_sweep.py; tests/popia |
| TODO-115 | critical | Partial | Add audit events for login success/failure, token refresh, logout, consent changes, learner profile changes, diagnostic lifecycle, lesson generation, LLM calls, parent report generation, data export, erasure request, admin access, and billing changes. | app/services/fourth_estate.py; app/services/audit_service.py; app/repositories/audit_repository.py |
| TODO-175 | critical | Partial | Complete signup/onboarding: guardian account, learner profile, consent capture, grade/subject selection, diagnostic start. | app/api_v2_routers/onboarding.py; app/frontend/src/components/eduboost/EntryScreens.tsx |
| TODO-183 | critical | Partial | Add keyboard navigation tests for login, signup, consent, diagnostic, lesson, and dashboards. | app/frontend/src/__tests__; playwright.config.ts |
| TODO-236 | critical | Partial | Expose Prometheus metrics for request count, latency, errors, status codes, dependency health, DB pool, Redis operations, background jobs, LLM calls, billing webhooks, and consent events. | prometheus.yml; prometheus/alerts.yml; app/core/metrics.py |
| TODO-251 | critical | Partial | Validate audit records, consent states, billing states, and learner records after restore. | app/services/consent.py; app/modules/consent; app/domain/schemas.py |
| TODO-398 | critical | Partial | Launch only after security baseline, POPIA workflows, backups, support channel, incident response, and billing are tested. | docs/incident_response.md; SECURITY.md |
| TODO-258 | critical | Missing | Add integration tests for auth, consent, learner lifecycle, diagnostics, lessons, study plans, parent reports, billing, export, and erasure. | pytest.ini; CODE_OF_CONDUCT.md; CONTRIBUTING.md; EduBoost_Technical_Status_Report.md; playwright.config.ts; README.md; SECURITY.md; LLM_Integration_Roadmap.md |
| TODO-053 | critical | Partial | Add or verify indexes for user email, learner ID, guardian ID, consent status, token identifiers, diagnostic attempt ID, lesson generation job ID, audit timestamp, audit actor ID, and subscription/customer ID. | alembic/versions/20260505_1734_add_missing_production_indexes.py |
| TODO-054 | critical | Partial | Add database-level constraints for role enums, consent status, audit event fields, immutable audit identifiers, unique guardian-learner relationships, and non-null sensitive workflow fields. | alembic/versions; app/models |
| TODO-093 | critical | Partial | Define consent states: pending, granted, denied, expired, withdrawn, and renewal_required. | app/services/consent.py; app/modules/consent; app/domain/schemas.py |
| TODO-094 | critical | Partial | Enforce parent/guardian consent before processing child learner data. | app/services/consent.py; tests/popia |
| TODO-095 | critical | Partial | Make consent enforcement declarative through FastAPI dependencies or middleware, not scattered manual checks. | app/core/dependencies.py; app/core/security.py |
| TODO-096 | critical | Partial | Add negative tests proving consent bypass is impossible for diagnostics, lessons, profiles, reports, gamification, analytics, AI feedback loops, and exports. | tests/popia; tests/test_popia_end_to_end.py |
| TODO-101 | critical | Partial | Implement export workflow for learner and guardian data. | app/api_v2_routers/popia.py; app/services/popia_service.py |
| TODO-102 | critical | Partial | Implement erasure workflow with exceptions for legally required audit records. | app/api_v2_routers/popia.py; app/services/popia_service.py; docs/popia_erasure.md |
| TODO-103 | critical | Partial | Implement correction/update workflow for inaccurate personal information. | app/services/popia_service.py; app/api_v2_routers/popia.py |
| TODO-104 | critical | Partial | Implement processing restriction workflow. | app/services/popia_service.py; app/api_v2_routers/popia.py |

_Additional items in CSV: 33._


### PR-005 Database/migration integrity

Open items: 13 — Partial 11, Missing 0, Blocked 2, Human-decision 0.

| ID | Priority | Status | Task | Evidence |
|---|---|---|---|---|
| TODO-052 | critical | Partial | Confirm every production table has explicit primary keys, timestamps, and appropriate foreign keys. | app/models; alembic/versions |
| TODO-061 | critical | Partial | Document rollback strategy for every destructive migration. | docs/db_rollback.md |
| TODO-062 | high | Partial | Add migration naming convention: `YYYYMMDD_HHMM_<short_description>.py`. | alembic/versions/20260505_1734_add_missing_production_indexes.py |
| TODO-066 | high | Partial | Add repository tests for every persistence path. | tests/unit/test_audit_repository.py; tests/unit/test_v2_services_full.py |
| TODO-067 | high | Partial | Ensure repository methods do not expose raw ORM objects to API responses. | app/repositories; app/api_v2_routers |
| TODO-063 | high | Blocked | Require backup, staging dry-run, validation script, and rollback plan for migrations touching learner/guardian data. | scripts/smoke_test_migrations.sh; .github/workflows/ci-cd.yml |
| TODO-064 | medium | Partial | Add migration smoke tests using production-like data volume. | scripts/smoke_test_migrations.sh; .github/workflows/ci-cd.yml |
| TODO-065 | medium | Partial | Add synthetic seed data for local development; never use real learner PII in fixtures. | scripts/seed_irt_items.py; scripts/seed_item_bank.py; tests/fixtures |
| TODO-058 | medium | Partial | Add performance tests for dashboard, diagnostic, lesson, parent report, and audit endpoints. | tests |
| TODO-069 | medium | Partial | Standardize repository method names: `get_*`, `list_*`, `create_*`, `update_*`, `soft_delete_*`, `append_*`. | app/repositories |
| TODO-070 | medium | Partial | Use pagination and deterministic sorting for all list endpoints. | app/api_v2_routers; app/repositories |
| TODO-071 | medium | Partial | Use cursor pagination for high-volume event streams. | app/api_v2_routers; app/repositories |
| TODO-057 | medium | Blocked | Add slow-query logging in staging and production. | EduBoost_Technical_Status_Report.md; CHANGELOG.md; coverage_html/status.json; .github/PULL_REQUEST_TEMPLATE.md; docs/api_v2.md; app/api_v2.py; docker/inference_server.py; .import_linter_cache/3aba9e28428eba0e4969263086dae345455662fc.data.json |

### PR-006 AI/CAPS/diagnostics safety

Open items: 64 — Partial 44, Missing 14, Blocked 0, Human-decision 6.

| ID | Priority | Status | Task | Evidence |
|---|---|---|---|---|
| TODO-121 | critical | Partial | Add structured output validation for AI-generated lessons. | app/modules/lessons/llm_gateway.py; app/services/lesson_service_v2.py |
| TODO-122 | critical | Partial | Reject output that fails schema, CAPS alignment, age-appropriateness, PII safety, or answer-key validation. | app/modules/lessons/llm_gateway.py; app/services/lesson_service_v2.py |
| TODO-123 | critical | Partial | Ensure no raw learner PII is sent to LLM providers. | app/modules/lessons/llm_gateway.py; app/services/lesson_service_v2.py |
| TODO-128 | critical | Partial | Define lesson output contract: topic, grade, subject, CAPS reference, objectives, explanation, worked examples, practice questions, answer key, remediation hints, difficulty, language level, and safety classification. | app/domain/schemas.py; app/domain/api_v2_models.py |
| TODO-129 | critical | Partial | Require generated answer keys to be independently checked. | app/services/caps_validator.py; app/modules/lessons |
| TODO-135 | critical | Partial | Create canonical CAPS topic map: phase, grade, subject, term, topic, subtopic, prerequisites, assessment standards. | data; app/services/caps_validator.py; docs/launch_scope.md |
| TODO-136 | critical | Partial | Add validators ensuring generated content references a valid CAPS topic. | app/services/caps_validator.py; tests |
| TODO-149 | critical | Partial | Define diagnostic item schema: item ID, subject, grade, topic, skill, difficulty, discrimination, correct answer, distractors, explanation, and CAPS reference. | app/modules/diagnostics; alembic/versions/0007_caps_irt_item_bank.py |
| TODO-150 | critical | Partial | Validate IRT parameters for difficulty bounds, discrimination bounds, probability output, overflow, and invalid input. | app/modules/diagnostics/irt_engine.py; tests |
| TODO-151 | critical | Partial | Add tests for probability of correctness, Fisher information, ability update, edge responses, empty responses, all-correct, and all-incorrect. | app/modules/diagnostics/irt_engine.py; tests |
| TODO-157 | critical | Partial | Build minimum viable item bank for each supported launch grade/subject. | alembic/versions/0005_seed_irt_items.py; alembic/versions/0007_caps_irt_item_bank.py |
| TODO-158 | critical | Partial | Add item review status: draft, AI-generated, human-reviewed, approved, retired. | app/models; app/domain/schemas.py |
| TODO-163 | critical | Partial | Define mastery model combining diagnostic estimate, practice performance, recency, consistency, and confidence. | app/api_v2_routers/learners.py; app/services/study_plan_service_v2.py |
| TODO-374 | critical | Partial | Define supported launch scope: grades, subjects, terms, topics. | app/frontend/src; app/api_v2_routers |
| TODO-375 | critical | Partial | Do not claim complete CAPS coverage until verified. | app/frontend/src; app/api_v2_routers |
| TODO-405 | high | Missing | Avoid overclaiming AI capability, CAPS coverage, or guaranteed learning outcomes. | pytest.ini; .agent.md; CONTRIBUTING.md; EduBoost_Technical_Status_Report.md; README.md; SECURITY.md; LLM_Integration_Roadmap.md; CHANGELOG.md |
| TODO-124 | high | Partial | Add provider fallback, timeout, retry, circuit breaker, and budget guardrails. | app/modules/lessons/llm_gateway.py; app/services/lesson_service_v2.py |
| TODO-125 | high | Partial | Log LLM metadata without logging sensitive prompt content. | app/modules/lessons/llm_gateway.py; app/services/lesson_service_v2.py |

_Additional items in CSV: 46._


### PR-007 Frontend core flows and accessibility

Open items: 18 — Partial 18, Missing 0, Blocked 0, Human-decision 0.

| ID | Priority | Status | Task | Evidence |
|---|---|---|---|---|
| TODO-168 | critical | Partial | Separate public browser-safe environment variables from server-only variables and deployment secrets. | app/frontend/next.config.js; .env.example; docs/environment_variables.md |
| TODO-169 | critical | Partial | Ensure no secrets are exposed through `NEXT_PUBLIC_*`. | app/frontend; docs/environment_variables.md |
| TODO-170 | critical | Partial | Add error boundaries for all major routes. | app/frontend/src/components/ui/ErrorMessage.tsx |
| TODO-171 | critical | Partial | Add loading, empty, and failure states for all API-backed screens. | app/frontend/src/components/ui/LoadingSpinner.tsx; app/frontend/src/components/ui/ErrorMessage.tsx |
| TODO-182 | critical | Partial | Meet WCAG 2.1 AA for core flows. | app/frontend/src; playwright.config.ts |
| TODO-184 | critical | Partial | Ensure sufficient color contrast and accessible form validation. | app/frontend/src/app/globals.css; app/frontend/src/components/eduboost/styles.ts |
| TODO-187 | critical | Partial | Make all learner and parent flows usable on mobile. | app/frontend/src/app/globals.css; app/frontend/src/components/eduboost/styles.ts |
| TODO-172 | high | Partial | Add global typed API client with auth handling, refresh handling, request ID propagation, typed responses, and normalized errors. | app/frontend/src/lib/api/client.ts; app/frontend/src/lib/api/types.ts; app/frontend/src/lib/api/services.ts |
| TODO-173 | high | Partial | Add protected route guards for learner, parent, teacher, and admin dashboards. | app/frontend/src/app/(auth)/layout.tsx; app/frontend/src/app/(learner)/layout.tsx |
| TODO-177 | high | Partial | Build learner dashboard with study plan, next lesson, progress, streak, weak topics, and recommended next activity. | app/frontend/src/components/eduboost; app/frontend/src/app/page.tsx |
| TODO-179 | high | Partial | Build diagnostic UX: question display, progress indicator, answer submission, pause/resume, and result summary. | app/frontend/src/components/eduboost/InteractiveDiagnostic.tsx |
| TODO-180 | high | Partial | Build lesson UX: explanation, worked example, practice questions, hints, answer reveal, feedback, and report-content issue. | app/frontend/src/components/eduboost/InteractiveLesson.tsx |
| TODO-185 | high | Partial | Add semantic headings, landmarks, and screen-reader friendly diagnostic questions. | app/frontend/src |
| TODO-188 | high | Partial | Add responsive layout tests. | app/frontend/src/app/globals.css; app/frontend/src/components/eduboost/styles.ts |
| TODO-174 | medium | Partial | Add bundle analysis, route-level code splitting, and performance budgets. | app/frontend/next.config.js |
| TODO-181 | medium | Partial | Build study-plan UX, teacher dashboard, and admin console. | app/frontend/src |
| TODO-186 | medium | Partial | Add reduced-motion mode, dyslexia-friendly typography option, text resizing, and audio narration. | app/frontend/src/app/globals.css |
| TODO-189 | medium | Partial | Add PWA/low-data mode with cached app shell, compressed assets, and offline-friendly messaging. | app/frontend/src/app/globals.css; app/frontend/src/components/eduboost/styles.ts |

### PR-008 DevOps/observability/DR

Open items: 68 — Partial 26, Missing 40, Blocked 1, Human-decision 1.

| ID | Priority | Status | Task | Evidence |
|---|---|---|---|---|
| TODO-243 | critical | Partial | Define incident categories: security incident, learner data exposure, auth outage, billing outage, AI content safety issue, data corruption, availability outage. | docs/incident_response.md; SECURITY.md |
| TODO-273 | critical | Missing | Validate production CORS; no wildcard origins with credentials. | wsl_copilot.sh; EduBoost_Technical_Status_Report.md; SECURITY.md; LLM_Integration_Roadmap.md; CHANGELOG.md; RoadMap.md; .env.example; .github/PULL_REQUEST_TEMPLATE.md |
| TODO-246 | critical | Partial | Enable automated encrypted PostgreSQL backups in a separate failure domain. | scripts/backup_postgres.sh; scripts/db_backup.sh; scripts/db_restore.sh |
| TODO-247 | critical | Partial | Define backup retention: daily, weekly, monthly. | scripts/backup_postgres.sh; scripts/db_backup.sh; scripts/db_restore.sh |
| TODO-248 | critical | Partial | Add backup failure alert. | scripts/backup_postgres.sh; scripts/db_backup.sh; scripts/db_restore.sh |
| TODO-249 | critical | Partial | Perform restore test into a clean environment. | scripts/backup_postgres.sh; scripts/db_backup.sh; scripts/db_restore.sh |
| TODO-250 | critical | Partial | Document RPO and RTO. | scripts/backup_postgres.sh; scripts/db_backup.sh; scripts/db_restore.sh |
| TODO-272 | critical | Missing | Configure security headers: CSP, HSTS, X-Content-Type-Options, Referrer-Policy, Permissions-Policy, and frame protections. | CONTRIBUTING.md; EduBoost_Technical_Status_Report.md; playwright.config.ts; README.md; SECURITY.md; LLM_Integration_Roadmap.md; CHANGELOG.md; RoadMap.md |
| TODO-274 | critical | Missing | Add CSRF strategy if cookie-based auth is used. | .agent.md; CONTRIBUTING.md; EduBoost_Technical_Status_Report.md; playwright.config.ts; README.md; SECURITY.md; LLM_Integration_Roadmap.md; CHANGELOG.md |
| TODO-275 | critical | Missing | Sanitize user-generated content. | EduBoost_Technical_Status_Report.md; LLM_Integration_Roadmap.md; RoadMap.md; coverage_html/coverage_html_cb_dd2e7eb5.js; coverage_html/style_cb_9ff733b0.css; .github/PULL_REQUEST_TEMPLATE.md; temp_1/subprocessor_register.md; bicep/container_apps.parameters.json |
| TODO-276 | critical | Missing | Validate file upload handling if uploads exist. | wsl_copilot.sh; pytest.ini; docker-compose.prod.yml; CODE_OF_CONDUCT.md; Makefile; docker-compose.yml; prometheus.yml; .agent.md |
| TODO-279 | critical | Missing | Keep pip-audit, npm audit, Trivy, Bandit, and gitleaks green. | wsl_copilot.sh; CONTRIBUTING.md; EduBoost_Technical_Status_Report.md; README.md; SECURITY.md; CHANGELOG.md; RoadMap.md; .env.example |
| TODO-280 | critical | Missing | Confirm no real secrets exist in git history; rotate anything exposed during development. | wsl_copilot.sh; pytest.ini; CODE_OF_CONDUCT.md; Makefile; docker-compose.yml; CONTRIBUTING.md; EduBoost_Technical_Status_Report.md; playwright.config.ts |
| TODO-207 | critical | Partial | Align CI image build paths with production Dockerfile names. | .github/workflows/ci-cd.yml; docker/Dockerfile.v2 |
| TODO-231 | critical | Partial | Emit structured JSON logs in production. | app/domain/schemas.py; app/domain/api_v2_models.py |
| TODO-244 | critical | Partial | Define emergency actions: disable lesson generation, revoke sessions, disable provider, freeze billing webhooks, maintenance mode. | docs/incident_response.md; SECURITY.md |
| TODO-257 | critical | Partial | Add route, service, and repository tests for every production path. | tests/unit/test_audit_repository.py; tests/unit/test_v2_services_full.py |
| TODO-219 | critical | Missing | Define local, test, staging, and production environments. | RoadMap.md; bicep/container_apps.bicep; docs/AI_AGENT_SKILLS_MANIFEST.md; docs/v2_migration.md; .github/ISSUE_TEMPLATE/production_incident.yml; temp_1/backlog_extracted/docs/backlog/backlog_audit.md; temp_1/pr_001_extracted/.github/ISSUE_TEMPLATE/production_incident.yml; docs/backlog/backlog_audit.md |

_Additional items in CSV: 50._


### PR-009 Product/ops/future differentiation

Open items: 120 — Partial 14, Missing 85, Blocked 2, Human-decision 19.

| ID | Priority | Status | Task | Evidence |
|---|---|---|---|---|
| TODO-016 | critical | Partial | Incident response, security disclosure, data breach handling, and learner-data escalation procedures are documented. | docs/incident_response.md; SECURITY.md |
| TODO-196 | critical | Partial | Implement secure webhook signature verification, idempotency, replay protection, and audit logging. | app/api_v2_routers/billing.py; app/api_v2_routers/lessons.py |
| TODO-403 | critical | Partial | Final launch checklist: release tag, production deploy, health green, readiness green, migrations applied, backup verified, alerting live, dashboards live, legal docs live, privacy docs live, support live, rollback tested. | scripts/backup_postgres.sh; scripts/db_backup.sh; scripts/db_restore.sh |
| TODO-318 | critical | Missing | Audit every admin read/write action. | wsl_copilot.sh; docker-compose.prod.yml; CODE_OF_CONDUCT.md; docker-compose.yml; .agent.md; CONTRIBUTING.md; EduBoost_Technical_Status_Report.md; README.md |
| TODO-328 | critical | Missing | Add local setup troubleshooting for Docker, database, Redis, frontend installs, migrations, and tests. | pytest.ini; docker-compose.prod.yml; Makefile; docker-compose.yml; prometheus.yml; CONTRIBUTING.md; EduBoost_Technical_Status_Report.md; playwright.config.ts |
| TODO-197 | critical | Partial | Add subscription states: trial, active, past_due, paused, canceled, expired. | app/services/subscription_service.py; app/domain/schemas.py |
| TODO-013 | critical | Blocked | Automated database backups are enabled, encrypted, monitored, and restore-tested. | docker-compose.prod.yml; Makefile; docker-compose.yml; .agent.md; EduBoost_Technical_Status_Report.md; CHANGELOG.md; RoadMap.md; .env.example |
| TODO-015 | critical | Blocked | Logs, metrics, traces, alerts, and dashboards are live before real learner data is processed. | requirements.txt; pytest.ini; docker-compose.prod.yml; CODE_OF_CONDUCT.md; requirements-docs.txt; docker-compose.yml; prometheus.yml; CONTRIBUTING.md |
| TODO-319 | critical | Missing | Hide unnecessary PII from support roles. | pytest.ini; CONTRIBUTING.md; SECURITY.md; CHANGELOG.md; coverage_html/coverage_html_cb_dd2e7eb5.js; .github/PULL_REQUEST_TEMPLATE.md; temp_1/pr_004_implementation_summary.md; temp_1/popia_data_rights.md |
| TODO-327 | critical | Missing | Keep README accurate and current. | wsl_copilot.sh; CONTRIBUTING.md; EduBoost_Technical_Status_Report.md; README.md; SECURITY.md; CHANGELOG.md; RoadMap.md; .env.example |
| TODO-336 | critical | Missing | Define analytics events with privacy review. | EduBoost_Technical_Status_Report.md; README.md; LLM_Integration_Roadmap.md; .env.example; coverage_html/status.json; coverage_html/coverage_html_cb_dd2e7eb5.js; coverage_html/style_cb_9ff733b0.css; .github/PULL_REQUEST_TEMPLATE.md |
| TODO-337 | critical | Missing | Do not send raw learner PII to analytics tools. | CODE_OF_CONDUCT.md; CONTRIBUTING.md; EduBoost_Technical_Status_Report.md; playwright.config.ts; SECURITY.md; LLM_Integration_Roadmap.md; CHANGELOG.md; RoadMap.md |
| TODO-389 | critical | Missing | Ensure legal docs match actual product behavior. | docker-compose.prod.yml; docker-compose.yml; .agent.md; CONTRIBUTING.md; EduBoost_Technical_Status_Report.md; playwright.config.ts; README.md; SECURITY.md |
| TODO-330 | high | Partial | Add frontend architecture docs for routing, state management, API client, auth handling, and component conventions. | docs/architecture.md; docs/architecture |
| TODO-299 | high | Missing | Add “How EduBoost protects learner data” page. | alembic.ini; CODE_OF_CONDUCT.md; Makefile; docker-compose.yml; prometheus.yml; .agent.md; CONTRIBUTING.md; EduBoost_Technical_Status_Report.md |
| TODO-199 | high | Partial | Add billing lifecycle tests. | tests |
| TODO-012 | high | Missing | Add graceful degraded-mode behavior for optional dependencies such as LLM providers, analytics, email, or billing. | docker-compose.prod.yml; CONTRIBUTING.md; EduBoost_Technical_Status_Report.md; README.md; CHANGELOG.md; RoadMap.md; .env.example; requirements/base.txt |
| TODO-404 | high | Missing | Announce limited scope accurately. | CODE_OF_CONDUCT.md; .agent.md; EduBoost_Technical_Status_Report.md; LLM_Integration_Roadmap.md; RoadMap.md; .github/PULL_REQUEST_TEMPLATE.md; temp_1/pr_004_implementation_summary.md; docs/popia_erasure.md |

_Additional items in CSV: 102._
