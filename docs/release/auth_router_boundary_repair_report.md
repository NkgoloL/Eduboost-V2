# Auth Router Boundary Repair Report

Generated at: `2026-05-18T06:56:32Z`

**Status:** implemented

- Added `app/api_v2_deps/auth_runtime.py` dependency module.
- Added `app/services/auth_runtime_boundary.py` runtime context service.
- Removed direct `LearnerRepository` construction/import from auth router.
- Routed guardian learner scope lookup through `AuthRuntimeContext.guardian_learner_ids`.

## Boundary

This batch closes the direct learner-repository refresh allowance. Remaining auth repository imports must be handled by a later full AuthService extraction batch.
