# Auth Service Extraction Report

Generated at: `2026-05-19T22:55:57Z`

Repository imports remaining in auth router: `0`

## Repository imports


## Remaining business-logic extraction debt

- Move register orchestration into AuthApplicationService.register
- Move login orchestration into AuthApplicationService.login
- Move refresh orchestration into AuthApplicationService.refresh
- Move dev-session bootstrap into AuthApplicationService.create_dev_session
- Add HTTP dependency-override integration tests for each auth lifecycle path
