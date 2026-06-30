---
title: "ADR-001 Rollback Plan — Supabase Auth Restoration"
status: active
owner: frontend
reviewers: [frontend, architecture]
audience: developer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-06-23
review_interval_days: 180
evidence_command: make docs-housekeeping-stage3-check
code_anchors: []
---
# ADR-001 Rollback Plan — Supabase Auth Restoration

```text
Status: Accepted
Date: 2026-05-28
Owner: Frontend Tech Lead + Backend Lead
RC Gate: RC1 (sits between ADR-001 and FE-P1-038)
Reviewers: Backend Lead, POPIA Compliance Officer
Evidence: TODO_V4.1 FE-P0-NEW-001, FE-PR-002 runtime log, Supabase session export script
```

## Goal

Provide an operationally safe procedure to revert the frontend from FastAPI JWT sessions back to the previous Supabase Auth integration if the migration fails mid-release.

## Trigger Conditions

- Prod hotfix requires immediate rollback because JWT cookies are being rejected or audit relays fail.
- POPIA Compliance Officer halts the rollout due to evidence gaps.
- FastAPI auth proxy suffers a blocking outage and no graceful degradation exists.

## Rollback Steps

1. **Freeze new deploys:** Pause the ACA frontend deployment and notify incident response.
2. **Re-enable Supabase client:**
   - Restore `@supabase/auth-helpers-nextjs` and Supabase env vars from Azure Key Vault snapshot.
   - Revert `src/app/api/auth/*` handlers and middleware to the Supabase-backed versions (`git checkout <rollback-tag> -- path`).
3. **Disable FastAPI auth proxy:**
   - Toggle feature flag `NEXT_PUBLIC_USE_FASTAPI_AUTH=false` (flag added in FE-PR-005) and redeploy the frontend.
   - Update backend ingress to stop issuing JWT cookies to the frontend surface.
4. **Session continuity:** Ask Supabase to invalidate sessions issued after the FastAPI cutover timestamp (recorded in release evidence) to avoid mixed-mode sessions.
5. **Audit + documentation:** Attach the rollback summary to `docs/adr/frontend/sign-off.md` and release evidence. POPIA audit log must note that Supabase regained control temporarily.

## Re-Enable Plan

- Complete root-cause analysis, update ADR-001 with findings, and capture additional evidence (tests, scripts) before reattempting the migration.
- Require sign-off from Backend Lead + POPIA Compliance Officer before turning FastAPI auth back on.

## Compliance & Evidence

- Supabase session export script stored under `scripts/supabase/export_sessions.py` (already present for legacy runtime).
- Release evidence must contain timestamps for when JWT cookies were enabled/disabled to satisfy audit traceability.
