# Router Repository Boundary Matrix

Generated at: `2026-05-17T22:10:22Z`

| Router | P0 | Repository imports | Transition allowed | Violations |
|---|---:|---|---|---|
| `app/api_v2_routers/0005_irt_seed.py` | False | - | - | - |
| `app/api_v2_routers/__init__.py` | False | - | - | - |
| `app/api_v2_routers/api_v2.py` | False | - | - | - |
| `app/api_v2_routers/assessments.py` | False | - | - | - |
| `app/api_v2_routers/audit.py` | False | - | - | - |
| `app/api_v2_routers/auth.py` | True | `app.repositories.repositories` | `app.repositories.repositories` | - |
| `app/api_v2_routers/billing.py` | False | - | - | - |
| `app/api_v2_routers/consent.py` | False | `app.repositories.repositories` | - | `app.repositories.repositories` |
| `app/api_v2_routers/consent_renewal.py` | False | - | - | - |
| `app/api_v2_routers/diagnostics.py` | False | `app.repositories.diagnostic_session_repository`, `app.repositories.item_bank_repository`, `app.repositories.mastery_repository`, `app.repositories.repositories` | - | `app.repositories.diagnostic_session_repository`, `app.repositories.item_bank_repository`, `app.repositories.mastery_repository`, `app.repositories.repositories` |
| `app/api_v2_routers/ether.py` | False | - | - | - |
| `app/api_v2_routers/gamification.py` | False | `app.repositories.gamification_repository`, `app.repositories.repositories` | - | `app.repositories.gamification_repository`, `app.repositories.repositories` |
| `app/api_v2_routers/jobs.py` | False | - | - | - |
| `app/api_v2_routers/judiciary.py` | False | - | - | - |
| `app/api_v2_routers/learners.py` | False | `app.repositories.mastery_repository`, `app.repositories.repositories` | - | `app.repositories.mastery_repository`, `app.repositories.repositories` |
| `app/api_v2_routers/lessons.py` | True | - | - | - |
| `app/api_v2_routers/onboarding.py` | False | `app.repositories.repositories` | - | `app.repositories.repositories` |
| `app/api_v2_routers/parents.py` | False | `app.repositories.repositories` | - | `app.repositories.repositories` |
| `app/api_v2_routers/popia.py` | True | - | - | - |
| `app/api_v2_routers/study_plans.py` | False | `app.repositories.repositories`, `app.repositories.study_plan_repository` | - | `app.repositories.repositories`, `app.repositories.study_plan_repository` |
| `app/api_v2_routers/system.py` | False | - | - | - |
| `app/api_v2_routers/test_api.py` | False | - | - | - |
| `app/api_v2_routers/test_services.py` | False | - | - | - |
