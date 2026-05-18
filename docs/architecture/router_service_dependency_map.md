# Router Service Dependency Map

Generated at: `2026-05-18T07:38:26Z`

| Router | Dependencies | Services/modules | Repositories | Database imports |
|---|---|---|---|---|
| `app/api_v2_routers/0005_irt_seed.py` | - | - | - | - |
| `app/api_v2_routers/__init__.py` | - | - | - | - |
| `app/api_v2_routers/api_v2.py` | - | - | - | - |
| `app/api_v2_routers/assessments.py` | - | `app.services.assessment_service_v2` | - | `app.core.database`, `sqlalchemy.ext.asyncio` |
| `app/api_v2_routers/audit.py` | - | `app.services.audit_service` | - | - |
| `app/api_v2_routers/auth.py` | `app.api_v2_deps.auth_runtime` | `app.services.auth_token_claims`, `app.services.fourth_estate` | `app.repositories.repositories` | `app.core.database`, `sqlalchemy.ext.asyncio` |
| `app/api_v2_routers/billing.py` | - | `app.services.fourth_estate`, `app.services.stripe_service` | - | `app.core.database`, `sqlalchemy.ext.asyncio` |
| `app/api_v2_routers/consent.py` | - | `app.modules.consent.service` | `app.repositories.repositories` | `app.core.database`, `sqlalchemy.ext.asyncio` |
| `app/api_v2_routers/consent_renewal.py` | - | `app.services.consent_renewal_service` | - | `app.core.database` |
| `app/api_v2_routers/diagnostics.py` | - | `app.modules.diagnostics`, `app.modules.diagnostics.diagnostic_session_service`, `app.modules.diagnostics.item_bank_service`, `app.modules.diagnostics.session_recovery_service`, `app.services.caps_validator`, `app.services.diagnostic`, `app.services.diagnostic_data_integrity` | `app.repositories.diagnostic_session_repository`, `app.repositories.item_bank_repository`, `app.repositories.mastery_repository`, `app.repositories.repositories` | `app.core.database`, `sqlalchemy.ext.asyncio` |
| `app/api_v2_routers/ether.py` | - | `app.services.ether_service` | - | `app.core.database`, `sqlalchemy.ext.asyncio` |
| `app/api_v2_routers/gamification.py` | - | `app.services.fourth_estate`, `app.services.gamification_service_v2` | `app.repositories.gamification_repository`, `app.repositories.repositories` | `app.core.database`, `sqlalchemy.ext.asyncio` |
| `app/api_v2_routers/jobs.py` | - | - | - | - |
| `app/api_v2_routers/judiciary.py` | - | `app.services.judiciary_service_v2` | - | - |
| `app/api_v2_routers/learners.py` | - | `app.modules.progress.progress_timeline_service`, `app.services.fourth_estate` | `app.repositories.mastery_repository`, `app.repositories.repositories` | `app.core.database`, `sqlalchemy.ext.asyncio` |
| `app/api_v2_routers/lessons.py` | - | `app.modules.lessons`, `app.modules.lessons.service`, `app.services.lesson_authorization` | - | `app.core.database`, `sqlalchemy.ext.asyncio` |
| `app/api_v2_routers/onboarding.py` | - | `app.services.ether` | `app.repositories.repositories` | `app.core.database`, `sqlalchemy.ext.asyncio` |
| `app/api_v2_routers/parents.py` | - | `app.services.consent`, `app.services.executive`, `app.services.fourth_estate` | `app.repositories.repositories` | `app.core.database`, `sqlalchemy.ext.asyncio` |
| `app/api_v2_routers/popia.py` | `app.api_v2_deps.consent_lifecycle` | `app.modules.consent.service`, `app.services.fourth_estate`, `app.services.popia_service` | - | - |
| `app/api_v2_routers/study_plans.py` | - | `app.services.audit_service`, `app.services.study_plan_service_v2`, `app.services.telemetry` | `app.repositories.repositories`, `app.repositories.study_plan_repository` | `app.core.database`, `sqlalchemy.ext.asyncio` |
| `app/api_v2_routers/system.py` | - | `app.services.system_service_v2` | - | - |
| `app/api_v2_routers/test_api.py` | - | - | - | - |
| `app/api_v2_routers/test_services.py` | - | `app.services.diagnostic`, `app.services.ether`, `app.services.judiciary` | - | - |
