# No False-Closure Status After code_871_910

**Status:** router repository boundary improved; beta remains NO-GO

code_871_910 closes direct repository imports/constructors in `app/api_v2_routers/auth.py` by introducing `AuthApplicationService` as the router dependency boundary.

## Still pending

- Move register/login/refresh/dev-session orchestration into explicit AuthApplicationService methods.
- Add HTTP dependency-override integration tests for auth lifecycle paths.
- Run full remote CI and branch-protection evidence.
- Keep `from __future__ import annotations` out of FastAPI router modules unless app import tests prove otherwise.
