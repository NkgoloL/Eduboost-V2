---
title: Phase 15 — Backend-Backed E2E Smoke Authority
status: active-control
owner: roadmap-governance
reviewers: [roadmap-governance, release-management, documentation-governance]
audience: roadmap-reviewer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-06
review_interval_days: 30
evidence_command: make docs-housekeeping-stage7-check
code_anchors: [docs/roadmap, docs/documentation/stage_7_release_archive_backlog_codemaps_governance.md]
---

# Phase 15 — Backend-Backed E2E Smoke Authority

## Status

Control harness prepared. Evidence must be captured separately after this harness lands on protected `master` and Phase 14 live-stack readiness verifies.

## Purpose

Phase 15 proves that EduBoost can run controlled browser/API smoke journeys against a live local runtime stack rather than the Phase 06 mocked Playwright API path.

This slice depends on:

- Phase 13B post-merge protected-branch baseline evidence already merged.
- Phase 14 live-stack readiness evidence already merged and valid.
- Local Postgres and Redis running.
- API running and reporting `/ready` and deep health as HTTP 200.
- Frontend running or startable by Playwright with `NEXT_PUBLIC_API_URL` pointing at the live API.

## Scope

In scope:

- Verify Phase 14 live-stack readiness before capture.
- Probe API health/readiness/deep-health endpoints.
- Probe the frontend root route.
- Probe the frontend `/api/v2/system/health` rewrite into the backend API.
- Run non-mocked Chromium Playwright smoke specs.
- Record evidence with SHA-256 integrity checks.

Out of scope:

- Production release authorisation.
- Deployment authorisation.
- Release tagging.
- Live learner traffic.
- Full production E2E certification.
- Runtime knowledge-graph implementation.

## Evidence Command

```bash
python3 scripts/runtime_readiness/capture_backend_backed_e2e_evidence.py \
  --api-base-url http://127.0.0.1:8000/api/v2 \
  --frontend-base-url http://127.0.0.1:3050 \
  --claim-backend-backed-e2e \
  --e2e-owner "Nkgolo Lebelo" \
  --require-valid \
  --json
```

If the frontend is already running and must not be started by Playwright, add:

```bash
--reuse-existing-frontend
```

## Verification Command

```bash
python3 scripts/runtime_readiness/verify_backend_backed_e2e.py --json
```

## Expected Valid State

```json
{
  "valid": true,
  "backend_backed_e2e_recorded": true,
  "live_stack_readiness_valid": true,
  "e2e_scope": "backend_backed_smoke",
  "mocked_api_used": false,
  "full_production_e2e_claimed": false,
  "production_release_authorised": false,
  "deployment_authorised": false,
  "release_tag_authorised": false,
  "live_learner_traffic_authorised": false,
  "runtime_kg_implementation_claimed": false
}
```

## Boundary

This phase records backend-backed smoke E2E readiness only. It does not authorise production release, deployment, release tagging, live learner traffic, or runtime KG implementation.
