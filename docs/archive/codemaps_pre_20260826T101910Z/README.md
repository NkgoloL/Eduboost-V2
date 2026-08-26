# Codemaps Documentation

This directory contains codemaps that document the architecture and implementation of EduBoost V2 systems. Codemaps provide detailed traces through codebases, showing execution flows, component relationships, and technical details.

## Codemap Structure

Each codemap file follows a standardized structure to ensure consistency and readability:

### File Format
- **File Extension:** `.md` (Markdown)
- **Naming Convention:** `snake_case_with_underscores.md` (e.g., `jwt_security_implementation_dual_system_architecture.md`)

### Document Structure

#### 1. Title and Overview
```markdown
# [System Name]

[Brief description of the system, key components, and notable entry points]
```

#### 2. Trace Sections
Each codemap contains one or more traces. Each trace represents a specific execution flow or aspect of the system.

##### Trace Header
```markdown
## Trace ID: [number]
**Title:** [Descriptive title]

**Description:** [Concise description of what this trace covers]
```

##### Motivation Section
```markdown
**Motivation:**
[Paragraph explaining the purpose and rationale for this system/component]
```

##### Details Section
```markdown
**Details:**
[Trace-specific narrative subsections derived from what the trace actually does]
```

The Details section should be adaptive, not a static checklist. Choose subsection names after reading the trace source and understanding the behavior being documented. Examples include `Registration Flow`, `Consent State Management`, `Fisher Information`, `Quality Gates`, `Spaced Repetition Scheduling`, `Worker Registration`, or `Router Imports`. Include concurrency, timing, migration, error handling, and security details only when they are relevant to that trace.

##### Trace Text Diagram
```markdown
**Trace text diagram:**
```
[ASCII diagram showing the flow]
```
```

##### Location IDs
```markdown
**Location ID: [letter][number]**
- **Title:** [Descriptive title]
- **Description:** [What this location represents]
- **Path:LineNumber:** [/absolute/path/to/file:line_number]
```

##### AI Guide Section
```markdown
### AI Guide: [Trace Title]

**Motivation:**
[Why this trace matters in the product, architecture, compliance model, or developer workflow]

**Details:**
[Adaptive narrative subsections tailored to the trace]
```

AI Guides should not repeat a generic `Overview / Key Components / Best Practices / Common Issues` template across traces. They should explain the trace in prose, cite Location IDs such as `[1a]` or `[4f]`, and use subsections that match the actual source-backed flow.

### Required Sections

Every trace MUST include:
1. **Title** - Descriptive name
2. **Description** - What the trace covers
3. **Motivation** - Why this system/component exists
4. **Details** - Adaptive technical narrative with trace-specific subsections
5. **Trace text diagram** - ASCII diagram of the flow
6. **Location IDs** - Code references with paths and line numbers
7. **AI Guide** - Comprehensive guide with Motivation and adaptive narrative Details

### Optional Sections

The following may be added as needed:
- **Trace-specific operational notes** (for example, job scheduling, retries, fallbacks)
- **Trace-specific security properties** (for example, PII encryption, token handling, consent gates)
- **Trace-specific edge cases** (for example, provider failure, stale sessions, duplicate registration)
- **Trace-specific code examples** when they clarify implementation behavior

## Existing Codemaps

### 1. Pytest Configuration and Test Suite Structure
- **File:** `pytest_configuration_and_test_suite_structure.md`
- **Description:** Maps pytest configuration from pytest.ini through test discovery, fixture hierarchy, coverage reporting, and CI execution
- **Traces:** 7 traces covering pytest initialization, test categorization, database fixtures, coverage measurement, CI workflows, Playwright E2E configuration, and module-specific fixtures
- **Key Components:** pytest.ini, conftest.py files, pytest-cov, GitHub Actions workflows, Playwright configuration

### 2. JWT Security Implementation: Dual-System Architecture
- **File:** `jwt_security_implementation_dual_system_architecture.md`
- **Description:** Documents JWT security implementation with dual-system architecture (primary system with JWT-based refresh tokens, alternative system with opaque refresh tokens)
- **Traces:** 8 traces covering login flow, access token creation, token verification, refresh token rotation, key rotation, token revocation, opaque refresh tokens, and password security
- **Key Components:** security.py, jwt_keyring.py, token_revocation.py, refresh_tokens.py, token_config.py, password.py, auth_service.py

### 3. Content Factory Full Generation System: Overnight Batch Pipeline
- **File:** `content_factory_full_generation_system_overnight_batch_pipeline.md`
- **Description:** End-to-end overnight batch generation pipeline that orchestrates content creation from planning through review submission
- **Traces:** 8 traces covering overnight run orchestration, content gap planning, task execution, diagnostic item generation, artifact creation and validation, staging readiness verification, staging seed execution, and report generation
- **Key Components:** run_full_generation.py, content_generation_planner.py, content_generation_executor.py, deterministic.py, content_factory.py, content_staging_readiness.py, content_staging_seed_executor.py, content_generation_reporter.py

### 4. Alembic Migration and DDL Management: Startup DDL Repairs, Migration Integrity, and Alembic Workflow
- **File:** `alembic_migration_and_ddl_management_startup_ddl_repairs_migration_integrity_and_alembic_workflow.md`
- **Description:** Database schema management through Alembic migrations and transitional startup DDL repairs with single-head linear migration graph, CI enforcement, and runtime health checks
- **Traces:** 8 traces covering startup DDL repair execution, Alembic migration execution, migration integrity CI validation, runtime migration health check, migration graph static validation, schema integrity ORM validation, migration smoke test workflow, and ADR-002 startup DDL deprecation plan
- **Key Components:** api_v2.py, alembic/env.py, migration_check.yml, health.py, verify_migration_graph.py, validate_schema_integrity.py, smoke_test_migrations.sh, ADR-002

### 5. JWT Security Implementation and Token Management
- **File:** `jwt_security_implementation_and_token_management.md`
- **Description:** JWT authentication system with dual-token architecture: short-lived access tokens (15 min) and single-use refresh tokens with family-based rotation, kid-based key rotation, Redis-backed token storage, multi-layer revocation, and canonical claims building
- **Traces:** 8 traces covering login flow, access token creation with keyring, token verification with revocation, refresh token rotation, building canonical access token claims, refresh token storage, JWT keyring validation, and token revocation
- **Key Components:** auth.py, auth_lifecycle_impl.py, security.py, jwt_keyring.py, refresh_tokens.py, token_revocation.py, auth_token_claims.py

### 6. Coverage Debt Management and Recovery System
- **File:** `coverage_debt_management_and_recovery_system.md`
- **Description:** Coverage debt management system from configuration through measurement, tracking, risk classification, and recovery planning with async-aware coverage, CI threshold enforcement, baseline measurement, module risk classification, quick-win test opportunities, and recovery sprint plan
- **Traces:** 7 traces covering coverage configuration and timeout resolution, CI coverage threshold enforcement, coverage baseline measurement and module breakdown, module risk classification and priority assignment, quick-win test opportunities and coverage impact, recovery sprint plan execution roadmap, and coverage exemptions and quality thresholds
- **Key Components:** .coveragerc, pytest.ini, ci-cd.yml, coverage_baseline_20260527.md, coverage_debt.md, coverage_quality_threshold_contract.md

### 7. EduBoost V2 Service Layer Architecture
- **File:** `eduboost_v2_service_layer_architecture.md`
- **Description:** Service layer implementing business logic across authentication, content generation, diagnostic assessments, POPIA compliance, and LLM orchestration with password verification, lockout checks, token issuance, artifact validation, IRT-based adaptive assessment, data subject rights, provider fallback, and quota control
- **Traces:** 8 traces covering user authentication flow, content artifact creation & validation, diagnostic session lifecycle, POPIA data export request, LLM gateway with fallback, content generation execution, consent lifecycle management, and lesson generation with quota control
- **Key Components:** auth_service.py, content_factory.py, diagnostic_session_service.py, popia_service.py, gateway.py, content_generation_executor.py, consent_service.py, lesson_service_v2.py

### 8. Base Repository Implementation: Generic Async CRUD & Database Interactions
- **File:** `base_repository_implementation_generic_async_crud_database_interactions.md`
- **Description:** Async repository pattern from database engine initialization through generic BaseRepository CRUD operations to concrete domain repositories and FastAPI integration with SQLAlchemy 2.0, asyncpg driver, connection pooling, session factory, declarative base, dependency injection, transaction management, and exception handling
- **Traces:** 8 traces covering database engine & session factory initialization, generic BaseRepository CRUD operations, concrete repository implementation pattern, FastAPI session lifecycle & transaction management, repository usage in API endpoint, ORM model to repository connection, advanced repository pattern (ItemBankRepository), and exception handling & error responses
- **Key Components:** database.py, base.py, repositories.py, auth_repository.py, item_bank_repository.py, exceptions.py, learners.py

### 9. API Documentation Structure: Sphinx & MkDocs Generation Pipeline
- **File:** `api_documentation_structure_sphinx_mkdocs_generation_pipeline.md`
- **Description:** Two parallel documentation systems: Sphinx generates comprehensive HTML API reference from Python docstrings with autodoc, napoleon, and viewcode extensions, while MkDocs builds a Material-themed operational docs site with mkdocstrings plugin for inline API references
- **Traces:** 6 traces covering Sphinx API documentation build flow, MkDocs site generation with mkdocstrings, Python docstring to HTML rendering, documentation inventory generation, CI documentation build pipeline, and navigation structure assembly in Sphinx
- **Key Components:** conf.py, index.rst, mkdocs.yml, docs_inventory.py, ci-cd.yml, Makefile, irt_engine.py

### 10. Test Coverage and CI Pipeline Configuration
- **File:** `test_coverage_and_ci_pipeline_configuration.md`
- **Description:** Pytest configuration, coverage reporting, and CI execution across the EduBoost-V2 testing infrastructure with async test auto-detection, marker-based categorization, coverage threshold enforcement, service containers for integration tests, and contract smoke test validation
- **Traces:** 7 traces covering pytest configuration and test discovery, coverage collection and threshold enforcement, CI core unit test execution, integration test database fixture setup, contract smoke test validation, CI coverage threshold enforcement, and runtime entrypoint contract validation
- **Key Components:** pytest.ini, conftest.py, ci-core.yml, ci-cd.yml, runtime-contract.yml, test_api_v2_routers_contract_smoke.py, test_entrypoints.py

### 11. Base Repository and CRUD Operations: Generic Async CRUD for Domain Aggregates
- **File:** `base_repository_and_crud_operations_generic_async_crud_for_domain_aggregates.md`
- **Description:** Repository pattern implementation from the generic BaseRepository class through concrete implementations to API/service usage with Python generics, SQLAlchemy 2.0 async operations, dependency injection, transaction management, and alternative patterns for legacy code
- **Traces:** 6 traces covering BaseRepository generic CRUD operations, concrete repository extensions, async database session lifecycle, repository usage in API routes, repository usage in service layer, and alternative repository patterns
- **Key Components:** base.py, learner_repository.py, diagnostic_repository.py, database.py, learners.py, diagnostic_service_v2.py, gamification_service_v2.py, repositories.py

### 12. EduBoost V2 Core Infrastructure: Runtime Primitives & Cross-Cutting Concerns
- **File:** `eduboost_v2_core_infrastructure_runtime_primitives_and_cross_cutting_concerns.md`
- **Description:** Foundational layer covering application bootstrap, authentication/authorization, LLM orchestration, health monitoring, POPIA consent enforcement, and error handling with JWT tokens, RBAC policies, semantic caching, health checks, and middleware chains
- **Traces:** 10 traces covering application bootstrap & initialization, JWT token creation & storage, JWT validation & revocation check, authorization policy enforcement, LLM lesson generation pipeline, deep health check execution, POPIA consent gate enforcement, exception to standardized API response, request lifecycle middleware chain, and AI quota enforcement
- **Key Components:** config.py, logging.py, database.py, exceptions.py, middleware.py, security.py, refresh_tokens.py, token_revocation.py, authorization.py, dependencies.py, llm_gateway.py, judiciary.py, health.py, consent_policy.py, rate_limiter.py

### 13. EduBoost V2 Domain Layer: Pydantic Models and Data Flow
- **File:** `eduboost_v2_domain_layer_pydantic_models_and_data_flow.md`
- **Description:** Domain models in app/domain/ flowing through the architecture from API transport schemas to business entities to persistence with API envelopes, consent state machines, content factory validation, diagnostic item queries, RBAC policies, coverage reports, data subject rights, and error envelopes
- **Traces:** 8 traces covering API envelope response construction, POPIA consent state transition, content factory artifact validation, diagnostic item repository query with domain schema, role-based authorization policy check, content coverage report generation, data subject rights request processing, and API error envelope construction
- **Key Components:** api_v2_models.py, schemas.py, consent.py, content_factory_schemas.py, item_schema.py, roles.py, content_coverage.py, data_subject_rights.py

### 14. EduBoost Frontend: Next.js Learner Platform with Auth, AI Lessons, Diagnostics & POPIA Compliance
- **File:** `eduboost_frontend_next_js_learner_platform_with_auth_ai_lessons_diagnostics_and_popia_compliance.md`
- **Description:** Next.js 15 TypeScript frontend featuring authentication flows, AI-generated lesson delivery, adaptive diagnostics with IRT scoring, gamification, parent dashboards with POPIA data rights, offline sync capabilities, and admin content factory tooling
- **Traces:** 8 traces covering guardian login flow, AI lesson generation with job polling, diagnostic assessment with IRT scoring, API error handling with token refresh, offline lesson completion sync, POPIA data export and erasure, app initialization with context providers, and study plan generation
- **Key Components:** page.tsx, services.ts, client.ts, offlineSync.ts, LearnerContext.tsx, RouteGuard.tsx, ParentDashboard.tsx, InteractiveDiagnostic.tsx

### 15. EduBoost V2 Modular Architecture: Core Domain Modules
- **File:** `eduboost_v2_modular_architecture_core_domain_modules.md`
- **Description:** Modular monolith's domain modules including authentication, POPIA consent management, IRT-based diagnostics, AI lesson generation, learner profiling, adaptive practice, and background jobs with ARQ async worker
- **Traces:** 9 traces covering guardian registration flow with PII encryption, consent grant lifecycle with audit trail, IRT diagnostic engine with Fisher information, AI lesson generation pipeline with validation, learner archetype profiling with Kabbalistic model, adaptive practice selection with spaced repetition, mastery model computation with risk signals, background job execution with cron schedules, and module integration with API router registration
- **Key Components:** service.py (auth), service.py (consent), irt_engine.py, item_bank_service.py, lesson_generator.py, ether_service.py, practice_generator.py, spaced_repetition_scheduler.py, mastery_model.py, learning_velocity_service.py, jobs.py

### 16. EduBoost V2 Repository Layer: Data Access Abstraction & Domain Persistence
- **File:** `eduboost_v2_repository_layer_data_access_abstraction_and_domain_persistence.md`
- **Description:** Repository pattern implementation across domain-specific persistence classes that encapsulate PostgreSQL access using async SQLAlchemy, append-only audit chains, POPIA consent tracking, diagnostic session state, item exposure control, dependency injection, and service-layer repository composition
- **Traces:** 8 traces covering BaseRepository generic CRUD operations, learner creation from API to database, audit repository hash-chain verification, consent repository POPIA enforcement, diagnostic session lifecycle persistence, item bank exposure tracking, repository dependency injection, and service-layer repository composition
- **Key Components:** base.py, repositories.py, auth_repository.py, audit_repository.py, consent_repository.py, diagnostic_session_repository.py, item_bank_repository.py, diagnostic_repositories.py, dependencies.py, popia_service.py, diagnostic_service_v2.py

### 17. EduBoost V2 Object-Level Authorization System (app/security/*)
- **File:** `eduboost_v2_object_level_authorization_system_app_security.md`
- **Description:** Centralized object-level authorization policy engine with role-based access control for learner-scoped resources using Actor-based model with ownership scopes (self, guardian, educator, support, admin, system) and canonical permissions (read, write, delete, admin), FastAPI dependency adapters bridging HTTP headers and JWT claims to the policy engine, and route integration alongside POPIA consent enforcement for two-layer security
- **Traces:** 8 traces covering core authorization policy evaluation, header-based actor construction for FastAPI, JWT claims to authorization actor adapter, route authorization enforcement for learner profile read, combined authorization and consent gate, authorization denial and HTTP 403 response, multi-role access pattern for guardian write access, and support role read-only access pattern
- **Key Components:** object_authorization.py, dependencies.py, learners.py, diagnostics.py, study_plans.py, consent_policy.py, service.py

### 18. EduBoost Frontend: Next.js Learning Platform with Auth, AI Lessons, Diagnostics & PWA
- **File:** `eduboost_frontend_next_js_learning_platform_with_auth_ai_lessons_diagnostics_and_pwa.md`
- **Description:** Next.js 15 TypeScript frontend providing guardian authentication, AI-powered adaptive lessons, IRT diagnostics, gamification, POPIA-compliant parent dashboards, and offline PWA capabilities
- **Traces:** 7 traces covering guardian login with JWT token and learner context initialization, client API call through proxy route to backend with envelope unwrapping, dashboard page load with server loader and client hydration, async lesson generation with job polling and result caching, diagnostic assessment with IRT scoring and gap analysis, service worker lifecycle with cache strategies for offline PWA, and Next.js middleware authentication guard for route protection
- **Key Components:** page.tsx, services.ts, client.ts, server-client.ts, DashboardClient.tsx, InteractiveDiagnostic.tsx, sw.ts, middleware.ts, RouteGuard.tsx, LearnerContext.tsx

## Creating New Codemaps

When creating a new codemap:

1. **Choose a System:** Identify a system or component that needs documentation
2. **Define Traces:** Break down the system into logical execution flows or aspects
3. **Follow Structure:** Use the standardized structure outlined above
4. **Add Motivation:** Explain why each component exists
5. **Provide Details:** Use adaptive subsections that match what the trace actually does
6. **Create Diagrams:** Use ASCII diagrams to visualize flows
7. **Reference Code:** Include accurate file paths and line numbers
8. **Write AI Guides:** Provide Motivation and adaptive narrative Details for each trace

## Codemap Purpose

Codemaps serve as:
- **Architecture Documentation:** Deep technical documentation of system implementation
- **Onboarding Resource:** Help new developers understand complex systems
- **Reference Material:** Quick reference for implementation details
- **Agent Knowledge Base:** Provide structured information for AI agents to understand and work with the codebase
- **Change Tracking:** Document architectural decisions and their rationale

## Maintenance

- Keep codemaps up to date with code changes
- Update line numbers when code is modified
- Add new traces when systems evolve
- Review and improve AI guides based on feedback, especially when they become generic or repetitive
- Ensure all paths and references remain accurate

## Related Documentation

- [ADR (Architecture Decision Records)](../adr/) - Architectural decisions and rationale
- [API Reference](../API_REFERENCE.md) - API documentation
- [Development Guide](../DEVELOPMENT.md) - Development guidelines
