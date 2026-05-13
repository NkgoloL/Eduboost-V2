# 8. Frontend production readiness and UX

## 8.1 Environment and frontend security

- [verify] `P0` Separate browser-safe environment variables from server-only secrets.
- [verify] `P0` Ensure no secrets are exposed through `NEXT_PUBLIC_*`.
- [verify] `P0` Add frontend env validation script to CI.
- [verify] `P0` Add safe public API URL configuration.
- [verify] `P0` Add typed environment schema.
- [verify] `P1` Add staging frontend env validation.
- [verify] `P1` Add production frontend env validation.
- [verify] `P1` Document frontend environment variables.

## 8.2 API client

- [verify] `P0` Update typed API client to consume canonical PR-002R envelope.
- [verify] `P0` Normalize error handling against canonical error envelope.
- [verify] `P0` Add auth token handling.
- [verify] `P0` Add refresh handling.
- [verify] `P0` Add request ID propagation.
- [verify] `P0` Add typed response parsing.
- [verify] `P0` Add typed error parsing.
- [verify] `P1` Add retry behavior for safe idempotent requests.
- [verify] `P1` Add network-offline detection.
- [verify] `P1` Add stale-data handling.
- [verify] `P1` Add API client tests.

## 8.3 Auth and onboarding UX

- [verify] `P0` Complete guardian signup screen.
- [verify] `P0` Complete guardian login screen.
- [verify] `P0` Complete logout UX.
- [verify] `P0` Complete session-expiry UX.
- [verify] `P0` Complete password reset request screen.
- [verify] `P0` Complete password reset completion screen.
- [verify] `P0` Complete email verification UX.
- [verify] `P0` Complete learner profile creation.
- [verify] `P0` Complete grade selection.
- [verify] `P0` Complete subject selection.
- [verify] `P0` Complete parental consent capture.
- [verify] `P0` Complete onboarding completion route.
- [verify] `P1` Add onboarding progress indicator.
- [verify] `P1` Add recoverable onboarding state.
- [verify] `P1` Add onboarding E2E test.

## 8.4 Protected routes

- [verify] `P0` Add protected route guard for learner dashboard.
- [verify] `P0` Add protected route guard for parent dashboard.
- [verify] `P0` Add protected route guard for teacher dashboard.
- [verify] `P0` Add protected route guard for admin dashboard.
- [verify] `P0` Add role-based redirect rules.
- [verify] `P0` Add unauthorized state.
- [verify] `P0` Add forbidden state.
- [verify] `P1` Add tests for route guards.

## 8.5 Learner UX

- [verify] `P0` Complete learner dashboard.
- [verify] `P0` Show study plan.
- [verify] `P0` Show next recommended lesson.
- [verify] `P0` Show progress.
- [verify] `P0` Show streak if gamification enabled.
- [verify] `P0` Show weak topics.
- [verify] `P0` Show recommended next activity.
- [verify] `P0` Complete diagnostic question display.
- [verify] `P0` Complete diagnostic progress indicator.
- [verify] `P0` Complete diagnostic answer submission.
- [verify] `P0` Complete diagnostic result summary.
- [verify] `P0` Complete lesson explanation view.
- [verify] `P0` Complete worked example view.
- [verify] `P0` Complete practice question interaction.
- [verify] `P0` Complete hints.
- [verify] `P0` Complete answer reveal.
- [verify] `P0` Complete feedback capture.
- [verify] `P0` Complete report-content issue flow.
- [verify] `P1` Add pause/resume diagnostic UX.
- [verify] `P1` Add offline-friendly lesson state.
- [verify] `P2` Add learner personalization settings.

## 8.6 Parent/guardian UX

- [verify] `P0` Complete parent dashboard.
- [verify] `P0` Show child progress.
- [verify] `P0` Show consent status.
- [verify] `P0` Show recommended support actions.
- [verify] `P0` Show reports.
- [verify] `P0` Show privacy controls.
- [verify] `P0` Add data export request UI.
- [verify] `P0` Add erasure request UI.
- [verify] `P0` Add data correction request UI.
- [verify] `P0` Add processing restriction request UI.
- [verify] `P1` Add subscription/billing UI.
- [verify] `P1` Add consent renewal UI.
- [verify] `P1` Add notification preferences UI.
- [verify] `P2` Add weekly parent report view.
- [verify] `P2` Add “how to help at home” guidance.

## 8.7 Teacher/admin UX

- [verify] `P1` Build teacher dashboard if in beta scope.
- [verify] `P1` Build admin console if in beta scope.
- [verify] `P1` Build audit dashboard.
- [verify] `P1` Build content review queue.
- [verify] `P2` Build class-level diagnostics.
- [verify] `P2` Build intervention groups.
- [verify] `P2` Build topic heatmaps.
- [verify] `P2` Build curriculum coverage admin view.

## 8.8 Accessibility and mobile

- [verify] `P0` Meet WCAG 2.1 AA for signup.
- [verify] `P0` Meet WCAG 2.1 AA for login.
- [verify] `P0` Meet WCAG 2.1 AA for consent.
- [verify] `P0` Meet WCAG 2.1 AA for diagnostic.
- [verify] `P0` Meet WCAG 2.1 AA for lesson.
- [verify] `P0` Meet WCAG 2.1 AA for dashboards.
- [verify] `P0` Add keyboard navigation tests.
- [verify] `P0` Ensure sufficient color contrast.
- [verify] `P0` Add accessible form validation.
- [verify] `P0` Add semantic headings.
- [verify] `P0` Add landmarks.
- [verify] `P0` Add screen-reader friendly diagnostic questions.
- [verify] `P0` Make all learner flows usable on mobile.
- [verify] `P0` Make all parent flows usable on mobile.
- [verify] `P1` Add responsive layout tests.
- [verify] `P1` Add reduced-motion mode.
- [verify] `P1` Add dyslexia-friendly typography option.
- [verify] `P1` Add text resizing.
- [verify] `P2` Add audio narration if product scope supports it.

## 8.9 PWA and low-data mode

- [verify] `P1` Add or verify service worker.
- [verify] `P1` Add or verify manifest.
- [verify] `P1` Cache app shell.
- [verify] `P1` Add offline-friendly lesson content.
- [verify] `P1` Add offline messaging.
- [verify] `P1` Add compressed assets.
- [verify] `P1` Add low-data mode.
- [verify] `P1` Add PWA installability test.
- [verify] `P1` Add offline E2E test.
- [verify] `P2` Add offline feedback queue.
- [verify] `P2` Add sync-on-reconnect behavior.

---

## 8.10 Repository-side implementation evidence

The repository-side implementation for frontend production readiness is captured by these files:

- `app/frontend/src/lib/productionReadiness/contracts.ts`
- `docs/frontend/production_frontend_env_security_contract.md`
- `docs/frontend/production_frontend_api_client_contract.md`
- `docs/frontend/production_auth_onboarding_ux_contract.md`
- `docs/frontend/production_protected_route_guard_contract.md`
- `docs/frontend/production_learner_parent_ux_contract.md`
- `docs/frontend/production_parent_privacy_controls_contract.md`
- `docs/frontend/production_teacher_admin_scope_contract.md`
- `docs/frontend/production_frontend_ux_accessibility_mobile_contract.md`
- `docs/frontend/production_frontend_pwa_low_data_contract.md`
- `scripts/check_frontend_production_readiness.py`
- `tests/unit/test_frontend_production_readiness.py`

Verification command:

```bash
make frontend-production-readiness-check
```

Boundary: this repository evidence verifies frontend contracts, route/UX readiness evidence, environment-safety controls, API-client behavior expectations, accessibility/mobile scope, and PWA/low-data scope. Live browser testing, human accessibility certification, and staging telemetry remain external release gates.
