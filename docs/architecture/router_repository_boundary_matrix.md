# Router Repository Boundary Matrix

Generated at: `2026-06-27T02:18:43Z`

| Router | P0 | Repository imports | Transition allowed | Violations |
|---|---:|---|---|---|
| `app/api_v2_routers/0005_irt_seed.py` | False | - | - | - |
| `app/api_v2_routers/__init__.py` | False | - | - | - |
| `app/api_v2_routers/admin_etl.py` | False | - | - | - |
| `app/api_v2_routers/ai_operations.py` | False | - | - | - |
| `app/api_v2_routers/api_v2.py` | False | - | - | - |
| `app/api_v2_routers/assessments.py` | False | - | - | - |
| `app/api_v2_routers/audit.py` | False | - | - | - |
| `app/api_v2_routers/auth.py` | True | - | - | - |
| `app/api_v2_routers/auth_extended.py` | False | - | - | - |
| `app/api_v2_routers/billing.py` | False | - | - | - |
| `app/api_v2_routers/consent.py` | False | `app.repositories.repositories` | - | `app.repositories.repositories` |
| `app/api_v2_routers/consent_renewal.py` | False | - | - | - |
| `app/api_v2_routers/content_factory.py` | False | `app.repositories.item_bank_repository`, `app.repositories.lesson_repository` | - | `app.repositories.item_bank_repository`, `app.repositories.lesson_repository` |
| `app/api_v2_routers/content_review.py` | False | - | - | - |
| `app/api_v2_routers/curriculum_expansion.py` | False | - | - | - |
| `app/api_v2_routers/diagnostics.py` | False | - | - | - |
| `app/api_v2_routers/ether.py` | False | - | - | - |
| `app/api_v2_routers/gamification.py` | False | `app.repositories.gamification_repository`, `app.repositories.repositories` | - | `app.repositories.gamification_repository`, `app.repositories.repositories` |
| `app/api_v2_routers/generation.py` | False | - | - | - |
| `app/api_v2_routers/irt_quality.py` | False | - | - | - |
| `app/api_v2_routers/jobs.py` | False | - | - | - |
| `app/api_v2_routers/learner_content.py` | False | - | - | - |
| `app/api_v2_routers/learners.py` | False | `app.repositories.mastery_repository`, `app.repositories.repositories` | - | `app.repositories.mastery_repository`, `app.repositories.repositories` |
| `app/api_v2_routers/lessons.py` | True | - | - | - |
| `app/api_v2_routers/onboarding.py` | False | `app.repositories.repositories` | - | `app.repositories.repositories` |
| `app/api_v2_routers/parents.py` | False | `app.repositories.repositories` | - | `app.repositories.repositories` |
| `app/api_v2_routers/popia.py` | True | - | - | - |
| `app/api_v2_routers/study_plans.py` | False | - | - | - |
| `app/api_v2_routers/system.py` | False | - | - | - |
| `app/api_v2_routers/test_api.py` | False | - | - | - |
| `app/api_v2_routers/test_services.py` | False | - | - | - |
| `app/api_v2_routers/tutor.py` | False | - | - | - |
