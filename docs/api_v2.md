# API V2 Overview

The V2 API is the supported EduBoost runtime.

Operational endpoints:

- `GET /health`
- `GET /ready`
- `GET /api/v2/health/deep`
- `GET /metrics`
- `POST /api/v2/auth/login`
- `POST /api/v2/auth/refresh`
- `GET /api/v2/learners/{learner_id}`
- `GET /api/v2/learners/{learner_id}/mastery`
- `POST /api/v2/lessons/generate`
- `POST /api/v2/study-plans/generate/{learner_id}`
- `GET /api/v2/jobs/{job_id}`
- `GET /api/v2/parents/{guardian_id}/dashboard`
- `GET /api/v2/parents/{guardian_id}/export`
- `DELETE /api/v2/learners/{learner_id}`

The V2 slice includes:

- Redis-backed job polling for long-running AI work
- daily quotas by subscription tier
- semantic lesson caching
- strict LLM schema validation
- append-only audit logging
- POPIA consent gating and erasure flows
