# POPIA Router Boundary Repair Report

Generated at: `2026-05-17T21:19:07Z`

**Status:** implemented

- Moved canonical consent service factory to `app/api_v2_deps/consent_lifecycle.py`.
- Moved authenticated actor extraction to dependency module.
- Moved POPIA learner-write wrapper to dependency module.
- Removed direct `app.repositories` import from POPIA router.
