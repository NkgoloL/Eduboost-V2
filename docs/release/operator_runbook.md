# Beta Operator Runbook

Status: repository-side runbook ready; pending staging validation

## First-Line Health Checks

- API health: `GET /api/v2/health/deep`
- Frontend: load the deployed beta URL and confirm the login page renders.
- Redis: confirm token/session/cache operations are reachable in the target environment.
- PostgreSQL: confirm migrations are at head and application DB connectivity is healthy.

## Start And Stop

Local stack:

```bash
docker compose up -d postgres redis api frontend
docker compose ps
docker compose logs --tail=100 api frontend
```

Stop local stack:

```bash
docker compose down
```
## Triage Flow

1. Confirm whether the failure is API, frontend, database, Redis, external provider, or content-related.
2. Capture timestamp, commit SHA, environment, user-visible symptom, and request ID if available.
3. Check logs before restarting services.
4. If learner data, consent, audit, or POPIA routes are involved, escalate to the POPIA/legal owner.
5. If auth, authorization, secrets, or payment routes are involved, escalate to the security owner.

## Common Remediation

- API unhealthy: inspect API logs, environment variables, DB connectivity, and migration state.
- Frontend broken: verify deployed artifact, API base URL, CORS headers, and browser console errors.
- Login failures: check auth service logs, Redis availability, token settings, and database user records.
- Lesson generation failures: check provider configuration, quota gates, prompt safety checks, and fallback behavior.
- Consent or export failures: stop beta expansion until audit and POPIA behavior are verified.

## Escalation

| Area | Escalation owner | Required evidence |
|---|---|---|
| Runtime outage | Operations owner | Health output, logs, dashboard link |
| Data/privacy issue | POPIA/legal owner | Affected route, request ID, audit evidence |
| Security issue | Security owner | Reproduction, logs, secret/auth impact |
| Content correctness | Product/content owner | Item ID, CAPS reference, reviewer notes |
| Release rollback | Release owner | Incident summary and rollback recommendation |
## Evidence To Capture During Incidents

- Incident start and end time.
- Environment and commit SHA.
- Health check output.
- Relevant API/frontend/database/Redis logs.
- User impact and affected flows.
- Mitigation or rollback decision.
- Follow-up TODO or issue link.

## Rollback Link

Use `docs/release/rollback_runbook.md` for rollback execution. This runbook is operational triage guidance and does not approve rollback by itself.