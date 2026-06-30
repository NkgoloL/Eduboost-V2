# FE-PR-007 Handover — Lesson completion + XP boundary

## Scope
- Added `LessonCompletionContract` fixture to `src/lib/learner/server-loaders.ts` so the lesson shell knows the XP award, audit actor, and offline queue policy up front.
- Introduced `src/lib/learner/lesson-completion-boundary.ts` (server action) that simulates the transactional completion + XP write, returning typed audit evidence.
- Refactored `LessonEntryClient` to consume the contract, call the server boundary, and drive explicit completion states (idle/pending/queued/success/error) plus offline queuing with `queueLessonSync`.
- Updated `InteractiveLesson` to accept the new completion props, render success/queued/error banners, and reference the XP award from the contract instead of hard-coded copy.
- Extended routing + learner journey tests to cover completion success, server failure, and offline queue persistence. Updated entry portal tests for the new props.

## Lesson completion boundary
| Piece | Purpose | Source |
| --- | --- | --- |
| `LessonCompletionContract` | Describes XP award, audit metadata, and offline queue behavior. Hydrates `LessonEntryClient` props. | `src/lib/learner/server-loaders.ts` |
| `completeLessonTransaction` server action | Fixture-backed transactional handler that returns `{ completionStatus, xpStatus, auditEventId }`. | `src/lib/learner/lesson-completion-boundary.ts` |
| Client island wiring | Uses the contract + server action to set completion state, show banners, badge XP, and refresh learner context. | `src/components/learner/LessonEntryClient.tsx`, `src/components/eduboost/InteractiveLesson.tsx` |

The boundary preserves `dynamic = "force-dynamic"` on the lesson route and continues to run entirely in RSC context while still exposing client-side offline queue fallbacks.

## Client UX details
- **Pending:** CTA shows spinner (`isCompleting`) while server action resolves.
- **Success:** Banner surfaces `XP synced • Audit ref {uuid}` and we push back to `/dashboard` after refreshing context.
- **Error:** Banner explains XP couldn’t sync; learner stays on lesson page and can retry once connected.
- **Offline:** If `navigator.onLine === false`, completion writes go into `queueLessonSync` with a message and immediate redirect to `/dashboard` (persistence proof for FE-PR-007).
- Copy still references existing CTA labels ("Claim My Stars") in the real UI; tests use the mocked button label.

## Tests & evidence
- `__tests__/RoutingIntegration.test.tsx`
  - Success path asserts server boundary input + redirect.
  - Failure path waits for the new error banner text.
  - Offline path verifies `queueLessonSync` is invoked before redirect.
- `src/__tests__/LearnerJourneys.test.ts`
  - Confirms lesson shell still references offline copy + `completionState` wiring.
- `__tests__/EntryAndPortal.test.tsx`
  - Updated portal smoke tests to pass the new props to `InteractiveLesson` so parent UI coverage reflects the RSC boundary.

## Verification commands
| Command | Result |
| --- | --- |
| `pnpm run type-check` | ✅ |
| `pnpm run lint` | ✅ |
| `pnpm test` | ✅ (RoutingIntegration still logs the pre-existing FE-TEST-ACT-001 act warning) |
| `pnpm run build` | ✅ |
| `ANALYZE=true pnpm run build` | ✅ (reports in `.next/analyze/{client,edge,nodejs}.html`) |

## Follow-ups / risks
1. **Backend wiring:** The fixture-backed `completeLessonTransaction` should be swapped for a real transactional API once the lesson completion endpoint exposes XP + audit responses.
2. **Offline sync telemetry:** When offline queue events flush, we should emit audit signals mirroring the server boundary to keep POPIA evidence consistent.
3. **FE-TEST-ACT-001:** LearnerProvider hydration still emits the `act(...)` warning in RoutingIntegration. Documented already; fix tracked separately.
