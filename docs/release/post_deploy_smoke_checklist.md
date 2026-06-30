# Post-Deploy Smoke Checklist

Status: pending staging execution
Environment: staging or disposable production-like environment

| Check | Expected result | Evidence field |
|---|---|---|
| `GET /api/v2/health/deep` | 2xx response with required dependency signals | URL, response body, timestamp |
| Auth register/login/refresh/logout | Non-500 success and clean failure paths | command output or browser trace |
| Dashboard load | Authenticated learner sees dashboard | screenshot or Playwright output |
| Lesson generation | Learner can request a lesson without server error | request/response or trace |
| Consent grant | Consent state is persisted and audited | API output and audit event |
| POPIA export | Export route returns expected learner data package | API output and file/hash |
| CORS/security headers | Expected frontend origin and security headers are present | header output |

## Completion Rule

Do not mark this checklist complete until every row has runtime evidence from the exact release candidate.