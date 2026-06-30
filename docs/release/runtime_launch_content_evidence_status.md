# Runtime Launch Content Evidence Status

Captured at: 2026-05-25T08:35:24Z
Deployed SHA: 6b68736
Backend deploy ID: dep-d89vt47r43ps73e3cd20
Frontend deploy ID: dep-d8a00ur7uimc739v13p0

## Summary

The Grade 4 Mathematics launch content slice is deployed, seeded, and verified in the live Render and Supabase-backed runtime. The green launch scope is 4.M.1.1, 4.M.1.2, 4.M.1.3.

## Health

| Check | Status |
|---|---|
| Backend /health | ok |
| Deep health | ok |
| Postgres | ok |
| Migrations | ok |
| Google LLM | ok |
| Frontend HTTP 200 | true |

## Launch Content Evidence

| Metric | Value |
|---|---:|
| Diagnostic items approved per launch ref | 40 |
| Diagnostic items expected per launch ref | 40 |
| Diagnostic items approved total | 120 |
| Lessons approved total | 24 |
| Answer-key verification | 100% |
| Green launch refs | 3 |

| CAPS Ref | Diagnostic Items Approved | Lessons Approved | Coverage Ratio |
|---|---:|---:|---:|
| 4.M.1.1 | 40 | 8 | 1.0 |
| 4.M.1.2 | 40 | 8 | 1.0 |
| 4.M.1.3 | 40 | 8 | 1.0 |

## Implementation Roadmap Taken

1. Confirm Render backend and frontend service IDs, URLs, and deploy branch.
2. Commit generated CAPS topic maps, diagnostic item bank, lesson bank, blueprints, study-plan templates, seeders, and validation tooling.
3. Push the same deploy SHA to both origin/master and origin/main because Render deploys main while the local checkout tracks master.
4. Redeploy backend and frontend from explicit commit SHAs.
5. Attempt direct Render one-off seed jobs and record that the current Render plan blocks one-off jobs and non-interactive SSH.
6. Harden seeders so diagnostic items load the new topic-map path and lesson rows can use a disabled system seed owner and learner.
7. Add an idempotent production startup seeder that checks live coverage, upserts missing approved diagnostic items and lessons, and skips once coverage is complete.
8. Fix live seed blockers by ignoring generated artifact metadata fields not present in diagnostic_items and making SQLAlchemy asyncpg PgBouncer-safe for Supabase transaction pooling.
9. Verify live health, deep health, diagnostic item coverage, lesson coverage, and frontend HTTP 200.

## Commands And Checks Used

- python3 scripts/validate_launch_content.py --strict
- python3 scripts/seed_item_bank.py --input data/generated/items/grade4_maths_launch_item_bank.json --status approved --dry-run --abort-on-failure
- python3 scripts/lessons/seed_lesson_bank.py --dry-run
- python3 -m pytest tests/smoke/test_app_import.py tests/unit/test_launch_content_factory.py -q --no-cov
- render deploys create srv-d86pc7mk1jcs739h4r0g --commit 6b68736 --wait --confirm --output json
- render deploys create srv-d88nokn7f7vs73beo9dg --commit 6b68736 --wait --confirm --output json
- curl -fsS https://eduboost-api.onrender.com/health
- curl -fsS https://eduboost-api.onrender.com/api/v2/health/deep
- curl -I -fsS https://eduboos-frontend.onrender.com

## Outstanding Tasks

- LC-OUT-001 Replace startup seeding with an operational seed command: Render one-off jobs were blocked on the current plan, so production startup seeding is the working implementation. Long term, enable Render jobs or add an admin-only seed runner and then disable automatic startup seeding.
- LC-OUT-002 Add a canonical lesson-bank model: Approved launch lessons are currently stored in learner-scoped lessons rows attached to a disabled system seed learner. Add a dedicated lesson_bank or approved_lessons table for canonical reusable content.
- LC-OUT-003 Seed assessment blueprints into runtime storage: Blueprint artifacts exist in the repository, but runtime assessment blueprint persistence and serving still need a canonical repository or table path.
- LC-OUT-004 Expand beyond the Grade 4 Mathematics launch slice: The green slice is limited to 4.M.1.1, 4.M.1.2, and 4.M.1.3. Next phases are full Grade 4 Mathematics and then Grades R-7.
- LC-OUT-005 Add an admin coverage dashboard: Backend coverage APIs exist. The admin frontend still needs a clear coverage panel for diagnostic items, lessons, and blueprints.
- LC-OUT-006 Audit frontend subject and content flows end to end: Backend content is seeded and verified. Still perform browser and user-flow verification for subjects, diagnostics, lesson generation, study plans, assessment attempts, and parent dashboard using real learner sessions.
- LC-OUT-007 Add CI guardrails for launch content: Add tests that reject ORM-incompatible generated artifacts, keep PgBouncer-safe DB config from regressing, and verify seeded launch refs remain green.

## Operational Note

Render one-off jobs were not available on the current account or plan, so this milestone uses an idempotent production startup seeder. The seeder checks coverage first and logs launch_content_seed_skipped_complete when the database already contains the required launch content.
