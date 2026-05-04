# Frontend-Backend Recovery Roadmap

Updated: 2026-05-04  
Source: user-reported frontend failures plus screenshots from the learner flow

Status legend:

- `[open]` not started
- `[in-progress]` being worked on
- `[done]` completed
- `[blocked]` waiting on another fix

## Problem Summary

The current frontend is reachable, but several core learner journeys are not
working end to end:

- Dashboard loads with an error banner instead of real progress data.
- Study plan page shows an error state and falls back to placeholder content.
- Badges page shows an error state and empty achievement data.
- Lesson generation fails after subject and topic selection.
- Buttons and interactive controls appear unreliable because route transitions
  work, but the underlying API actions fail.
- Some UI polish has regressed while errors are showing, including raw HTML
  entities and awkward layout/text presentation.

## Evidence From The Current Screens

1. `Dashboard` shows: `Failed to load dashboard data. Please try again.`
2. `Study Plan` shows: `Failed to load your study plan. Please try again.`
3. `Badges` shows: `Failed to load your achievements. Keep learning to earn more!`
4. `Lesson` shows: `Failed to generate lesson. Our AI is taking a quick nap, please try again!`
5. The learner flow still renders fallback values such as `0%`, empty badges,
   and generic rest-day content even after API failures.
6. Copy/layout regressions are visible, for example:
   - `Let&apos;s` rendering literally on the dashboard
   - `MonTODAY` appearing jammed together on the study-plan page
   - lesson subject/topic cards looking poorly styled in the broken state

## Phase 1: Connectivity and Reproduction

1. `[done]` Reproduce the learner flow failures with the frontend and backend
   running together and capture the exact failing HTTP requests for:
   - dashboard
   - study plan
   - badges
   - lesson generation
2. `[done]` Verify the active API base URL, container networking, and local
   environment wiring for `NEXT_PUBLIC_API_URL`, backend port exposure, and
   CORS.
3. `[done]` Confirm that the frontend is sending the correct auth token for
   learner-scoped calls and that the backend accepts that token shape.
4. `[done]` Check whether the backend routes used by the frontend still match
   the current V2 route contracts and payload shapes.

## Phase 2: Backend Contract Repair

5. `[done]` Restore dashboard data loading by validating and fixing the
   mastery and gamification endpoints used by:
   - `LearnerService.getMastery(...)`
   - `LearnerService.getGamificationProfile(...)`
6. `[done]` Restore study-plan loading by validating the study-plan endpoint,
   response schema, and learner lookup path.
7. `[done]` Restore badges and achievements loading by validating the
   gamification profile endpoint and badge payload format.
8. `[done]` Restore lesson generation by validating:
   - request payload from the frontend
   - lesson-generation endpoint availability
   - async job completion or direct response flow
   - required provider/config dependencies in local development
9. `[open]` Verify that lesson completion, XP award, and post-lesson state
   refresh work after lesson generation succeeds.

## Phase 3: Frontend Behavior Repair

10. `[done]` Fix broken learner-page error handling so failed API calls do not
    quietly render misleading fallback success content underneath the error
    banner.
11. `[done]` Add clear empty, loading, offline, and failed states for
    dashboard, plan, badges, and lesson pages so the learner experience is
    consistent and understandable.
12. `[done]` Make the primary learner CTAs reliable and explicit:
    - `Start New Lesson`
    - `Take Assessment`
    - `Start Adventure`
    - study-plan item `Start` buttons
13. `[done]` Audit the frontend service layer for request/response mismatch,
    especially where the UI assumes fields that may not exist in the active V2
    responses.

## Phase 4: UI Regression Cleanup

14. `[done]` Replace raw HTML entity artifacts like `Let&apos;s` with clean
    rendered copy.
15. `[done]` Fix layout glitches such as `MonTODAY` on the study-plan page and
    spacing/alignment issues in the learner panels.
16. `[done]` Repair lesson subject/topic card styling so the chooser looks like
    a deliberate product surface instead of fallback browser controls.
17. `[open]` Review dark-theme contrast, card backgrounds, and button states on
    broken and recovered screens.

## Phase 5: Test and Release Guardrails

18. `[done]` Add or repair frontend tests that cover the learner data-fetching
    journeys for dashboard, plan, badges, and lesson generation.
19. `[done]` Add backend contract tests for the specific V2 endpoints used by
    the current frontend learner flow.
20. `[open]` Add an end-to-end smoke test for the critical learner journey:
    login -> dashboard -> assessment or lesson -> study plan -> badges.
21. `[open]` Add a pre-release validation checklist that confirms the frontend
    can talk to the backend in the local Docker stack before marking a build as
    healthy.

## Likely Hotspots

The screenshots and current code suggest these areas deserve first attention:

- `app/frontend/src/lib/api/client.ts`
- `app/frontend/src/app/(learner)/dashboard/page.tsx`
- `app/frontend/src/app/(learner)/plan/page.tsx`
- `app/frontend/src/app/(learner)/badges/page.tsx`
- `app/frontend/src/app/(learner)/lesson/page.tsx`
- `app/api_v2.py`
- the V2 learner, lesson, study-plan, and gamification routes/services they
  depend on

## Definition of Done

This roadmap is complete when:

- dashboard data loads without the current error banner
- study plans load real learner data
- badges load real progress and earned badge data
- lessons generate successfully from the UI
- learner buttons trigger working backend behavior instead of dead ends
- the visibly broken copy/layout issues are cleaned up
- the happy path is covered by automated smoke coverage

## Progress Notes

- Added a non-production dev-session bootstrap path so the learner bypass login
  creates a real guardian token, learner record, and active consent instead of
  a fake local-only persona.
- Rewired the gamification backend path toward the active learner model so
  dashboard and badges can fetch against a real repository instead of a broken
  placeholder query.
- Normalized study-plan schedule output to the day keys the frontend expects.
- Added a local lesson-generation fallback for environments without configured
  LLM provider keys.
- Started cleaning visible learner-flow UI regressions in the dashboard, study
  plan, and lesson chooser.
- Improved frontend error normalization and handling for V2 API contracts.
- Fixed `MonTODAY` layout and polished the lesson chooser UI.
- Updated E2E and Vitest contract tests for V2 endpoints.
- Verified backend contracts using `tests/integration/test_learner_flow_contract.py`.
