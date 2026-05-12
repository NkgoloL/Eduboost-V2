# EduBoost V2 — Production Readiness Backlog

**Purpose:** This document serves as the high-level index for the granular implementation backlog required to move EduBoost V2 to a production-ready, public-beta-safe platform.

The backlog has been split into domain-specific files for better maintainability and parallel execution.

## Backlog Domains

1.  **[Repository State](docs/backlog/production_readiness/00_repository_state_and_canonical_source_of_truth.md)** — Governance, branch policy, and verification automation.
2.  **[Backend Runtime & API Contract](docs/backlog/production_readiness/01_pr-002r_replacement_—_backend_runtime_and_api_contract_baseline.md)** — Canonical runtime, router registration, and OpenAPI contract.
3.  **[Architecture & Boundaries](docs/backlog/production_readiness/02_backend_architecture_modular_monolith_and_dependency_boundaries.md)** — Modular monolith enforcement and metaphor cleanup.
4.  **[Auth & Authorization](docs/backlog/production_readiness/03_authentication_sessions_rbac_and_object-level_authorization.md)** — RBAC, session policy, and object-level security.
5.  **[POPIA & Privacy](docs/backlog/production_readiness/04_popia_consent_privacy_data-subject_rights_and_audit.md)** — Consent lifecycle, data subject rights, and audit integrity.
6.  **[Database & Performance](docs/backlog/production_readiness/05_database_persistence_migrations_and_performance.md)** — Schema readiness, migrations, and query latency.
7.  **[AI & LLM Safety](docs/backlog/production_readiness/06_ai_llm_safety_lesson_generation_and_caps_validation.md)** — LLM gateway, PII safety, and CAPS alignment.
8.  **[Diagnostics & Mastery](docs/backlog/production_readiness/07_diagnostics_assessment_item_bank_and_mastery_model.md)** — IRT engine, item bank, and remediation logic.
9.  **[Frontend & UX](docs/backlog/production_readiness/08_frontend_production_readiness_and_ux.md)** — API client, protected routes, and accessibility (WCAG).
10. **[Billing & Payments](docs/backlog/production_readiness/09_billing_subscriptions_payments_and_monetization.md)** — Provider integration, webhooks, and pricing rules.
11. **[Notifications](docs/backlog/production_readiness/10_notifications_and_communication.md)** — Transactional templates and delivery controls.
12. **[Observability](docs/backlog/production_readiness/11_observability_metrics_logging_tracing_and_alerting.md)** — Prometheus metrics, structured logging, and alerting.
13. **[CI/CD & Infrastructure](docs/backlog/production_readiness/12_ci_cd_infrastructure_deployment_docker_and_environments.md)** — Pipeline correctness and environment management.
14. **[Backup & Recovery](docs/backlog/production_readiness/13_backup_restore_and_disaster_recovery.md)** — RPO/RTO, restore drills, and Redis resilience.
15. **[Quality & Evidence](docs/backlog/production_readiness/14_testing_release_evidence_and_quality_gates.md)** — Test coverage, E2E (Playwright), and release evidence bundles.
16. **[Security Posture](docs/backlog/production_readiness/15_security_posture_and_threat_modeling.md)** — Threat modeling, secrets management, and pen-test readiness.
17. **[Operations & Support](docs/backlog/production_readiness/16_incident_response_operations_and_support.md)** — Incident response, emergency controls, and support runbooks.
18. **[Documentation & Claims](docs/backlog/production_readiness/17_documentation_adrs_and_claim_discipline.md)** — ADRs, production docs, and claim verification.
19. **[Beta Launch Scope](docs/backlog/production_readiness/18_beta_launch_staging_acceptance_and_product_scope.md)** — Staging acceptance, launch scope, and go/no-go criteria.
20. **[Post-Production Roadmap](docs/backlog/production_readiness/19_roadmap_after_production-readiness_baseline.md)** — Product expansion and technical scale.

## Final Release Gate
-   **[Final Release-Blocker Checklist](docs/backlog/production_readiness/20_final_release-blocker_checklist.md)**

---

**Execution Rule:** No item is considered complete unless there is **implementation evidence** and **verification evidence** (green CI, staging run, or release-evidence artifact).
