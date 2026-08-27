# Authorization Consolidation Matrix (TSR-6.10, TSR-6.11)

## Policy & Authority Overview
All authorization checks across V2 API endpoints are consolidated under a single authoritative security architecture in `app/security/dependencies.py` and `app/api_v2_deps/auth.py`.

## Authorization Matrix
| Endpoint / Resource | Required Role | Object Ownership Check | Consent Check |
|:---|:---|:---|:---|
| `/learners/{id}` | Learner / Guardian / Admin | `require_learner_read_for_current_user` | `require_active_consent_for_current_user` |
| `/onboarding/submit` | Guardian / Learner | `require_learner_write_for_current_user` | Verified |
| `/consent/*` | Guardian / Admin | Guardian subject matching | N/A |
| `/practice/*` | Learner / Guardian | Session owner verification | Active consent verified |
| `/admin/*` | Admin | Role == `admin` required | N/A |
