# Staging Smoke Evidence

**Status:** pending runtime execution
<!-- Status: pending runtime execution -->

This file is the stable release gate for staging smoke evidence. It must remain pending until a real staging deployment smoke run is accepted by the release owner.

Latest raw smoke output, when available:

- JSON: `docs/release/staging_smoke_latest.json`
- Markdown: `docs/release/staging_smoke_latest.md`

## Required environment

| Field | Value |
|---|---|
| Staging URL | TODO |
| Commit SHA | TODO |
| Deployment ID | TODO |
| Operator | TODO |
| Timestamp UTC | TODO |

## Required smoke checks

| Check | Expected result | Evidence |
|---|---|---|
| `GET /api/v2/health/deep` | `200 OK` with all critical checks healthy, or documented degraded `503` before acceptance | TODO |
| `GET /openapi.json` | schema available and current | TODO |
| Auth register/login/refresh/logout | success path works; cookies/headers correct | TODO |
| Learner dashboard/read route | object authorization works | TODO |
| Lesson generation route | accepted or expected controlled response | TODO |
| Study plan generation route | accepted or expected controlled response | TODO |
| POPIA data export route | authorized path works; unauthorized path rejected | TODO |
| Security headers | expected headers present | TODO |
| CORS | allowed origin accepted; disallowed origin rejected | TODO |
| Observability | request appears in logs/traces/metrics | TODO |

## Command log

```bash
# paste accepted staging smoke commands and output here
```

## Decision

- [ ] Staging smoke passed and is accepted for release evidence.
- [ ] Staging smoke failed and release is blocked.
- [ ] Staging smoke partially passed; exceptions documented and approved.
