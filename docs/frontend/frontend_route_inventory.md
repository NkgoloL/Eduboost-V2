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
| `app/frontend/.next/server/app/(auth)/login/page.js` | `Route, path:` | `learner, parent, dashboard, consent` |
| `app/frontend/.next/server/app/(auth)/login/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic` |
| `app/frontend/.next/server/app/(auth)/register/page.js` | `Route, path:` | `learner, parent, dashboard, lesson, diagnostic, progress, consent` |
| `app/frontend/.next/server/app/(auth)/register/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic` |
| `app/frontend/.next/server/app/(learner)/badges/page.js` | `Route, path:` | `learner, lesson, diagnostic, progress` |
| `app/frontend/.next/server/app/(learner)/badges/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic` |
| `app/frontend/.next/server/app/(learner)/dashboard/page.js` | `Route, path:` | `learner, parent, dashboard, lesson, diagnostic, assessment, progress` |
| `app/frontend/.next/server/app/(learner)/dashboard/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic` |
| `app/frontend/.next/server/app/(learner)/diagnostic/page.js` | `Route, path:` | `learner, dashboard, diagnostic, assessment, progress` |
| `app/frontend/.next/server/app/(learner)/diagnostic/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic` |
| `app/frontend/.next/server/app/(learner)/lesson/page.js` | `Route, path:` | `learner, dashboard, lesson` |
| `app/frontend/.next/server/app/(learner)/lesson/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic` |
| `app/frontend/.next/server/app/(learner)/parent/page.js` | `Route, path:, Link` | `learner, parent, progress` |
| `app/frontend/.next/server/app/(learner)/parent/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic` |
| `app/frontend/.next/server/app/(learner)/plan/page.js` | `Route, path:` | `learner, lesson, diagnostic, assessment, progress` |
| `app/frontend/.next/server/app/(learner)/plan/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic` |
| `app/frontend/.next/server/app/(parent)/parent-dashboard/page.js` | `Route, path:` | `learner, parent, dashboard` |
| `app/frontend/.next/server/app/(parent)/parent-dashboard/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic` |
| `app/frontend/.next/server/app/_not-found/page.js` | `Route, path:` | `_none_` |
| `app/frontend/.next/server/app/_not-found/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic` |
| `app/frontend/.next/server/app/page.js` | `Route, path:` | `learner, parent` |
| `app/frontend/.next/server/app/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic` |
| `app/frontend/.next/server/app/parent-portal/page.js` | `Route, path:` | `parent` |
| `app/frontend/.next/server/app/parent-portal/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic` |
| `app/frontend/.next/server/chunks/382.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, assessment` |
| `app/frontend/.next/server/chunks/682.js` | `Route, Routes, path:, Link` | `_none_` |
| `app/frontend/.next/server/chunks/732.js` | `Route, Routes, path:, Link` | `parent` |
| `app/frontend/.next/server/chunks/879.js` | `Route, Link` | `learner, dashboard, lesson, diagnostic, progress, consent` |
| `app/frontend/.next/server/chunks/983.js` | `Link` | `learner, parent, dashboard, lesson, progress` |
| `app/frontend/.next/server/chunks/991.js` | `Route, path:, Link` | `parent, progress` |
| `app/frontend/.next/server/interception-route-rewrite-manifest.js` | `Route` | `_none_` |
| `app/frontend/.next/server/pages/_error.js` | `Route, path:, href=, Link` | `_none_` |
| `app/frontend/.next/standalone/.next/server/app/(auth)/login/page.js` | `Route, path:` | `learner, parent, dashboard, consent` |
| `app/frontend/.next/standalone/.next/server/app/(auth)/login/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic` |
| `app/frontend/.next/standalone/.next/server/app/(auth)/register/page.js` | `Route, path:` | `learner, parent, dashboard, lesson, diagnostic, progress, consent` |
| `app/frontend/.next/standalone/.next/server/app/(auth)/register/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic` |
| `app/frontend/.next/standalone/.next/server/app/(learner)/badges/page.js` | `Route, path:` | `learner, lesson, diagnostic, progress` |
| `app/frontend/.next/standalone/.next/server/app/(learner)/badges/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic` |
| `app/frontend/.next/standalone/.next/server/app/(learner)/dashboard/page.js` | `Route, path:` | `learner, parent, dashboard, lesson, diagnostic, assessment, progress` |
| `app/frontend/.next/standalone/.next/server/app/(learner)/dashboard/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic` |
| `app/frontend/.next/standalone/.next/server/app/(learner)/diagnostic/page.js` | `Route, path:` | `learner, dashboard, diagnostic, assessment, progress` |
| `app/frontend/.next/standalone/.next/server/app/(learner)/diagnostic/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic` |
| `app/frontend/.next/standalone/.next/server/app/(learner)/lesson/page.js` | `Route, path:` | `learner, dashboard, lesson` |
| `app/frontend/.next/standalone/.next/server/app/(learner)/lesson/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic` |
| `app/frontend/.next/standalone/.next/server/app/(learner)/parent/page.js` | `Route, path:, Link` | `learner, parent, progress` |
| `app/frontend/.next/standalone/.next/server/app/(learner)/parent/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic` |
| `app/frontend/.next/standalone/.next/server/app/(learner)/plan/page.js` | `Route, path:` | `learner, lesson, diagnostic, assessment, progress` |
| `app/frontend/.next/standalone/.next/server/app/(learner)/plan/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic` |
| `app/frontend/.next/standalone/.next/server/app/(parent)/parent-dashboard/page.js` | `Route, path:` | `learner, parent, dashboard` |
| `app/frontend/.next/standalone/.next/server/app/(parent)/parent-dashboard/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic` |
| `app/frontend/.next/standalone/.next/server/app/_not-found/page.js` | `Route, path:` | `_none_` |
| `app/frontend/.next/standalone/.next/server/app/_not-found/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic` |
| `app/frontend/.next/standalone/.next/server/app/page.js` | `Route, path:` | `learner, parent` |
| `app/frontend/.next/standalone/.next/server/app/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic` |
| `app/frontend/.next/standalone/.next/server/app/parent-portal/page.js` | `Route, path:` | `parent` |
| `app/frontend/.next/standalone/.next/server/app/parent-portal/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic` |
| `app/frontend/.next/standalone/.next/server/chunks/382.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, assessment` |
| `app/frontend/.next/standalone/.next/server/chunks/682.js` | `Route, Routes, path:, Link` | `_none_` |
| `app/frontend/.next/standalone/.next/server/chunks/732.js` | `Route, Routes, path:, Link` | `parent` |
| `app/frontend/.next/standalone/.next/server/chunks/879.js` | `Route, Link` | `learner, dashboard, lesson, diagnostic, progress, consent` |
| `app/frontend/.next/standalone/.next/server/chunks/983.js` | `Link` | `learner, parent, dashboard, lesson, progress` |
| `app/frontend/.next/standalone/.next/server/chunks/991.js` | `Route, path:, Link` | `parent, progress` |
| `app/frontend/.next/standalone/.next/server/pages/_error.js` | `Route, path:, href=, Link` | `_none_` |
| `app/frontend/.next/standalone/server.js` | `Route, Routes, Link` | `_none_` |
| `app/frontend/.next/static/chunks/117-68e90f423b45e887.js` | `Route, Routes, path:, Link` | `_none_` |
| `app/frontend/.next/static/chunks/154-dc61fd38fd74f10e.js` | `_none_` | `learner, parent, dashboard, lesson, diagnostic, progress, consent` |
| `app/frontend/.next/static/chunks/720-32b9d797f1cddfb8.js` | `Route, path:, Link` | `parent, progress` |
| `app/frontend/.next/static/chunks/871-e7378926093d3547.js` | `Link` | `learner, parent, dashboard, lesson, progress` |
| `app/frontend/.next/static/chunks/app/(auth)/login/page-89a3e73e768d7b17.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, progress, consent` |
| `app/frontend/.next/static/chunks/app/(auth)/register/page-235678661208e097.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, progress, consent` |
| `app/frontend/.next/static/chunks/app/(learner)/badges/page-91ddd1f371a7b2e5.js` | `_none_` | `learner, parent, dashboard, lesson, diagnostic, progress, consent` |
| `app/frontend/.next/static/chunks/app/(learner)/dashboard/page-508ec197be95f974.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, assessment, progress` |
| `app/frontend/.next/static/chunks/app/(learner)/diagnostic/page-e425efeb68c58ffd.js` | `Route` | `learner, dashboard, diagnostic, assessment, progress` |
| `app/frontend/.next/static/chunks/app/(learner)/layout-49ae049e7b571662.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, assessment` |
| `app/frontend/.next/static/chunks/app/(learner)/lesson/page-9645cd8eceefcce9.js` | `Route` | `learner, dashboard, lesson` |
| `app/frontend/.next/static/chunks/app/(learner)/parent/page-3088f2d29dc26d18.js` | `Link` | `learner, parent, dashboard, lesson, diagnostic, progress, consent` |
| `app/frontend/.next/static/chunks/app/(learner)/plan/page-805473f8887e01bd.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, assessment, progress, consent` |
| `app/frontend/.next/static/chunks/app/(parent)/parent-dashboard/page-d4d7a3b032f3fd59.js` | `Route` | `learner, parent, dashboard` |
| `app/frontend/.next/static/chunks/app/layout-54d7d6d6657a648f.js` | `Route, Link` | `learner, parent, dashboard, lesson, diagnostic, progress, consent` |
| `app/frontend/.next/static/chunks/app/page-14b09c6e7d01d225.js` | `Route` | `learner, parent` |
| `app/frontend/.next/static/chunks/app/parent-portal/page-1891ac730088cc93.js` | `Route` | `_none_` |
| `app/frontend/.next/static/chunks/fd9d1056-ebff176a35585c2c.js` | `path:, href=, Link` | `parent, progress` |
| `app/frontend/.next/static/chunks/framework-00a8ba1a63cfdc9e.js` | `path:, href=, Link` | `parent, progress` |
| `app/frontend/.next/static/chunks/main-70a628e45d5f87dd.js` | `Route, Routes, path:, href=, Link` | `parent, progress` |
| `app/frontend/.next/static/chunks/polyfills-42372ed130431b0a.js` | `path:, href=` | `parent` |
| `app/frontend/.next/static/chunks/webpack-e08da262b32814b6.js` | `_none_` | `parent` |
| `app/frontend/.next/types/app/(learner)/badges/page.ts` | `_none_` | `learner` |
| `app/frontend/.next/types/app/(learner)/dashboard/page.ts` | `_none_` | `learner, dashboard` |
| `app/frontend/.next/types/app/(learner)/diagnostic/page.ts` | `_none_` | `learner, diagnostic` |
| `app/frontend/.next/types/app/(learner)/lesson/page.ts` | `_none_` | `learner, lesson` |
| `app/frontend/.next/types/app/(learner)/parent/page.ts` | `_none_` | `learner, parent` |
| `app/frontend/.next/types/app/(learner)/plan/page.ts` | `_none_` | `learner` |
| `app/frontend/.next/types/app/(parent)/parent-dashboard/page.ts` | `_none_` | `parent, dashboard` |
| `app/frontend/.next/types/app/parent-portal/page.ts` | `_none_` | `parent` |
| `app/frontend/__tests__/BetaAndFeedback.test.tsx` | `Link` | `_none_` |
| `app/frontend/__tests__/EntryAndPortal.test.tsx` | `_none_` | `learner, parent, dashboard, lesson, progress, onboarding` |
| `app/frontend/__tests__/EntryScreens.test.tsx` | `_none_` | `learner, parent, onboarding` |
| `app/frontend/__tests__/FeaturePanels.test.tsx` | `_none_` | `learner, dashboard, lesson, diagnostic` |
| `app/frontend/__tests__/InteractiveDiagnostic.test.tsx` | `_none_` | `learner, diagnostic, assessment` |
| `app/frontend/__tests__/InteractiveDiagnosticFlow.test.tsx` | `_none_` | `learner, diagnostic, assessment` |
| `app/frontend/__tests__/LegacyApiHelpers.test.ts` | `_none_` | `learner, diagnostic` |
| `app/frontend/__tests__/ParentDashboard.test.tsx` | `_none_` | `learner, parent, dashboard, lesson, progress` |
| `app/frontend/__tests__/RouteGuard.test.tsx` | `Route` | `learner, parent` |
| `app/frontend/__tests__/RoutingIntegration.test.tsx` | `Route, Routes` | `learner, dashboard, lesson, diagnostic, assessment` |
| `app/frontend/__tests__/client.api.test.ts` | `_none_` | `learner, lesson` |
| `app/frontend/__tests__/offlineSync.test.ts` | `_none_` | `learner, lesson` |
| `app/frontend/__tests__/services.coverage.test.ts` | `_none_` | `learner, parent, dashboard, lesson, diagnostic, consent` |
| `app/frontend/__tests__/services.smoke.test.ts` | `_none_` | `learner, lesson, diagnostic, consent` |
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
| `app/frontend/src/components/lessons/LessonTrustLabel.tsx` | `Link` | `parent, lesson` |
| `app/frontend/src/context/LearnerContext.tsx` | `_none_` | `learner` |
| `app/frontend/src/lib/api/client.ts` | `_none_` | `learner, parent, consent` |
| `app/frontend/src/lib/api/offlineSync.ts` | `_none_` | `learner, lesson` |
| `app/frontend/src/lib/api/services.ts` | `_none_` | `learner, parent, dashboard, lesson, diagnostic, progress, consent` |
| `app/frontend/src/lib/api/types.ts` | `_none_` | `learner, parent, dashboard, lesson, diagnostic, progress, consent` |
| `app/frontend/src/lib/productionReadiness/contracts.ts` | `Route` | `learner, parent, dashboard, lesson, diagnostic, consent, onboarding` |

## Command

```bash
make frontend-route-inventory
```
