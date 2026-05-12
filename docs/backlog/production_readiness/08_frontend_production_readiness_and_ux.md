# 8. Frontend production readiness and UX

## 8.1 Environment and frontend security

- [ ] `P0` Separate browser-safe environment variables from server-only secrets.
- [ ] `P0` Ensure no secrets are exposed through `NEXT_PUBLIC_*`.
- [ ] `P0` Add frontend env validation script to CI.
- [ ] `P0` Add safe public API URL configuration.
- [ ] `P0` Add typed environment schema.
- [ ] `P1` Add staging frontend env validation.
- [ ] `P1` Add production frontend env validation.
- [ ] `P1` Document frontend environment variables.

## 8.2 API client

- [ ] `P0` Update typed API client to consume canonical PR-002R envelope.
- [ ] `P0` Normalize error handling against canonical error envelope.
- [ ] `P0` Add auth token handling.
- [ ] `P0` Add refresh handling.
- [ ] `P0` Add request ID propagation.
- [ ] `P0` Add typed response parsing.
- [ ] `P0` Add typed error parsing.
- [ ] `P1` Add retry behavior for safe idempotent requests.
- [ ] `P1` Add network-offline detection.
- [ ] `P1` Add stale-data handling.
- [ ] `P1` Add API client tests.

## 8.3 Auth and onboarding UX

- [ ] `P0` Complete guardian signup screen.
- [ ] `P0` Complete guardian login screen.
- [ ] `P0` Complete logout UX.
- [ ] `P0` Complete session-expiry UX.
- [ ] `P0` Complete password reset request screen.
- [ ] `P0` Complete password reset completion screen.
- [ ] `P0` Complete email verification UX.
- [ ] `P0` Complete learner profile creation.
- [ ] `P0` Complete grade selection.
- [ ] `P0` Complete subject selection.
- [ ] `P0` Complete parental consent capture.
- [ ] `P0` Complete onboarding completion route.
- [ ] `P1` Add onboarding progress indicator.
- [ ] `P1` Add recoverable onboarding state.
- [ ] `P1` Add onboarding E2E test.

## 8.4 Protected routes

- [ ] `P0` Add protected route guard for learner dashboard.
- [ ] `P0` Add protected route guard for parent dashboard.
- [ ] `P0` Add protected route guard for teacher dashboard.
- [ ] `P0` Add protected route guard for admin dashboard.
- [ ] `P0` Add role-based redirect rules.
- [ ] `P0` Add unauthorized state.
- [ ] `P0` Add forbidden state.
- [ ] `P1` Add tests for route guards.

## 8.5 Learner UX

- [ ] `P0` Complete learner dashboard.
- [ ] `P0` Show study plan.
- [ ] `P0` Show next recommended lesson.
- [ ] `P0` Show progress.
- [ ] `P0` Show streak if gamification enabled.
- [ ] `P0` Show weak topics.
- [ ] `P0` Show recommended next activity.
- [ ] `P0` Complete diagnostic question display.
- [ ] `P0` Complete diagnostic progress indicator.
- [ ] `P0` Complete diagnostic answer submission.
- [ ] `P0` Complete diagnostic result summary.
- [ ] `P0` Complete lesson explanation view.
- [ ] `P0` Complete worked example view.
- [ ] `P0` Complete practice question interaction.
- [ ] `P0` Complete hints.
- [ ] `P0` Complete answer reveal.
- [ ] `P0` Complete feedback capture.
- [ ] `P0` Complete report-content issue flow.
- [ ] `P1` Add pause/resume diagnostic UX.
- [ ] `P1` Add offline-friendly lesson state.
- [ ] `P2` Add learner personalization settings.

## 8.6 Parent/guardian UX

- [ ] `P0` Complete parent dashboard.
- [ ] `P0` Show child progress.
- [ ] `P0` Show consent status.
- [ ] `P0` Show recommended support actions.
- [ ] `P0` Show reports.
- [ ] `P0` Show privacy controls.
- [ ] `P0` Add data export request UI.
- [ ] `P0` Add erasure request UI.
- [ ] `P0` Add data correction request UI.
- [ ] `P0` Add processing restriction request UI.
- [ ] `P1` Add subscription/billing UI.
- [ ] `P1` Add consent renewal UI.
- [ ] `P1` Add notification preferences UI.
- [ ] `P2` Add weekly parent report view.
- [ ] `P2` Add “how to help at home” guidance.

## 8.7 Teacher/admin UX

- [ ] `P1` Build teacher dashboard if in beta scope.
- [ ] `P1` Build admin console if in beta scope.
- [ ] `P1` Build audit dashboard.
- [ ] `P1` Build content review queue.
- [ ] `P2` Build class-level diagnostics.
- [ ] `P2` Build intervention groups.
- [ ] `P2` Build topic heatmaps.
- [ ] `P2` Build curriculum coverage admin view.

## 8.8 Accessibility and mobile

- [ ] `P0` Meet WCAG 2.1 AA for signup.
- [ ] `P0` Meet WCAG 2.1 AA for login.
- [ ] `P0` Meet WCAG 2.1 AA for consent.
- [ ] `P0` Meet WCAG 2.1 AA for diagnostic.
- [ ] `P0` Meet WCAG 2.1 AA for lesson.
- [ ] `P0` Meet WCAG 2.1 AA for dashboards.
- [ ] `P0` Add keyboard navigation tests.
- [ ] `P0` Ensure sufficient color contrast.
- [ ] `P0` Add accessible form validation.
- [ ] `P0` Add semantic headings.
- [ ] `P0` Add landmarks.
- [ ] `P0` Add screen-reader friendly diagnostic questions.
- [ ] `P0` Make all learner flows usable on mobile.
- [ ] `P0` Make all parent flows usable on mobile.
- [ ] `P1` Add responsive layout tests.
- [ ] `P1` Add reduced-motion mode.
- [ ] `P1` Add dyslexia-friendly typography option.
- [ ] `P1` Add text resizing.
- [ ] `P2` Add audio narration if product scope supports it.

## 8.9 PWA and low-data mode

- [ ] `P1` Add or verify service worker.
- [ ] `P1` Add or verify manifest.
- [ ] `P1` Cache app shell.
- [ ] `P1` Add offline-friendly lesson content.
- [ ] `P1` Add offline messaging.
- [ ] `P1` Add compressed assets.
- [ ] `P1` Add low-data mode.
- [ ] `P1` Add PWA installability test.
- [ ] `P1` Add offline E2E test.
- [ ] `P2` Add offline feedback queue.
- [ ] `P2` Add sync-on-reconnect behavior.

---

