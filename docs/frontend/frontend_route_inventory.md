# Frontend Route Inventory

## Purpose

This inventory records frontend route, page, and journey-related surfaces.

## Required Journey Areas

- learner onboarding
- learner dashboard
- diagnostic start and submit
- lesson generation and lesson view
- study plan or practice flow
- parent dashboard and learner progress
- consent and trust surfaces

## Discovered Surfaces

| Path | Route markers | Journey markers |
| --- | --- | --- |
| `app/frontend/.next/server/app/(auth)/login/page.js` | `Route, path:` | `learner, parent, dashboard, lesson, diagnostic, progress` |
| `app/frontend/.next/server/app/(auth)/login/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic` |
| `app/frontend/.next/server/app/(learner)/badges/page.js` | `Route, path:` | `learner, parent, dashboard, lesson, diagnostic, assessment, progress, consent` |
| `app/frontend/.next/server/app/(learner)/badges/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic` |
| `app/frontend/.next/server/app/(learner)/dashboard/page.js` | `Route, path:` | `learner, parent, dashboard, lesson, diagnostic, assessment, progress, consent` |
| `app/frontend/.next/server/app/(learner)/dashboard/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic` |
| `app/frontend/.next/server/app/(learner)/diagnostic/page.js` | `Route, path:` | `learner, parent, dashboard, lesson, diagnostic, assessment, progress, consent, onboarding` |
| `app/frontend/.next/server/app/(learner)/diagnostic/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic` |
| `app/frontend/.next/server/app/(learner)/lesson/page.js` | `Route, path:` | `learner, parent, dashboard, lesson, diagnostic, assessment, progress, consent` |
| `app/frontend/.next/server/app/(learner)/lesson/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic` |
| `app/frontend/.next/server/app/(learner)/parent/page.js` | `Route, path:, Link` | `learner, parent, dashboard, lesson, diagnostic, assessment, progress, consent` |
| `app/frontend/.next/server/app/(learner)/parent/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic` |
| `app/frontend/.next/server/app/(learner)/plan/page.js` | `Route, path:` | `learner, parent, dashboard, lesson, diagnostic, assessment, progress, consent` |
| `app/frontend/.next/server/app/(learner)/plan/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic` |
| `app/frontend/.next/server/app/(parent)/parent-dashboard/page.js` | `Route, path:, Link` | `learner, parent, dashboard, lesson, diagnostic, progress, consent, onboarding` |
| `app/frontend/.next/server/app/(parent)/parent-dashboard/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic` |
| `app/frontend/.next/server/app/_not-found/page.js` | `Route, path:` | `learner, parent, dashboard, lesson, diagnostic, progress` |
| `app/frontend/.next/server/app/_not-found/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic` |
| `app/frontend/.next/server/app/page.js` | `Route, path:` | `learner, parent, dashboard, lesson, diagnostic, progress` |
| `app/frontend/.next/server/app/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic` |
| `app/frontend/.next/server/app/parent-portal/page.js` | `Route, path:, Link` | `learner, parent, dashboard, lesson, diagnostic, progress, consent, onboarding` |
| `app/frontend/.next/server/app/parent-portal/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic` |
| `app/frontend/.next/server/interception-route-rewrite-manifest.js` | `Route` | `_none_` |
| `app/frontend/.next/server/vendor-chunks/d3-color.js` | `_none_` | `parent` |
| `app/frontend/.next/server/vendor-chunks/d3-path.js` | `path:` | `_none_` |
| `app/frontend/.next/server/vendor-chunks/d3-shape.js` | `path:, Link` | `_none_` |
| `app/frontend/.next/server/vendor-chunks/fast-equals.js` | `_none_` | `parent` |
| `app/frontend/.next/server/vendor-chunks/lodash.js` | `_none_` | `parent, progress` |
| `app/frontend/.next/server/vendor-chunks/next.js` | `Route, Routes, path:, href=, Link, useNavigate` | `parent, dashboard, progress` |
| `app/frontend/.next/server/vendor-chunks/prop-types.js` | `Link` | `_none_` |
| `app/frontend/.next/server/vendor-chunks/react-smooth.js` | `Route` | `_none_` |
| `app/frontend/.next/server/vendor-chunks/react-transition-group.js` | `Route, Routes` | `parent` |
| `app/frontend/.next/server/vendor-chunks/recharts.js` | `Route, path:, Link` | `parent, progress` |
| `app/frontend/.next/server/vendor-chunks/victory-vendor.js` | `Link` | `_none_` |
| `app/frontend/.next/static/chunks/app/(auth)/layout.js` | `Link` | `parent` |
| `app/frontend/.next/static/chunks/app/(auth)/login/page.js` | `Route, Link` | `learner, parent, dashboard, lesson, diagnostic, progress, consent` |
| `app/frontend/.next/static/chunks/app/(learner)/badges/page.js` | `Link` | `learner, parent, dashboard, lesson, diagnostic, progress, consent` |
| `app/frontend/.next/static/chunks/app/(learner)/dashboard/page.js` | `Route, Link` | `learner, parent, dashboard, lesson, diagnostic, assessment, progress, consent` |
| `app/frontend/.next/static/chunks/app/(learner)/diagnostic/page.js` | `Route, Link` | `learner, parent, dashboard, lesson, diagnostic, assessment, progress, consent, onboarding` |
| `app/frontend/.next/static/chunks/app/(learner)/layout.js` | `Route, Link` | `learner, parent, dashboard, lesson, diagnostic, assessment, progress, consent` |
| `app/frontend/.next/static/chunks/app/(learner)/lesson/page.js` | `Route, Link` | `learner, parent, dashboard, lesson, diagnostic, progress, consent` |
| `app/frontend/.next/static/chunks/app/(learner)/parent/page.js` | `Link` | `learner, parent, dashboard, lesson, diagnostic, progress, consent` |
| `app/frontend/.next/static/chunks/app/(learner)/plan/page.js` | `Route, Link` | `learner, parent, dashboard, lesson, diagnostic, assessment, progress, consent` |
| `app/frontend/.next/static/chunks/app/(parent)/parent-dashboard/page.js` | `Route, Routes, path:, Link` | `learner, parent, dashboard, lesson, diagnostic, progress, consent, onboarding` |
| `app/frontend/.next/static/chunks/app/layout.js` | `Link` | `learner, parent, dashboard, lesson, diagnostic, progress, consent` |
| `app/frontend/.next/static/chunks/app/page.js` | `Route, Link` | `learner, parent` |
| `app/frontend/.next/static/chunks/app/parent-portal/page.js` | `Route, Routes, path:, Link` | `learner, parent, dashboard, lesson, diagnostic, progress, consent, onboarding` |
| `app/frontend/.next/static/chunks/app-pages-internals.js` | `Route, Routes, path:, Link` | `parent` |
| `app/frontend/.next/static/chunks/main-app.js` | `Route, Routes, path:, href=, Link, useNavigate` | `parent, dashboard, progress` |
| `app/frontend/.next/static/chunks/polyfills.js` | `href=` | `parent` |
| `app/frontend/.next/static/chunks/webpack.js` | `Link` | `parent, progress` |
| `app/frontend/.next/types/app/(learner)/badges/page.ts` | `_none_` | `learner` |
| `app/frontend/.next/types/app/(learner)/dashboard/page.ts` | `_none_` | `learner, dashboard` |
| `app/frontend/.next/types/app/(learner)/diagnostic/page.ts` | `_none_` | `learner, diagnostic` |
| `app/frontend/.next/types/app/(learner)/layout.ts` | `_none_` | `learner` |
| `app/frontend/.next/types/app/(learner)/lesson/page.ts` | `_none_` | `learner, lesson` |
| `app/frontend/.next/types/app/(learner)/parent/page.ts` | `_none_` | `learner, parent` |
| `app/frontend/.next/types/app/(learner)/plan/page.ts` | `_none_` | `learner` |
| `app/frontend/.next/types/app/(parent)/parent-dashboard/page.ts` | `_none_` | `parent, dashboard` |
| `app/frontend/.next/types/app/parent-portal/page.ts` | `_none_` | `parent` |
| `app/frontend/__tests__/EntryAndPortal.test.tsx` | `_none_` | `learner, parent, dashboard, lesson, progress, onboarding` |
| `app/frontend/__tests__/FeaturePanels.test.tsx` | `_none_` | `learner, dashboard, lesson, diagnostic` |
| `app/frontend/__tests__/InteractiveDiagnosticFlow.test.tsx` | `_none_` | `learner, diagnostic, assessment` |
| `app/frontend/__tests__/LegacyApiHelpers.test.ts` | `_none_` | `learner, diagnostic` |
| `app/frontend/__tests__/RoutingIntegration.test.tsx` | `Route, Routes` | `learner, dashboard, lesson, diagnostic` |
| `app/frontend/__tests__/setup.ts` | `_none_` | `diagnostic, progress` |
| `app/frontend/coverage/prettify.js` | `_none_` | `parent` |
| `app/frontend/coverage/sorter.js` | `_none_` | `parent` |
| `app/frontend/public/service-worker.js` | `_none_` | `parent, dashboard, lesson, diagnostic` |
| `app/frontend/src/__tests__/AccessibilityContracts.test.tsx` | `Route, Link` | `learner, parent, dashboard, diagnostic, progress, consent` |
| `app/frontend/src/__tests__/ApiLayer.test.ts` | `_none_` | `learner, parent, dashboard, lesson, diagnostic` |
| `app/frontend/src/__tests__/DiagnosticContract.test.ts` | `_none_` | `learner, diagnostic` |
| `app/frontend/src/__tests__/LearnerJourneys.test.ts` | `_none_` | `learner, dashboard, lesson, progress` |
| `app/frontend/src/__tests__/OfflineSync.test.ts` | `_none_` | `learner, lesson` |
| `app/frontend/src/app/(auth)/login/page.tsx` | `Route` | `learner, parent, dashboard, consent` |
| `app/frontend/src/app/(auth)/register/page.tsx` | `Route` | `learner, parent, dashboard, lesson, diagnostic, progress, consent` |
| `app/frontend/src/app/(learner)/badges/page.tsx` | `_none_` | `learner, lesson, diagnostic, progress` |
| `app/frontend/src/app/(learner)/dashboard/page.tsx` | `Route` | `learner, parent, dashboard, lesson, diagnostic, assessment, progress` |
| `app/frontend/src/app/(learner)/diagnostic/page.tsx` | `Route` | `learner, dashboard, diagnostic` |
| `app/frontend/src/app/(learner)/layout.tsx` | `Route` | `learner, dashboard` |
| `app/frontend/src/app/(learner)/lesson/page.tsx` | `Route` | `learner, dashboard, lesson` |
| `app/frontend/src/app/(learner)/parent/page.tsx` | `Link` | `learner, parent, progress` |
| `app/frontend/src/app/(learner)/plan/page.tsx` | `Route` | `learner, lesson, diagnostic, assessment, progress` |
| `app/frontend/src/app/(parent)/parent-dashboard/page.tsx` | `Route` | `parent, dashboard` |
| `app/frontend/src/app/layout.tsx` | `Link` | `learner` |
| `app/frontend/src/app/page.tsx` | `Route` | `learner, parent` |
| `app/frontend/src/app/parent-portal/page.tsx` | `Route` | `parent, dashboard` |
| `app/frontend/src/components/ServiceWorkerRegistration.tsx` | `_none_` | `lesson` |
| `app/frontend/src/components/accessibility/A11y.tsx` | `href=, Link` | `_none_` |
| `app/frontend/src/components/eduboost/BetaAndFeedback.tsx` | `href=` | `_none_` |
| `app/frontend/src/components/eduboost/EntryScreens.tsx` | `_none_` | `learner, parent, consent, onboarding` |
| `app/frontend/src/components/eduboost/ErrorBoundary.tsx` | `Route` | `dashboard` |
| `app/frontend/src/components/eduboost/FeaturePanels.tsx` | `_none_` | `learner, dashboard, lesson, diagnostic` |
| `app/frontend/src/components/eduboost/InteractiveDiagnostic.tsx` | `_none_` | `learner, dashboard, diagnostic, assessment, progress` |
| `app/frontend/src/components/eduboost/InteractiveLesson.tsx` | `_none_` | `learner, lesson` |
| `app/frontend/src/components/eduboost/ParentDashboard.tsx` | `href=, Link` | `learner, parent, dashboard, lesson, progress` |
| `app/frontend/src/components/eduboost/RouteGuard.tsx` | `Route` | `learner, parent, dashboard` |
| `app/frontend/src/components/eduboost/ShellComponents.tsx` | `_none_` | `learner, parent, dashboard, lesson, diagnostic, assessment, progress, consent` |
| `app/frontend/src/components/eduboost/api.ts` | `_none_` | `learner, diagnostic` |
| `app/frontend/src/components/eduboost/constants.ts` | `_none_` | `lesson` |
| `app/frontend/src/components/eduboost/styles.ts` | `_none_` | `parent, consent, onboarding` |
| `app/frontend/src/context/LearnerContext.tsx` | `_none_` | `learner` |
| `app/frontend/src/lib/api/client.ts` | `_none_` | `learner, parent, consent` |
| `app/frontend/src/lib/api/offlineSync.ts` | `_none_` | `learner, lesson` |
| `app/frontend/src/lib/api/services.ts` | `_none_` | `learner, parent, dashboard, lesson, diagnostic, progress, consent` |
| `app/frontend/src/lib/api/types.ts` | `_none_` | `learner, parent, dashboard, lesson, diagnostic, progress, consent` |

## Command

```bash
make frontend-route-inventory
```
