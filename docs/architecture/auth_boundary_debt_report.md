# Auth Boundary Debt Report

Generated at: `2026-05-18T07:38:24Z`

| Item | Value |
|---|---|
| Repository imports | `app.repositories.repositories` |
| LearnerRepository symbol present | False |
| Direct get_by_guardian present | False |

## Remaining debt

- Extract remaining auth repository interactions into canonical AuthService
- Remove auth router repository imports after AuthService extraction
- Remove auth transition ignore_imports from .importlinter
