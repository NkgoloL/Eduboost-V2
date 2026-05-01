# API V2 Overview

The V2 API is introduced incrementally alongside the legacy runtime.

Current V2 baseline endpoints:

- `GET /health`
- `POST /api/v2/auth/session`
- `POST /api/v2/auth/refresh`
- `GET /api/v2/learners/{learner_id}`
- `POST /api/v2/diagnostics/{learner_id}`
- `POST /api/v2/study-plans/{learner_id}`
- `GET /api/v2/parents/{guardian_id}/reports/{learner_id}`
- `GET /api/v2/audit`

The V2 slice now includes:
- Redis-backed quota enforcement
- semantic-style response caching for diagnostics
- BackgroundTasks-based async logging hooks
