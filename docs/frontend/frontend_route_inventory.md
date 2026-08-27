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
| `app/frontend/.next/required-server-files.js` | `Route, Routes, Link` | `_none_` |
| `app/frontend/.next/server/app/(auth)/login/page.js` | `Route, Routes, path:, Link` | `learner, parent, dashboard, lesson, progress` |
| `app/frontend/.next/server/app/(auth)/login/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, onboarding` |
| `app/frontend/.next/server/app/(auth)/register/page.js` | `Route, Routes, path:` | `learner, parent, dashboard, lesson, diagnostic, progress, consent` |
| `app/frontend/.next/server/app/(auth)/register/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, onboarding` |
| `app/frontend/.next/server/app/(dashboard)/admin/roadmap/page.js` | `Route, Routes, path:` | `learner, dashboard, lesson, diagnostic, progress` |
| `app/frontend/.next/server/app/(dashboard)/admin/roadmap/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, onboarding` |
| `app/frontend/.next/server/app/(learner)/badges/page.js` | `Route, Routes, path:` | `learner, parent, lesson, diagnostic, progress` |
| `app/frontend/.next/server/app/(learner)/badges/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, onboarding` |
| `app/frontend/.next/server/app/(learner)/dashboard/page.js` | `Route, Routes, path:` | `learner, parent, dashboard, lesson, diagnostic, assessment, progress` |
| `app/frontend/.next/server/app/(learner)/dashboard/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, onboarding` |
| `app/frontend/.next/server/app/(learner)/diagnostic/page.js` | `Route, Routes, path:` | `learner, dashboard, lesson, diagnostic, assessment, progress` |
| `app/frontend/.next/server/app/(learner)/diagnostic/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, onboarding` |
| `app/frontend/.next/server/app/(learner)/lesson/page.js` | `Route, Routes, path:` | `learner, lesson` |
| `app/frontend/.next/server/app/(learner)/lesson/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, onboarding` |
| `app/frontend/.next/server/app/(learner)/parent/page.js` | `Route, Routes, path:` | `learner, parent, dashboard, lesson, diagnostic, assessment, progress, consent` |
| `app/frontend/.next/server/app/(learner)/parent/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, onboarding` |
| `app/frontend/.next/server/app/(learner)/plan/page.js` | `Route, Routes, path:` | `learner, lesson, diagnostic, assessment, progress` |
| `app/frontend/.next/server/app/(learner)/plan/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, onboarding` |
| `app/frontend/.next/server/app/(parent)/parent-dashboard/page.js` | `Route, Routes, path:, Link` | `learner, parent, dashboard, lesson, progress, consent` |
| `app/frontend/.next/server/app/(parent)/parent-dashboard/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, onboarding` |
| `app/frontend/.next/server/app/_global-error/page.js` | `Route, Routes, path:, Link` | `parent` |
| `app/frontend/.next/server/app/_global-error/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, onboarding` |
| `app/frontend/.next/server/app/_not-found/page.js` | `Route, Routes, path:` | `_none_` |
| `app/frontend/.next/server/app/_not-found/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, onboarding` |
| `app/frontend/.next/server/app/admin/content-factory/page.js` | `Route, Routes, path:` | `learner, parent, dashboard, lesson, diagnostic, assessment` |
| `app/frontend/.next/server/app/admin/content-factory/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, onboarding` |
| `app/frontend/.next/server/app/api/auth/login/route.js` | `Route, Routes, path:` | `_none_` |
| `app/frontend/.next/server/app/api/auth/login/route_client-reference-manifest.js` | `Route` | `_none_` |
| `app/frontend/.next/server/app/api/auth/logout/route.js` | `Route, Routes, path:` | `_none_` |
| `app/frontend/.next/server/app/api/auth/logout/route_client-reference-manifest.js` | `Route` | `_none_` |
| `app/frontend/.next/server/app/api/auth/refresh/route.js` | `Route, Routes, path:` | `_none_` |
| `app/frontend/.next/server/app/api/auth/refresh/route_client-reference-manifest.js` | `Route` | `_none_` |
| `app/frontend/.next/server/app/api/auth/register/route.js` | `Route, Routes, path:` | `_none_` |
| `app/frontend/.next/server/app/api/auth/register/route_client-reference-manifest.js` | `Route` | `_none_` |
| `app/frontend/.next/server/app/api/auth/session/route.js` | `Route, Routes, path:` | `_none_` |
| `app/frontend/.next/server/app/api/auth/session/route_client-reference-manifest.js` | `Route` | `_none_` |
| `app/frontend/.next/server/app/api/backend/[...path]/route.js` | `Route, Routes, path:` | `_none_` |
| `app/frontend/.next/server/app/api/backend/[...path]/route_client-reference-manifest.js` | `Route` | `_none_` |
| `app/frontend/.next/server/app/api/backend/route.js` | `Route, Routes, path:` | `_none_` |
| `app/frontend/.next/server/app/api/backend/route_client-reference-manifest.js` | `Route` | `_none_` |
| `app/frontend/.next/server/app/api/health/route.js` | `Route, Routes, path:` | `_none_` |
| `app/frontend/.next/server/app/api/health/route_client-reference-manifest.js` | `Route` | `_none_` |
| `app/frontend/.next/server/app/api/tutor/review/route.js` | `Route, Routes, path:` | `learner, lesson` |
| `app/frontend/.next/server/app/api/tutor/review/route_client-reference-manifest.js` | `Route` | `_none_` |
| `app/frontend/.next/server/app/api/tutor/route.js` | `Route, Routes, path:` | `lesson` |
| `app/frontend/.next/server/app/api/tutor/route_client-reference-manifest.js` | `Route` | `_none_` |
| `app/frontend/.next/server/app/auth/reset-password/page.js` | `Route, Routes, path:, Link` | `learner, parent` |
| `app/frontend/.next/server/app/auth/reset-password/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, onboarding` |
| `app/frontend/.next/server/app/auth/verify-email/page.js` | `Route, Routes, path:, Link` | `onboarding` |
| `app/frontend/.next/server/app/auth/verify-email/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, onboarding` |
| `app/frontend/.next/server/app/learners/[learnerId]/diagnostic/page.js` | `Route, Routes, path:` | `learner, diagnostic` |
| `app/frontend/.next/server/app/learners/[learnerId]/diagnostic/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, onboarding` |
| `app/frontend/.next/server/app/learners/[learnerId]/diagnostic/results/page.js` | `Route, Routes, path:` | `learner, diagnostic` |
| `app/frontend/.next/server/app/learners/[learnerId]/diagnostic/results/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, onboarding` |
| `app/frontend/.next/server/app/learners/[learnerId]/lesson/page.js` | `Route, Routes, path:` | `learner, lesson` |
| `app/frontend/.next/server/app/learners/[learnerId]/lesson/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, onboarding` |
| `app/frontend/.next/server/app/learners/[learnerId]/page.js` | `Route, Routes, path:` | `learner` |
| `app/frontend/.next/server/app/learners/[learnerId]/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, onboarding` |
| `app/frontend/.next/server/app/learners/[learnerId]/plan/page.js` | `Route, Routes, path:` | `learner` |
| `app/frontend/.next/server/app/learners/[learnerId]/plan/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, onboarding` |
| `app/frontend/.next/server/app/onboarding/page.js` | `Route, Routes, path:, Link` | `learner, parent, dashboard, lesson, diagnostic, assessment, progress, consent, onboarding` |
| `app/frontend/.next/server/app/onboarding/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, onboarding` |
| `app/frontend/.next/server/app/page.js` | `Route, Routes, path:` | `learner, parent` |
| `app/frontend/.next/server/app/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, onboarding` |
| `app/frontend/.next/server/app/parent/learners/[learnerId]/consent/page.js` | `Route, Routes, path:` | `learner, parent, consent` |
| `app/frontend/.next/server/app/parent/learners/[learnerId]/consent/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, consent, onboarding` |
| `app/frontend/.next/server/app/parent/learners/[learnerId]/data/page.js` | `Route, Routes, path:` | `learner, parent` |
| `app/frontend/.next/server/app/parent/learners/[learnerId]/data/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, onboarding` |
| `app/frontend/.next/server/app/parent/learners/[learnerId]/report/page.js` | `Route, Routes, path:` | `learner, parent` |
| `app/frontend/.next/server/app/parent/learners/[learnerId]/report/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, onboarding` |
| `app/frontend/.next/server/app/parent-portal/page.js` | `Route, Routes, path:` | `parent` |
| `app/frontend/.next/server/app/parent-portal/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, onboarding` |
| `app/frontend/.next/server/app/settings/privacy/page.js` | `Route, Routes, path:` | `learner, parent, lesson` |
| `app/frontend/.next/server/app/settings/privacy/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, onboarding` |
| `app/frontend/.next/server/chunks/267.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, assessment, progress, consent` |
| `app/frontend/.next/server/chunks/425.js` | `Route, Routes, path:, href=, Link` | `parent, progress` |
| `app/frontend/.next/server/chunks/440.js` | `Route, href=, Link` | `_none_` |
| `app/frontend/.next/server/chunks/481.js` | `Route, Link` | `_none_` |
| `app/frontend/.next/server/chunks/517.js` | `Route, Routes, path:` | `parent` |
| `app/frontend/.next/server/chunks/593.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, assessment` |
| `app/frontend/.next/server/chunks/600.js` | `Route` | `learner, dashboard, lesson` |
| `app/frontend/.next/server/chunks/921.js` | `Route, Link` | `learner, parent, dashboard, lesson, diagnostic, progress, consent` |
| `app/frontend/.next/server/chunks/928.js` | `Link` | `_none_` |
| `app/frontend/.next/server/chunks/985.js` | `Route` | `_none_` |
| `app/frontend/.next/server/instrumentation.js` | `path:` | `parent` |
| `app/frontend/.next/server/interception-route-rewrite-manifest.js` | `Route` | `_none_` |
| `app/frontend/.next/server/server-reference-manifest.js` | `_none_` | `learner, dashboard, lesson, diagnostic` |
| `app/frontend/.next/standalone/.next/server/app/(auth)/login/page.js` | `Route, Routes, path:, Link` | `learner, parent, dashboard, lesson, progress` |
| `app/frontend/.next/standalone/.next/server/app/(auth)/login/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, onboarding` |
| `app/frontend/.next/standalone/.next/server/app/(auth)/register/page.js` | `Route, Routes, path:` | `learner, parent, dashboard, lesson, diagnostic, progress, consent` |
| `app/frontend/.next/standalone/.next/server/app/(auth)/register/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, onboarding` |
| `app/frontend/.next/standalone/.next/server/app/(dashboard)/admin/roadmap/page.js` | `Route, Routes, path:` | `learner, dashboard, lesson, diagnostic, progress` |
| `app/frontend/.next/standalone/.next/server/app/(dashboard)/admin/roadmap/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, onboarding` |
| `app/frontend/.next/standalone/.next/server/app/(learner)/badges/page.js` | `Route, Routes, path:` | `learner, parent, lesson, diagnostic, progress` |
| `app/frontend/.next/standalone/.next/server/app/(learner)/badges/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, onboarding` |
| `app/frontend/.next/standalone/.next/server/app/(learner)/dashboard/page.js` | `Route, Routes, path:` | `learner, parent, dashboard, lesson, diagnostic, assessment, progress` |
| `app/frontend/.next/standalone/.next/server/app/(learner)/dashboard/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, onboarding` |
| `app/frontend/.next/standalone/.next/server/app/(learner)/diagnostic/page.js` | `Route, Routes, path:` | `learner, dashboard, lesson, diagnostic, assessment, progress` |
| `app/frontend/.next/standalone/.next/server/app/(learner)/diagnostic/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, onboarding` |
| `app/frontend/.next/standalone/.next/server/app/(learner)/lesson/page.js` | `Route, Routes, path:` | `learner, lesson` |
| `app/frontend/.next/standalone/.next/server/app/(learner)/lesson/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, onboarding` |
| `app/frontend/.next/standalone/.next/server/app/(learner)/parent/page.js` | `Route, Routes, path:` | `learner, parent, dashboard, lesson, diagnostic, assessment, progress, consent` |
| `app/frontend/.next/standalone/.next/server/app/(learner)/parent/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, onboarding` |
| `app/frontend/.next/standalone/.next/server/app/(learner)/plan/page.js` | `Route, Routes, path:` | `learner, lesson, diagnostic, assessment, progress` |
| `app/frontend/.next/standalone/.next/server/app/(learner)/plan/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, onboarding` |
| `app/frontend/.next/standalone/.next/server/app/(parent)/parent-dashboard/page.js` | `Route, Routes, path:, Link` | `learner, parent, dashboard, lesson, progress, consent` |
| `app/frontend/.next/standalone/.next/server/app/(parent)/parent-dashboard/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, onboarding` |
| `app/frontend/.next/standalone/.next/server/app/_global-error/page.js` | `Route, Routes, path:, Link` | `parent` |
| `app/frontend/.next/standalone/.next/server/app/_global-error/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, onboarding` |
| `app/frontend/.next/standalone/.next/server/app/_not-found/page.js` | `Route, Routes, path:` | `_none_` |
| `app/frontend/.next/standalone/.next/server/app/_not-found/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, onboarding` |
| `app/frontend/.next/standalone/.next/server/app/admin/content-factory/page.js` | `Route, Routes, path:` | `learner, parent, dashboard, lesson, diagnostic, assessment` |
| `app/frontend/.next/standalone/.next/server/app/admin/content-factory/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, onboarding` |
| `app/frontend/.next/standalone/.next/server/app/api/auth/login/route.js` | `Route, Routes, path:` | `_none_` |
| `app/frontend/.next/standalone/.next/server/app/api/auth/login/route_client-reference-manifest.js` | `Route` | `_none_` |
| `app/frontend/.next/standalone/.next/server/app/api/auth/logout/route.js` | `Route, Routes, path:` | `_none_` |
| `app/frontend/.next/standalone/.next/server/app/api/auth/logout/route_client-reference-manifest.js` | `Route` | `_none_` |
| `app/frontend/.next/standalone/.next/server/app/api/auth/refresh/route.js` | `Route, Routes, path:` | `_none_` |
| `app/frontend/.next/standalone/.next/server/app/api/auth/refresh/route_client-reference-manifest.js` | `Route` | `_none_` |
| `app/frontend/.next/standalone/.next/server/app/api/auth/register/route.js` | `Route, Routes, path:` | `_none_` |
| `app/frontend/.next/standalone/.next/server/app/api/auth/register/route_client-reference-manifest.js` | `Route` | `_none_` |
| `app/frontend/.next/standalone/.next/server/app/api/auth/session/route.js` | `Route, Routes, path:` | `_none_` |
| `app/frontend/.next/standalone/.next/server/app/api/auth/session/route_client-reference-manifest.js` | `Route` | `_none_` |
| `app/frontend/.next/standalone/.next/server/app/api/backend/[...path]/route.js` | `Route, Routes, path:` | `_none_` |
| `app/frontend/.next/standalone/.next/server/app/api/backend/[...path]/route_client-reference-manifest.js` | `Route` | `_none_` |
| `app/frontend/.next/standalone/.next/server/app/api/backend/route.js` | `Route, Routes, path:` | `_none_` |
| `app/frontend/.next/standalone/.next/server/app/api/backend/route_client-reference-manifest.js` | `Route` | `_none_` |
| `app/frontend/.next/standalone/.next/server/app/api/health/route.js` | `Route, Routes, path:` | `_none_` |
| `app/frontend/.next/standalone/.next/server/app/api/health/route_client-reference-manifest.js` | `Route` | `_none_` |
| `app/frontend/.next/standalone/.next/server/app/api/tutor/review/route.js` | `Route, Routes, path:` | `learner, lesson` |
| `app/frontend/.next/standalone/.next/server/app/api/tutor/review/route_client-reference-manifest.js` | `Route` | `_none_` |
| `app/frontend/.next/standalone/.next/server/app/api/tutor/route.js` | `Route, Routes, path:` | `lesson` |
| `app/frontend/.next/standalone/.next/server/app/api/tutor/route_client-reference-manifest.js` | `Route` | `_none_` |
| `app/frontend/.next/standalone/.next/server/app/auth/reset-password/page.js` | `Route, Routes, path:, Link` | `learner, parent` |
| `app/frontend/.next/standalone/.next/server/app/auth/reset-password/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, onboarding` |
| `app/frontend/.next/standalone/.next/server/app/auth/verify-email/page.js` | `Route, Routes, path:, Link` | `onboarding` |
| `app/frontend/.next/standalone/.next/server/app/auth/verify-email/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, onboarding` |
| `app/frontend/.next/standalone/.next/server/app/learners/[learnerId]/diagnostic/page.js` | `Route, Routes, path:` | `learner, diagnostic` |
| `app/frontend/.next/standalone/.next/server/app/learners/[learnerId]/diagnostic/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, onboarding` |
| `app/frontend/.next/standalone/.next/server/app/learners/[learnerId]/diagnostic/results/page.js` | `Route, Routes, path:` | `learner, diagnostic` |
| `app/frontend/.next/standalone/.next/server/app/learners/[learnerId]/diagnostic/results/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, onboarding` |
| `app/frontend/.next/standalone/.next/server/app/learners/[learnerId]/lesson/page.js` | `Route, Routes, path:` | `learner, lesson` |
| `app/frontend/.next/standalone/.next/server/app/learners/[learnerId]/lesson/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, onboarding` |
| `app/frontend/.next/standalone/.next/server/app/learners/[learnerId]/page.js` | `Route, Routes, path:` | `learner` |
| `app/frontend/.next/standalone/.next/server/app/learners/[learnerId]/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, onboarding` |
| `app/frontend/.next/standalone/.next/server/app/learners/[learnerId]/plan/page.js` | `Route, Routes, path:` | `learner` |
| `app/frontend/.next/standalone/.next/server/app/learners/[learnerId]/plan/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, onboarding` |
| `app/frontend/.next/standalone/.next/server/app/onboarding/page.js` | `Route, Routes, path:, Link` | `learner, parent, dashboard, lesson, diagnostic, assessment, progress, consent, onboarding` |
| `app/frontend/.next/standalone/.next/server/app/onboarding/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, onboarding` |
| `app/frontend/.next/standalone/.next/server/app/page.js` | `Route, Routes, path:` | `learner, parent` |
| `app/frontend/.next/standalone/.next/server/app/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, onboarding` |
| `app/frontend/.next/standalone/.next/server/app/parent/learners/[learnerId]/consent/page.js` | `Route, Routes, path:` | `learner, parent, consent` |
| `app/frontend/.next/standalone/.next/server/app/parent/learners/[learnerId]/consent/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, consent, onboarding` |
| `app/frontend/.next/standalone/.next/server/app/parent/learners/[learnerId]/data/page.js` | `Route, Routes, path:` | `learner, parent` |
| `app/frontend/.next/standalone/.next/server/app/parent/learners/[learnerId]/data/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, onboarding` |
| `app/frontend/.next/standalone/.next/server/app/parent/learners/[learnerId]/report/page.js` | `Route, Routes, path:` | `learner, parent` |
| `app/frontend/.next/standalone/.next/server/app/parent/learners/[learnerId]/report/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, onboarding` |
| `app/frontend/.next/standalone/.next/server/app/parent-portal/page.js` | `Route, Routes, path:` | `parent` |
| `app/frontend/.next/standalone/.next/server/app/parent-portal/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, onboarding` |
| `app/frontend/.next/standalone/.next/server/app/settings/privacy/page.js` | `Route, Routes, path:` | `learner, parent, lesson` |
| `app/frontend/.next/standalone/.next/server/app/settings/privacy/page_client-reference-manifest.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, onboarding` |
| `app/frontend/.next/standalone/.next/server/chunks/267.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, assessment, progress, consent` |
| `app/frontend/.next/standalone/.next/server/chunks/425.js` | `Route, Routes, path:, href=, Link` | `parent, progress` |
| `app/frontend/.next/standalone/.next/server/chunks/440.js` | `Route, href=, Link` | `_none_` |
| `app/frontend/.next/standalone/.next/server/chunks/481.js` | `Route, Link` | `_none_` |
| `app/frontend/.next/standalone/.next/server/chunks/517.js` | `Route, Routes, path:` | `parent` |
| `app/frontend/.next/standalone/.next/server/chunks/593.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, assessment` |
| `app/frontend/.next/standalone/.next/server/chunks/600.js` | `Route` | `learner, dashboard, lesson` |
| `app/frontend/.next/standalone/.next/server/chunks/921.js` | `Route, Link` | `learner, parent, dashboard, lesson, diagnostic, progress, consent` |
| `app/frontend/.next/standalone/.next/server/chunks/928.js` | `Link` | `_none_` |
| `app/frontend/.next/standalone/.next/server/chunks/985.js` | `Route` | `_none_` |
| `app/frontend/.next/standalone/.next/server/instrumentation.js` | `path:` | `parent` |
| `app/frontend/.next/standalone/.next/server/server-reference-manifest.js` | `_none_` | `learner, dashboard, lesson, diagnostic` |
| `app/frontend/.next/standalone/server.js` | `Route, Routes, Link` | `_none_` |
| `app/frontend/.next/static/chunks/2349-fdb6f7cdc7d3ac75.js` | `Route, path:, Link` | `parent, progress` |
| `app/frontend/.next/static/chunks/2513-98a4a8257e26393a.js` | `Link` | `_none_` |
| `app/frontend/.next/static/chunks/4090-5e94e08d06b809c0.js` | `Route, Routes, path:, href=, Link` | `parent` |
| `app/frontend/.next/static/chunks/4292-a955022516a20e92.js` | `Route, href=, Link` | `_none_` |
| `app/frontend/.next/static/chunks/5608-0086b4f44f3f8b53.js` | `Route, path:` | `parent, progress` |
| `app/frontend/.next/static/chunks/59b4a6e9-015a87f8d1ca2642.js` | `href=, Link` | `parent, progress` |
| `app/frontend/.next/static/chunks/6139-1250c0a8c490b7d3.js` | `_none_` | `parent` |
| `app/frontend/.next/static/chunks/6246-25ccd54b6d198458.js` | `_none_` | `learner, parent, dashboard, lesson, diagnostic, progress, consent` |
| `app/frontend/.next/static/chunks/7403-1294f02f45130ca7.js` | `Route, Link` | `learner, dashboard, lesson` |
| `app/frontend/.next/static/chunks/9913-30eb4a3d8d51fd69.js` | `_none_` | `progress` |
| `app/frontend/.next/static/chunks/app/(auth)/login/page-21d2c305faf671a4.js` | `Route, Link` | `learner, parent, dashboard, lesson, progress` |
| `app/frontend/.next/static/chunks/app/(auth)/register/page-f797f4c208c62ac7.js` | `Route, Link` | `learner, parent, dashboard, lesson, diagnostic, progress, consent` |
| `app/frontend/.next/static/chunks/app/(dashboard)/admin/roadmap/page-0d0270ec84d806bc.js` | `_none_` | `learner, dashboard, lesson, diagnostic, progress` |
| `app/frontend/.next/static/chunks/app/(learner)/badges/page-c545c9892d4474fc.js` | `Link` | `learner, parent, lesson, diagnostic, progress` |
| `app/frontend/.next/static/chunks/app/(learner)/dashboard/page-1fcda78f4cff84e5.js` | `Route, Link` | `learner, parent, dashboard, lesson, diagnostic, assessment, progress` |
| `app/frontend/.next/static/chunks/app/(learner)/diagnostic/page-3a1f6559c1e30e7c.js` | `Route` | `learner, dashboard, diagnostic, assessment, progress` |
| `app/frontend/.next/static/chunks/app/(learner)/layout-bb9d815b3fc6ca9a.js` | `Route, Link` | `learner, parent, dashboard, lesson, diagnostic, assessment` |
| `app/frontend/.next/static/chunks/app/(learner)/parent/page-300c3dfb55685c59.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, assessment, progress, consent` |
| `app/frontend/.next/static/chunks/app/(learner)/plan/page-529f360b9330ce94.js` | `Route, Link` | `learner, lesson, diagnostic, assessment, progress` |
| `app/frontend/.next/static/chunks/app/(parent)/parent-dashboard/page-975cd751a76471de.js` | `Route, Link` | `learner, parent, dashboard, lesson, progress, consent` |
| `app/frontend/.next/static/chunks/app/admin/content-factory/page-56d3071c5cd48835.js` | `path:` | `learner, parent, lesson, diagnostic, assessment` |
| `app/frontend/.next/static/chunks/app/auth/reset-password/page-de0e0d7fac5db486.js` | `Route, Link` | `learner, parent` |
| `app/frontend/.next/static/chunks/app/auth/verify-email/page-b2bba859a63bfffe.js` | `Route, Link` | `onboarding` |
| `app/frontend/.next/static/chunks/app/error-3b2d19b018e93c0d.js` | `Link` | `_none_` |
| `app/frontend/.next/static/chunks/app/layout-4d5da681574338bd.js` | `Route, Link` | `dashboard` |
| `app/frontend/.next/static/chunks/app/learners/[learnerId]/diagnostic/page-e9655271007491c0.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, assessment, progress, consent` |
| `app/frontend/.next/static/chunks/app/learners/[learnerId]/diagnostic/results/page-099d317ae6bdea79.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, assessment, progress, consent` |
| `app/frontend/.next/static/chunks/app/learners/[learnerId]/page-03f7ca5ca3fa2226.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, assessment, progress, consent` |
| `app/frontend/.next/static/chunks/app/learners/[learnerId]/plan/page-10c13cf4ecf9e532.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, assessment, progress, consent` |
| `app/frontend/.next/static/chunks/app/onboarding/page-a1e2b27ef78da0c8.js` | `Route, Link` | `learner, parent, dashboard, lesson, diagnostic, assessment, progress, consent, onboarding` |
| `app/frontend/.next/static/chunks/app/page-433aed3d6d92042f.js` | `Route, Link` | `learner, parent` |
| `app/frontend/.next/static/chunks/app/parent/learners/[learnerId]/consent/page-28748de6300445fd.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, assessment, progress, consent` |
| `app/frontend/.next/static/chunks/app/parent/learners/[learnerId]/data/page-daa3fb269e9f86bd.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, assessment, progress, consent` |
| `app/frontend/.next/static/chunks/app/parent/learners/[learnerId]/report/page-c25130f937b05926.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, assessment, progress, consent` |
| `app/frontend/.next/static/chunks/app/parent-portal/page-9a4a4fe875fbb241.js` | `Route` | `parent, dashboard` |
| `app/frontend/.next/static/chunks/app/settings/privacy/page-a3ffbd72099e48ef.js` | `_none_` | `learner, parent, lesson` |
| `app/frontend/.next/static/chunks/framework-35256df14265b061.js` | `path:, href=, Link` | `parent, progress` |
| `app/frontend/.next/static/chunks/main-2de5cb76fa39f915.js` | `Route, Routes, path:, href=, Link` | `parent, progress` |
| `app/frontend/.next/static/chunks/polyfills-42372ed130431b0a.js` | `path:, href=` | `parent` |
| `app/frontend/.next/static/chunks/webpack-6d2987a23a916cb0.js` | `_none_` | `parent` |
| `app/frontend/.next/static/ogUR-PSrtyrt_G9ObxZYa/_buildManifest.js` | `Route` | `_none_` |
| `app/frontend/.next/types/app/(dashboard)/admin/roadmap/page.ts` | `_none_` | `dashboard` |
| `app/frontend/.next/types/app/(learner)/badges/page.ts` | `_none_` | `learner` |
| `app/frontend/.next/types/app/(learner)/dashboard/page.ts` | `_none_` | `learner, dashboard` |
| `app/frontend/.next/types/app/(learner)/diagnostic/page.ts` | `_none_` | `learner, diagnostic` |
| `app/frontend/.next/types/app/(learner)/parent/page.ts` | `_none_` | `learner, parent` |
| `app/frontend/.next/types/app/(learner)/plan/page.ts` | `_none_` | `learner` |
| `app/frontend/.next/types/app/(parent)/parent-dashboard/page.ts` | `_none_` | `parent, dashboard` |
| `app/frontend/.next/types/app/api/auth/login/route.ts` | `Route` | `_none_` |
| `app/frontend/.next/types/app/api/auth/logout/route.ts` | `Route` | `_none_` |
| `app/frontend/.next/types/app/api/auth/refresh/route.ts` | `Route` | `_none_` |
| `app/frontend/.next/types/app/api/auth/register/route.ts` | `Route` | `_none_` |
| `app/frontend/.next/types/app/api/auth/session/route.ts` | `Route` | `_none_` |
| `app/frontend/.next/types/app/api/backend/[...path]/route.ts` | `Route` | `_none_` |
| `app/frontend/.next/types/app/api/backend/route.ts` | `Route` | `_none_` |
| `app/frontend/.next/types/app/api/health/route.ts` | `Route` | `_none_` |
| `app/frontend/.next/types/app/api/tutor/review/route.ts` | `Route` | `_none_` |
| `app/frontend/.next/types/app/api/tutor/route.ts` | `Route` | `_none_` |
| `app/frontend/.next/types/app/learners/[learnerId]/diagnostic/page.ts` | `_none_` | `learner, diagnostic` |
| `app/frontend/.next/types/app/learners/[learnerId]/diagnostic/results/page.ts` | `_none_` | `learner, diagnostic` |
| `app/frontend/.next/types/app/learners/[learnerId]/lesson/page.ts` | `_none_` | `learner, lesson` |
| `app/frontend/.next/types/app/learners/[learnerId]/page.ts` | `_none_` | `learner` |
| `app/frontend/.next/types/app/learners/[learnerId]/plan/page.ts` | `_none_` | `learner` |
| `app/frontend/.next/types/app/onboarding/page.ts` | `_none_` | `onboarding` |
| `app/frontend/.next/types/app/parent/learners/[learnerId]/consent/page.ts` | `_none_` | `learner, parent, consent` |
| `app/frontend/.next/types/app/parent/learners/[learnerId]/data/page.ts` | `_none_` | `learner, parent` |
| `app/frontend/.next/types/app/parent/learners/[learnerId]/report/page.ts` | `_none_` | `learner, parent` |
| `app/frontend/.next/types/app/parent-portal/page.ts` | `_none_` | `parent` |
| `app/frontend/.next/types/routes.d.ts` | `Route, Routes` | `learner, parent, dashboard, lesson, diagnostic, consent, onboarding` |
| `app/frontend/.next/types/validator.ts` | `Route, Routes` | `learner, parent, dashboard, lesson, diagnostic, consent, onboarding` |
| `app/frontend/__tests__/BetaAndFeedback.test.tsx` | `Link` | `_none_` |
| `app/frontend/__tests__/EntryAndPortal.test.tsx` | `_none_` | `learner, parent, dashboard, lesson, progress, onboarding` |
| `app/frontend/__tests__/EntryScreens.test.tsx` | `_none_` | `learner, parent, onboarding` |
| `app/frontend/__tests__/FeaturePanels.test.tsx` | `_none_` | `learner, dashboard, lesson, diagnostic` |
| `app/frontend/__tests__/InteractiveDiagnostic.test.tsx` | `_none_` | `learner, diagnostic, assessment` |
| `app/frontend/__tests__/InteractiveDiagnosticFlow.test.tsx` | `_none_` | `learner, diagnostic, assessment` |
| `app/frontend/__tests__/ParentDashboard.test.tsx` | `_none_` | `learner, parent, dashboard, lesson, progress, consent` |
| `app/frontend/__tests__/RouteGuard.test.tsx` | `Route, Routes` | `learner, parent` |
| `app/frontend/__tests__/RoutingIntegration.test.tsx` | `Route, Routes` | `learner, dashboard, lesson, diagnostic, assessment` |
| `app/frontend/__tests__/TrustworthyBetaQualityPanel.test.tsx` | `Link` | `diagnostic` |
| `app/frontend/__tests__/client.api.test.ts` | `Route, Routes` | `lesson, diagnostic, progress` |
| `app/frontend/__tests__/offlineSync.test.ts` | `_none_` | `learner, lesson` |
| `app/frontend/__tests__/services.coverage.test.ts` | `_none_` | `learner, parent, dashboard, lesson, diagnostic, consent` |
| `app/frontend/__tests__/services.smoke.test.ts` | `Route` | `learner, lesson, diagnostic, consent` |
| `app/frontend/__tests__/setup.ts` | `_none_` | `diagnostic, progress` |
| `app/frontend/middleware.ts` | `_none_` | `parent, dashboard, onboarding` |
| `app/frontend/next-env.d.ts` | `Route, Routes` | `_none_` |
| `app/frontend/public/service-worker.js` | `_none_` | `parent, dashboard, lesson, diagnostic` |
| `app/frontend/public/sw.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, consent, onboarding` |
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
| `app/frontend/src/app/(learner)/layout.tsx` | `Route` | `learner, parent, dashboard` |
| `app/frontend/src/app/(learner)/lesson/page.tsx` | `_none_` | `learner, lesson` |
| `app/frontend/src/app/(learner)/parent/page.tsx` | `Route` | `parent` |
| `app/frontend/src/app/(learner)/plan/page.tsx` | `Route` | `learner, lesson, diagnostic, assessment, progress` |
| `app/frontend/src/app/(parent)/parent-dashboard/page.tsx` | `Route` | `parent, dashboard` |
| `app/frontend/src/app/admin/content-factory/page.tsx` | `_none_` | `dashboard` |
| `app/frontend/src/app/api/backend/[...path]/route.ts` | `Route, path:` | `_none_` |
| `app/frontend/src/app/api/tutor/review/route.ts` | `_none_` | `learner, parent` |
| `app/frontend/src/app/api/tutor/route.ts` | `_none_` | `lesson` |
| `app/frontend/src/app/auth/reset-password/page.tsx` | `Route, Routes, href=, Link` | `learner, parent` |
| `app/frontend/src/app/auth/verify-email/page.tsx` | `Route, Routes, href=, Link` | `onboarding` |
| `app/frontend/src/app/layout.tsx` | `Link` | `learner` |
| `app/frontend/src/app/learners/[learnerId]/diagnostic/page.tsx` | `Route` | `diagnostic` |
| `app/frontend/src/app/learners/[learnerId]/diagnostic/results/page.tsx` | `Route` | `learner, diagnostic` |
| `app/frontend/src/app/learners/[learnerId]/lesson/page.tsx` | `_none_` | `learner, lesson` |
| `app/frontend/src/app/learners/[learnerId]/page.tsx` | `Route` | `learner` |
| `app/frontend/src/app/learners/[learnerId]/plan/page.tsx` | `Route` | `learner` |
| `app/frontend/src/app/onboarding/page.tsx` | `Route, Link` | `learner, parent, dashboard, lesson, diagnostic, assessment, progress, consent, onboarding` |
| `app/frontend/src/app/page.tsx` | `Route` | `learner, parent` |
| `app/frontend/src/app/parent/learners/[learnerId]/consent/page.tsx` | `Route` | `learner, parent, consent` |
| `app/frontend/src/app/parent/learners/[learnerId]/data/page.tsx` | `Route` | `learner, parent` |
| `app/frontend/src/app/parent/learners/[learnerId]/report/page.tsx` | `Route` | `learner, parent` |
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
| `app/frontend/src/components/e2e/SeededE2ERoutePages.tsx` | `Route, href=, Link` | `learner, parent, dashboard, lesson, diagnostic, assessment, progress, consent` |
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
| `app/frontend/src/components/eduboost/TrustworthyBetaQualityPanel.tsx` | `Route, href=` | `learner` |
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
