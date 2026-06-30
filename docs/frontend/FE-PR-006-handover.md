# FE-PR-006 Handover — Learner Dashboard/Diagnostic/Lesson Server Shells

## Scope
- Created `src/lib/learner/server-loaders.ts` with typed synthetic fixtures (learner, mastery, gamification, lesson) used while backend data is still stabilizing.
- Split learner dashboard/diagnostic/lesson routes into server shells that import dedicated client islands (`DashboardClient`, `DiagnosticEntryClient`, `LessonEntryClient`) per ADR-006.
- Added learner-specific skeleton components for dashboard/diagnostic/lesson loading states.
- Ensured client islands preserve existing CTA/navigation flows, offline handling, mastery updates, XP awards, and error/empty states.
- Updated routing + learner journey integration tests to target the new client islands and shell props.

## RSC Boundaries & Client Islands
| Route | Server component | Client island | Notes |
| --- | --- | --- | --- |
| `/dashboard` | `app/(learner)/dashboard/page.tsx` | `DashboardClient` | Server loader hydrates learner/mastery/gamification before rendering interactive CTA grid. |
| `/diagnostic` | `app/(learner)/diagnostic/page.tsx` | `DiagnosticEntryClient` (wraps `InteractiveDiagnostic`) | Loader seeds learner fixture and allowed subjects; client island still runs adaptive flow. |
| `/lesson` | `app/(learner)/lesson/page.tsx` | `LessonEntryClient` (wraps `InteractiveLesson`) | Loader seeds recommended subject/topic + optional lesson snapshot. |

All shells remain `dynamic = "force-dynamic"` to avoid accidental PPR/streaming per RC guardrails.

## Fixtures & Synthetic Evidence
- Learner fixture: Grade 5 (Naledi) archetype "trailblazer" plus mastery + gamification snapshots.
- Lesson fixture: Tuck-shop fractions lesson with sectioned content; reused for initial lesson view.
- Subject fixture: `AVAILABLE_SUBJECTS_FIXTURE` feeds diagnostic entry UI.
- Fixures live in `src/lib/learner/server-loaders.ts`; future work can swap to real backend fetches without touching route components.

## Loading/Error/Empty States
- `DashboardClient` keeps `DashboardSkeleton`, offline warnings, and `error && !gamification` guard tested via learner journey contracts.
- `LessonEntryClient` still exposes `completionError`, offline cache fallback, XP award handling, and queue/sync messaging.
- `DiagnosticEntryClient` falls back to `DiagnosticSkeleton` until learner context is hydrated, then delegates to `InteractiveDiagnostic` which already handles empty/error flows.

## Accessibility & Guardrails
- Shell components keep route-level headings and CTA ordering from prior implementation.
- No AI tutor, voice, WhatsApp, PWA, analytics, advanced gamification, or guardian portal changes were added.
- Session + proxy guardrails from FE-PR-005 remain untouched (server loaders run in RSC context with `server-only`).
- PPR/streaming remain disabled; pages stay fully dynamic to avoid RC1 gate regressions.

## Test Coverage
- `__tests__/RoutingIntegration.test.tsx` now renders the new client islands with shell props to confirm navigation semantics.
- `src/__tests__/LearnerJourneys.test.ts` still asserts dashboard/lesson client code paths contain the expected error-state strings.
- Full Vitest suite (104 tests) continues to cover services, diagnostics, offline sync, proxies, and contracts.

## Verification Commands
| Command | Result |
| --- | --- |
| `pnpm run type-check` | ✅ |
| `pnpm run lint` | ✅ |
| `pnpm test` | ✅ |
| `pnpm run build` | ✅ |
| `ANALYZE=true pnpm run build` | ✅ (reports in `.next/analyze/{client,edge,nodejs}.html`, bundle sizes unchanged from FE-PR-005 baselines) |

## Follow-ups / Risks
1. **Backend wiring:** Once learner dashboard APIs are stable we can swap the loader fixtures for real fetches (ensuring POPIA compliance and caching strategy).
2. **Additional shells:** Parent/plan/badges routes still run as client components; FE-PR-007 can adopt the same pattern.
3. **FE-TEST-ACT-001 — LearnerProvider hydration warning:** Routing integration tests emit `act(...)` warnings because LearnerProvider sets state in effects. Behavior matches the pre-existing provider pattern, but follow-up work should wrap provider hydration/state refresh in the test harness or refactor initialization once RC2 route shells stabilize.
