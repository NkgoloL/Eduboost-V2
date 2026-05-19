# Auth Service Extraction Repair Report

Generated at: `2026-05-19T18:44:04Z`

**Status:** implemented

## Implemented

- Added `app/services/auth_application_service.py`.
- Added `app/api_v2_deps/auth_service.py`.
- Replaced direct auth router repository constructors with `auth_service.<repo>` handles.
- Removed direct `app.repositories` imports from `app/api_v2_routers/auth.py`.
- Preserved `auth.py` eager route model evaluation by rejecting future annotations.

## Import-linter allowances removed


## Remaining debt

- Move auth business logic from router into AuthApplicationService methods in smaller semantic slices.
- Add HTTP integration tests for register/login/refresh/dev-session with dependency overrides.
