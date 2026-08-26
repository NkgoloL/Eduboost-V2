---
title: "Router Service Dependency Map"
status: "active"
owner: "engineering"
reviewers: ["engineering"]
audience: "developer"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-08-26"
review_interval_days: 60
evidence_command: "make docs-housekeeping-check"
code_anchors: ["docs/architecture/router_service_dependency_map.md"]
---

# Router Service Dependency Map

Generated at: `2026-08-03T14:01:56Z`

| Router | Dependencies | Services/modules | Repositories | Database imports |
|---|---|---|---|---|
| `app/api_v2_routers/0005_irt_seed.py` | - | - | - | - |
| `app/api_v2_routers/__init__.py` | - | - | - | - |
| `app/api_v2_routers/admin_etl.py` | `app.api_v2_deps.auth` | - | - | - |
| `app/api_v2_routers/ai_operations.py` | `app.api_v2_deps.auth` | `app.services.ai_operations` | - | `app.core.database`, `sqlalchemy.ext.asyncio` |
| `app/api_v2_routers/api_v2.py` | - | - | - | - |
| `app/api_v2_routers/assessments.py` | `app.api_v2_deps.auth` | `app.services.assessment_service_v2` | - | `app.core.database`, `sqlalchemy.ext.asyncio` |
| `app/api_v2_routers/audit.py` | `app.api_v2_deps.auth` | `app.services.audit_service` | - | - |
| `app/api_v2_routers/auth.py` | `app.api_v2_deps.auth`, `app.api_v2_deps.auth_runtime`, `app.api_v2_deps.auth_service` | `app.services.auth_application_service`, `app.services.auth_token_claims` | - | `app.core.database`, `sqlalchemy.ext.asyncio` |
| `app/api_v2_routers/auth_extended.py` | `app.api_v2_deps.auth` | `app.services.email_service` | - | `app.core.database`, `sqlalchemy.ext.asyncio` |
| `app/api_v2_routers/billing.py` | `app.api_v2_deps.auth` | `app.services.audit_service`, `app.services.stripe_service` | - | `app.core.database`, `sqlalchemy.ext.asyncio` |
| `app/api_v2_routers/commercial_launch.py` | - | `app.modules.commercial_launch` | - | - |
| `app/api_v2_routers/consent.py` | `app.api_v2_deps.auth` | `app.modules.consent.service`, `app.services.popia_service` | `app.repositories.repositories` | `app.core.database`, `sqlalchemy.ext.asyncio` |
| `app/api_v2_routers/consent_renewal.py` | `app.api_v2_deps.auth` | `app.modules.jobs` | - | - |
| `app/api_v2_routers/content_factory.py` | `app.api_v2_deps.auth` | `app.services.content_artifact_lifecycle`, `app.services.content_bulk_review`, `app.services.content_coverage_service`, `app.services.content_factory`, `app.services.content_factory_orchestrator`, `app.services.content_generation.provider_factory`, `app.services.content_generation_executor`, `app.services.content_generation_planner`, `app.services.content_generation_runs`, `app.services.content_learner_read_service`, `app.services.content_production_promotion_executor`, `app.services.content_production_promotion_gate`, `app.services.content_production_read_verification`, `app.services.content_review_queue`, `app.services.content_reviewer_assignment`, `app.services.content_scope_registry`, `app.services.content_seed_promotion`, `app.services.content_staging_preview_service`, `app.services.content_staging_read_verification`, `app.services.content_staging_readiness`, `app.services.content_staging_seed_executor` | `app.repositories.item_bank_repository`, `app.repositories.lesson_repository` | `app.core.database`, `sqlalchemy.ext.asyncio` |
| `app/api_v2_routers/content_quality.py` | - | `app.modules.content_quality.acceptance`, `app.modules.content_quality.readiness` | - | - |
| `app/api_v2_routers/content_review.py` | `app.api_v2_deps.auth` | `app.services.content_answer_key_verification`, `app.services.content_review_governance` | - | `app.core.database`, `sqlalchemy.ext.asyncio` |
| `app/api_v2_routers/controlled_beta.py` | - | `app.modules.controlled_beta` | - | - |
| `app/api_v2_routers/curriculum_expansion.py` | `app.api_v2_deps.auth` | `app.services.curriculum_expansion` | - | `app.core.database`, `sqlalchemy.ext.asyncio` |
| `app/api_v2_routers/diagnostics.py` | `app.api_v2_deps`, `app.api_v2_deps.auth` | `app.modules.diagnostics`, `app.modules.diagnostics.diagnostic_session_service`, `app.modules.diagnostics.item_bank_service`, `app.modules.diagnostics.session_recovery_service`, `app.services.caps_validator`, `app.services.diagnostic`, `app.services.diagnostic_data_integrity`, `app.services.diagnostic_route_integrity`, `app.services.runtime_kg.route_integration` | - | `app.core.database`, `sqlalchemy.ext.asyncio` |
| `app/api_v2_routers/ether.py` | `app.api_v2_deps.auth` | `app.services.ether` | - | - |
| `app/api_v2_routers/gamification.py` | `app.api_v2_deps.auth` | `app.services.fourth_estate`, `app.services.gamification_service_v2` | `app.repositories.gamification_repository`, `app.repositories.repositories` | `app.core.database`, `sqlalchemy.ext.asyncio` |
| `app/api_v2_routers/generation.py` | `app.api_v2_deps.auth` | `app.modules.jobs`, `app.services.batch_generation`, `app.services.content_generation.source_context`, `app.services.llm_provider` | - | `app.core.database`, `sqlalchemy.ext.asyncio` |
| `app/api_v2_routers/irt_quality.py` | `app.api_v2_deps.auth` | `app.modules.jobs`, `app.services.irt_quality_service` | - | `app.core.database`, `sqlalchemy.ext.asyncio` |
| `app/api_v2_routers/jobs.py` | `app.api_v2_deps.auth` | - | - | - |
| `app/api_v2_routers/learner_content.py` | `app.api_v2_deps.auth` | `app.services.content_learner_read_service` | - | `app.core.database`, `sqlalchemy.ext.asyncio` |
| `app/api_v2_routers/learners.py` | `app.api_v2_deps.auth` | `app.modules.progress.progress_timeline_service`, `app.services.popia_service` | `app.repositories.mastery_repository`, `app.repositories.repositories` | `app.core.database`, `sqlalchemy.ext.asyncio` |
| `app/api_v2_routers/lessons.py` | `app.api_v2_deps.auth` | `app.modules.jobs`, `app.modules.lessons`, `app.modules.lessons.service`, `app.services.lesson_authorization` | - | `app.core.database`, `sqlalchemy.ext.asyncio` |
| `app/api_v2_routers/observability_sre.py` | - | `app.modules.observability` | - | - |
| `app/api_v2_routers/onboarding.py` | `app.api_v2_deps.auth` | `app.services.ether` | `app.repositories.repositories` | `app.core.database`, `sqlalchemy.ext.asyncio` |
| `app/api_v2_routers/parents.py` | `app.api_v2_deps.auth` | `app.services.executive`, `app.services.popia_service` | `app.repositories.repositories` | `app.core.database`, `sqlalchemy.ext.asyncio` |
| `app/api_v2_routers/performance_scale_cost.py` | - | `app.modules.performance_scale_cost` | - | - |
| `app/api_v2_routers/popia.py` | `app.api_v2_deps.auth`, `app.api_v2_deps.consent_lifecycle` | `app.modules.consent.service`, `app.services.popia_service` | - | - |
| `app/api_v2_routers/privacy_operations.py` | - | `app.modules.privacy_ops.assurance`, `app.modules.privacy_ops.readiness` | - | - |
| `app/api_v2_routers/production_release.py` | - | `app.modules.production_release` | - | - |
| `app/api_v2_routers/security_assurance.py` | - | `app.modules.security_assurance` | - | - |
| `app/api_v2_routers/study_plans.py` | `app.api_v2_deps.auth` | `app.modules.jobs`, `app.services.runtime_kg.route_integration` | - | `app.core.database`, `sqlalchemy.ext.asyncio` |
| `app/api_v2_routers/system.py` | - | `app.services.system_service_v2` | - | - |
| `app/api_v2_routers/test_api.py` | - | - | - | - |
| `app/api_v2_routers/test_services.py` | - | `app.services.archetype_service`, `app.services.diagnostic`, `app.services.judiciary` | - | - |
| `app/api_v2_routers/tutor.py` | `app.api_v2_deps.auth` | `app.services.learner_tutor`, `app.services.lesson_authorization` | - | `app.core.database`, `sqlalchemy.ext.asyncio` |
| `app/api_v2_routers/vertical_journey.py` | `app.api_v2_deps.auth` | `app.modules.consent.service`, `app.modules.vertical_journey.hardening`, `app.modules.vertical_journey.service`, `app.services.learner_service`, `app.services.runtime_kg.route_integration` | - | `app.core.database`, `sqlalchemy.ext.asyncio` |
