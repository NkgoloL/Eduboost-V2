---
title: "Frontend Route Inventory"
status: "current-evidence"
owner: "frontend"
reviewers: ["frontend", "product", "privacy"]
audience: "developer"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-06-24"
review_interval_days: 60
evidence_command: "make docs-housekeeping-stage5-check"
code_anchors: "[app/frontend, docs/frontend/README.md]"
---

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
| `app/frontend/.eslintrc.js` | `_none_` | `learner, consent` |
| `app/frontend/__tests__/BetaAndFeedback.test.tsx` | `Link` | `_none_` |
| `app/frontend/__tests__/EntryAndPortal.test.tsx` | `_none_` | `learner, parent, dashboard, lesson, progress, onboarding` |
| `app/frontend/__tests__/EntryScreens.test.tsx` | `_none_` | `learner, parent, onboarding` |
| `app/frontend/__tests__/FeaturePanels.test.tsx` | `_none_` | `learner, dashboard, lesson, diagnostic` |
| `app/frontend/__tests__/InteractiveDiagnostic.test.tsx` | `_none_` | `learner, diagnostic, assessment` |
| `app/frontend/__tests__/InteractiveDiagnosticFlow.test.tsx` | `_none_` | `learner, diagnostic, assessment` |
| `app/frontend/__tests__/LegacyApiHelpers.test.ts` | `_none_` | `learner, diagnostic` |
| `app/frontend/__tests__/ParentDashboard.test.tsx` | `_none_` | `learner, parent, dashboard, lesson, progress, consent` |
| `app/frontend/__tests__/RouteGuard.test.tsx` | `Route, Routes` | `learner, parent` |
| `app/frontend/__tests__/RoutingIntegration.test.tsx` | `Route, Routes` | `learner, dashboard, lesson, diagnostic, assessment` |
| `app/frontend/__tests__/client.api.test.ts` | `Route, Routes` | `lesson, diagnostic, progress` |
| `app/frontend/__tests__/offlineSync.test.ts` | `_none_` | `learner, lesson` |
| `app/frontend/__tests__/services.coverage.test.ts` | `_none_` | `learner, parent, dashboard, lesson, diagnostic, consent` |
| `app/frontend/__tests__/services.smoke.test.ts` | `Route` | `learner, lesson, diagnostic, consent` |
| `app/frontend/__tests__/setup.ts` | `_none_` | `diagnostic, progress` |
| `app/frontend/middleware.ts` | `_none_` | `parent, dashboard, onboarding` |
| `app/frontend/next-env.d.ts` | `Route, Routes` | `_none_` |
| `app/frontend/public/service-worker.js` | `_none_` | `parent, dashboard, lesson, diagnostic` |
| `app/frontend/public/sw.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, onboarding` |
| `app/frontend/src/__tests__/AccessibilityContracts.test.tsx` | `Route, Link` | `learner, parent, dashboard, diagnostic, progress, consent` |
| `app/frontend/src/__tests__/ApiLayer.test.ts` | `Route, Routes` | `learner, parent, dashboard, lesson, diagnostic` |
| `app/frontend/src/__tests__/ContentFactoryMode.test.ts` | `_none_` | `dashboard` |
| `app/frontend/src/__tests__/DiagnosticContract.test.ts` | `_none_` | `learner, diagnostic` |
| `app/frontend/src/__tests__/LearnerJourneys.test.ts` | `_none_` | `learner, dashboard, lesson, progress` |
| `app/frontend/src/__tests__/OfflineSync.test.ts` | `_none_` | `learner, lesson` |
| `app/frontend/src/__tests__/authRoutes.test.ts` | `Route, Routes, path:` | `dashboard, diagnostic` |
| `app/frontend/src/__tests__/db/cache-api.test.ts` | `_none_` | `learner, lesson, progress` |
| `app/frontend/src/__tests__/guardian/whatsapp-share-shell.test.tsx` | `_none_` | `learner` |
| `app/frontend/src/__tests__/tutor/parent-review-access.test.ts` | `_none_` | `parent` |
| `app/frontend/src/__tests__/tutor/parent-review-api.test.ts` | `Route` | `learner, lesson` |
| `app/frontend/src/__tests__/tutor/parent-review-contracts.test.ts` | `_none_` | `learner, parent, lesson` |
| `app/frontend/src/__tests__/tutor/parent-review-redaction.test.ts` | `_none_` | `learner, parent, lesson` |
| `app/frontend/src/__tests__/tutor/parent-review-retention.test.ts` | `_none_` | `parent` |
| `app/frontend/src/__tests__/tutor/tutor-contracts.test.ts` | `Route` | `lesson` |
| `app/frontend/src/__tests__/tutor/tutor-review-integration.test.ts` | `_none_` | `learner, parent, lesson` |
| `app/frontend/src/__tests__/tutor/tutor-route.test.ts` | `Route` | `lesson` |
| `app/frontend/src/__tests__/tutor/tutor-safety.test.ts` | `_none_` | `learner, lesson` |
| `app/frontend/src/__tests__/voice/voice-consent.test.ts` | `_none_` | `learner, consent` |
| `app/frontend/src/__tests__/voice/voice-guardrails.test.ts` | `_none_` | `consent` |
| `app/frontend/src/__tests__/voice/voice-input-shell.test.tsx` | `_none_` | `learner, consent` |
| `app/frontend/src/app/(auth)/login/page.tsx` | `Route, href=, Link` | `learner, parent, dashboard, lesson, progress` |
| `app/frontend/src/app/(auth)/register/page.tsx` | `Route` | `learner, parent, dashboard, lesson, diagnostic, progress, consent` |
| `app/frontend/src/app/(dashboard)/admin/roadmap/page.tsx` | `Route` | `dashboard, lesson` |
| `app/frontend/src/app/(learner)/badges/page.tsx` | `_none_` | `learner, lesson, diagnostic, progress` |
| `app/frontend/src/app/(learner)/dashboard/page.tsx` | `_none_` | `learner, dashboard` |
| `app/frontend/src/app/(learner)/diagnostic/page.tsx` | `_none_` | `learner, diagnostic` |
| `app/frontend/src/app/(learner)/layout.tsx` | `Route` | `learner, dashboard` |
| `app/frontend/src/app/(learner)/lesson/page.tsx` | `_none_` | `learner, lesson` |
| `app/frontend/src/app/(learner)/parent/page.tsx` | `Link` | `learner, parent, progress` |
| `app/frontend/src/app/(learner)/plan/page.tsx` | `Route` | `learner, lesson, diagnostic, assessment, progress` |
| `app/frontend/src/app/(parent)/parent-dashboard/page.tsx` | `Route` | `parent, dashboard` |
| `app/frontend/src/app/admin/content-factory/page.tsx` | `_none_` | `dashboard` |
| `app/frontend/src/app/api/backend/[...path]/route.ts` | `Route, path:` | `_none_` |
| `app/frontend/src/app/api/tutor/review/route.ts` | `_none_` | `learner, parent` |
| `app/frontend/src/app/api/tutor/route.ts` | `_none_` | `lesson` |
| `app/frontend/src/app/auth/reset-password/page.tsx` | `Route, Routes, href=, Link` | `learner, parent` |
| `app/frontend/src/app/auth/verify-email/page.tsx` | `Route, Routes, href=, Link` | `onboarding` |
| `app/frontend/src/app/layout.tsx` | `Link` | `learner` |
| `app/frontend/src/app/onboarding/page.tsx` | `Route, Link` | `learner, parent, dashboard, lesson, diagnostic, assessment, progress, consent, onboarding` |
| `app/frontend/src/app/page.tsx` | `Route` | `learner, parent` |
| `app/frontend/src/app/parent-portal/page.tsx` | `Route` | `parent, dashboard` |
| `app/frontend/src/app/settings/privacy/page.tsx` | `_none_` | `learner, parent, lesson` |
| `app/frontend/src/app/sw.ts` | `Route, Routes` | `parent, dashboard, lesson, diagnostic, onboarding` |
| `app/frontend/src/components/ServiceWorkerRegistration.tsx` | `_none_` | `lesson` |
| `app/frontend/src/components/accessibility/A11y.tsx` | `href=, Link` | `_none_` |
| `app/frontend/src/components/admin/ETLAdminDashboard.tsx` | `path:` | `parent, lesson, assessment` |
| `app/frontend/src/components/admin/contentFactory/ContentFactoryLiveDashboard.tsx` | `_none_` | `dashboard` |
| `app/frontend/src/components/admin/contentFactory/StagingProductionPreviewPanel.tsx` | `_none_` | `learner, lesson, diagnostic` |
| `app/frontend/src/components/admin/contentFactory/StagingReadinessPanel.tsx` | `href=` | `_none_` |
| `app/frontend/src/components/dashboard/course-card.tsx` | `href=, Link` | `parent, dashboard, lesson, progress` |
| `app/frontend/src/components/dashboard/metric-card.tsx` | `_none_` | `parent` |
| `app/frontend/src/components/eduboost/BetaAndFeedback.tsx` | `href=` | `_none_` |
| `app/frontend/src/components/eduboost/EntryScreens.tsx` | `_none_` | `learner, parent, consent, onboarding` |
| `app/frontend/src/components/eduboost/ErrorBoundary.tsx` | `Route` | `dashboard` |
| `app/frontend/src/components/eduboost/FeaturePanels.tsx` | `_none_` | `learner, dashboard, lesson, diagnostic` |
| `app/frontend/src/components/eduboost/InfoOfficerNotice.tsx` | `href=` | `consent` |
| `app/frontend/src/components/eduboost/InteractiveDiagnostic.tsx` | `_none_` | `learner, dashboard, diagnostic, assessment, progress` |
| `app/frontend/src/components/eduboost/InteractiveLesson.tsx` | `_none_` | `learner, lesson` |
| `app/frontend/src/components/eduboost/LessonRoadmap.tsx` | `Route` | `learner, dashboard, lesson, diagnostic, progress` |
| `app/frontend/src/components/eduboost/ParentDashboard.tsx` | `href=, Link` | `learner, parent, dashboard, lesson, progress, consent` |
| `app/frontend/src/components/eduboost/RouteGuard.tsx` | `Route` | `learner, parent, dashboard` |
| `app/frontend/src/components/eduboost/ShellComponents.tsx` | `_none_` | `learner, parent, dashboard, lesson, diagnostic, assessment, progress, consent` |
| `app/frontend/src/components/eduboost/api.ts` | `_none_` | `learner, diagnostic` |
| `app/frontend/src/components/eduboost/constants.ts` | `_none_` | `lesson` |
| `app/frontend/src/components/eduboost/styles.ts` | `_none_` | `parent, consent, onboarding` |
| `app/frontend/src/components/forms/ValidationMessage.tsx` | `href=, Link` | `_none_` |
| `app/frontend/src/components/grade-r/PhonicsKaraokeText.tsx` | `_none_` | `parent` |
| `app/frontend/src/components/guardian/WhatsAppShareShell.tsx` | `Link` | `learner` |
| `app/frontend/src/components/layout/dashboard-sidebar.tsx` | `href=, Link` | `parent, dashboard, assessment, progress` |
| `app/frontend/src/components/layout/dashboard-topbar.tsx` | `href=, Link` | `parent, dashboard, lesson` |
| `app/frontend/src/components/layout/marketing-footer.tsx` | `href=, Link` | `learner, parent` |
| `app/frontend/src/components/layout/marketing-header.tsx` | `href=, Link` | `parent` |
| `app/frontend/src/components/learner/AiTutorChat.tsx` | `_none_` | `learner, lesson` |
| `app/frontend/src/components/learner/DashboardClient.tsx` | `Route` | `learner, parent, dashboard, lesson, diagnostic, assessment, progress` |
| `app/frontend/src/components/learner/DashboardSkeleton.tsx` | `_none_` | `dashboard` |
| `app/frontend/src/components/learner/DiagnosticEntryClient.tsx` | `Route` | `learner, dashboard, diagnostic` |
| `app/frontend/src/components/learner/DiagnosticSkeleton.tsx` | `_none_` | `diagnostic` |
| `app/frontend/src/components/learner/LessonEntryClient.tsx` | `Route` | `learner, dashboard, lesson` |
| `app/frontend/src/components/learner/LessonSkeleton.tsx` | `_none_` | `lesson` |
| `app/frontend/src/components/learner/__tests__/AiTutorChat.test.tsx` | `_none_` | `learner, lesson` |
| `app/frontend/src/components/lessons/LessonTrustLabel.tsx` | `Link` | `parent, lesson` |
| `app/frontend/src/components/ui/badge.tsx` | `_none_` | `parent` |
| `app/frontend/src/components/ui/breadcrumb.tsx` | `Link` | `_none_` |
| `app/frontend/src/components/ui/button.tsx` | `Link` | `_none_` |
| `app/frontend/src/components/ui/input.tsx` | `_none_` | `parent` |
| `app/frontend/src/components/ui-shadcn/badge.tsx` | `_none_` | `parent` |
| `app/frontend/src/components/ui-shadcn/breadcrumb.tsx` | `Link` | `_none_` |
| `app/frontend/src/components/ui-shadcn/button.tsx` | `Link` | `_none_` |
| `app/frontend/src/components/ui-shadcn/input.tsx` | `_none_` | `parent` |
| `app/frontend/src/components/voice/VoiceInputShell.tsx` | `_none_` | `learner, consent` |
| `app/frontend/src/context/LearnerContext.tsx` | `_none_` | `learner` |
| `app/frontend/src/lib/admin/contentFactoryMode.ts` | `_none_` | `dashboard` |
| `app/frontend/src/lib/api/contentFactory.ts` | `_none_` | `learner, lesson, diagnostic` |
| `app/frontend/src/lib/api/offlineSync.ts` | `_none_` | `learner, lesson` |
| `app/frontend/src/lib/api/services.ts` | `_none_` | `learner, parent, dashboard, lesson, diagnostic, progress, consent` |
| `app/frontend/src/lib/api/types.ts` | `_none_` | `learner, parent, dashboard, lesson, diagnostic, progress, consent` |
| `app/frontend/src/lib/auth/cookies.ts` | `path:` | `_none_` |
| `app/frontend/src/lib/db/cache-api.ts` | `_none_` | `learner, lesson, progress, consent` |
| `app/frontend/src/lib/db/schema.ts` | `_none_` | `learner, lesson` |
| `app/frontend/src/lib/db/storage-budget.ts` | `_none_` | `lesson` |
| `app/frontend/src/lib/learner/lesson-completion-boundary.ts` | `_none_` | `learner, lesson` |
| `app/frontend/src/lib/learner/server-loaders.ts` | `_none_` | `learner, dashboard, lesson, diagnostic` |
| `app/frontend/src/lib/productionReadiness/contracts.ts` | `Route` | `learner, parent, dashboard, lesson, diagnostic, consent, onboarding` |
| `app/frontend/src/lib/share/types.ts` | `_none_` | `learner` |
| `app/frontend/src/lib/share/whatsapp.ts` | `Link` | `_none_` |
| `app/frontend/src/lib/tutor/audit.ts` | `_none_` | `lesson` |
| `app/frontend/src/lib/tutor/client.ts` | `_none_` | `lesson` |
| `app/frontend/src/lib/tutor/parent-review/dto.ts` | `_none_` | `learner, parent, lesson` |
| `app/frontend/src/lib/tutor/parent-review/redaction.ts` | `_none_` | `learner, parent, lesson` |
| `app/frontend/src/lib/tutor/parent-review/repository.ts` | `_none_` | `learner, parent` |
| `app/frontend/src/lib/tutor/parent-review/retention.ts` | `_none_` | `parent` |
| `app/frontend/src/lib/tutor/parent-review/service.ts` | `_none_` | `learner, parent` |
| `app/frontend/src/lib/tutor/parent-review/types.ts` | `_none_` | `learner, parent, lesson` |
| `app/frontend/src/lib/tutor/rate-limit.ts` | `_none_` | `lesson` |
| `app/frontend/src/lib/tutor/safety.ts` | `_none_` | `learner, lesson` |
| `app/frontend/src/lib/tutor/types.ts` | `_none_` | `lesson` |
| `app/frontend/src/lib/utils.ts` | `_none_` | `progress` |
| `app/frontend/src/lib/voice/consent.ts` | `_none_` | `learner, consent` |
| `app/frontend/src/lib/voice/guardrails.ts` | `_none_` | `consent` |
| `app/frontend/src/lib/voice/types.ts` | `_none_` | `learner, consent` |
| `app/frontend/src/types/index.ts` | `_none_` | `parent, dashboard, lesson, assessment, progress` |

## Command

```bash
make frontend-route-inventory
```
