---
title: Frontend-Backend Validation Checklist
status: release-record
owner: release-management
reviewers: [release-management, evidence-custodian, documentation-governance]
audience: release-reviewer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-06
review_interval_days: 180
evidence_command: make docs-housekeeping-stage7-check
code_anchors: [docs/release, docs/documentation/stage_7_release_archive_backlog_codemaps_governance.md]
---

# Frontend-Backend Validation Checklist

Use this before marking a local or release build healthy.

## Local Stack

- Start dependencies: `docker compose up -d postgres redis`
- Confirm API config: `NEXT_PUBLIC_API_URL=http://localhost:8000/api/v2`
- Confirm backend readiness: `curl http://localhost:8000/health`
- Confirm frontend readiness: open `http://localhost:3050`

## Learner Smoke

- Create a non-production learner session through `/api/v2/auth/dev-session`.
- Dashboard loads mastery and gamification without an error banner.
- Study plan generation returns a completed job with `days` and `schedule`.
- Badges page loads a gamification profile with `earned_badges`.
- Lesson generation returns a completed job.
- Completing a lesson and awarding XP updates the gamification profile.

## Test Commands

- Backend contract smoke: `.venv/bin/python -m pytest -q tests/integration/test_learner_flow_contract.py --no-cov`
- Auth lifecycle: `.venv/bin/python -m pytest -q tests/integration/test_auth_refresh.py --no-cov`
- Frontend type check: `node node_modules/typescript/bin/tsc --noEmit`
- Frontend journey tests: `npm run test -- LearnerPages ApiLayer`
- Critical Playwright smoke: `npx playwright test tests/e2e/learner_smoke.spec.ts --project=chromium`

## Release Gate

- No generated files such as `coverage.xml` or `tsconfig.tsbuildinfo` are left in the diff.
- Provider keys may be absent or invalid in local development; lesson generation must still use the offline fallback.
- Production must not expose `/api/v2/auth/dev-session`.
