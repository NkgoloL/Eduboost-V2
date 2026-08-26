---
title: "Frontend Route Inventory"
status: "active"
owner: "quality"
reviewers: ["quality", "engineering"]
audience: "developer"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-08-26"
review_interval_days: 60
evidence_command: "make docs-housekeeping-check"
code_anchors: ["docs/frontend/frontend_route_inventory.md"]
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
| `app/frontend/.next/dev/server/app/page.js` | `Route, Routes, path:, Link` | `learner, parent, dashboard, lesson, diagnostic, progress, consent` |
| `app/frontend/.next/dev/server/app/page_client-reference-manifest.js` | `Route` | `learner` |
| `app/frontend/.next/dev/server/edge-instrumentation.js` | `path:, Link` | `parent` |
| `app/frontend/.next/dev/server/edge-runtime-webpack.js` | `_none_` | `parent, progress` |
| `app/frontend/.next/dev/server/interception-route-rewrite-manifest.js` | `Route` | `_none_` |
| `app/frontend/.next/dev/server/vendor-chunks/lucide-react@1.17.0_react@18.3.1.js` | `Route` | `_none_` |
| `app/frontend/.next/dev/server/vendor-chunks/next-themes@0.4.6_react-dom@18.3.1_react@18.3.1__react@18.3.1.js` | `Route` | `_none_` |
| `app/frontend/.next/dev/server/vendor-chunks/next@16.2.7_@babel+core@7.29.7_react-dom@18.3.1_react@18.3.1__react@18.3.1.js` | `Route, Routes, path:, Link` | `parent, progress` |
| `app/frontend/.next/dev/server/vendor-chunks/sonner@2.0.7_react-dom@18.3.1_react@18.3.1__react@18.3.1.js` | `Route, Link` | `_none_` |
| `app/frontend/.next/dev/server/vendor-chunks/zod@4.4.3.js` | `path:, Link` | `parent` |
| `app/frontend/.next/dev/static/chunks/app/error.js` | `Link` | `_none_` |
| `app/frontend/.next/dev/static/chunks/app/layout.js` | `Route, href=, Link` | `learner, parent, dashboard, lesson, diagnostic, progress, consent` |
| `app/frontend/.next/dev/static/chunks/app/loading.js` | `Link` | `_none_` |
| `app/frontend/.next/dev/static/chunks/app/page.js` | `Route, Link` | `learner, parent` |
| `app/frontend/.next/dev/static/chunks/app-pages-internals.js` | `Route, Routes, path:, Link` | `parent` |
| `app/frontend/.next/dev/static/chunks/main-app.js` | `Route, Routes, path:, href=, Link` | `parent, progress` |
| `app/frontend/.next/dev/static/chunks/polyfills.js` | `path:, href=` | `parent` |
| `app/frontend/.next/dev/static/chunks/webpack.js` | `Link` | `parent, progress` |
| `app/frontend/.next/dev/static/development/_buildManifest.js` | `Route` | `_none_` |
| `app/frontend/.next/dev/types/routes.d.ts` | `Route, Routes` | `learner, parent, dashboard, lesson, diagnostic, consent, onboarding` |
| `app/frontend/.next/dev/types/validator.ts` | `Route, Routes` | `learner, parent, dashboard, lesson, diagnostic, consent, onboarding` |
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
| `app/frontend/.next/server/chunks/214.js` | `Link` | `_none_` |
| `app/frontend/.next/server/chunks/571.js` | `Route, Link` | `learner, parent, dashboard, lesson, diagnostic, progress, consent` |
| `app/frontend/.next/server/chunks/59.js` | `Route, Routes, path:` | `parent` |
| `app/frontend/.next/server/chunks/638.js` | `Route, href=, Link` | `_none_` |
| `app/frontend/.next/server/chunks/651.js` | `Route, Routes, path:, href=, Link` | `parent, progress` |
| `app/frontend/.next/server/chunks/663.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, assessment` |
| `app/frontend/.next/server/chunks/74.js` | `Route` | `learner, dashboard, lesson` |
| `app/frontend/.next/server/chunks/839.js` | `Route, Link` | `_none_` |
| `app/frontend/.next/server/chunks/952.js` | `Route` | `_none_` |
| `app/frontend/.next/server/chunks/975.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, assessment, progress, consent` |
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
| `app/frontend/.next/standalone/.next/server/chunks/214.js` | `Link` | `_none_` |
| `app/frontend/.next/standalone/.next/server/chunks/571.js` | `Route, Link` | `learner, parent, dashboard, lesson, diagnostic, progress, consent` |
| `app/frontend/.next/standalone/.next/server/chunks/59.js` | `Route, Routes, path:` | `parent` |
| `app/frontend/.next/standalone/.next/server/chunks/638.js` | `Route, href=, Link` | `_none_` |
| `app/frontend/.next/standalone/.next/server/chunks/651.js` | `Route, Routes, path:, href=, Link` | `parent, progress` |
| `app/frontend/.next/standalone/.next/server/chunks/663.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, assessment` |
| `app/frontend/.next/standalone/.next/server/chunks/74.js` | `Route` | `learner, dashboard, lesson` |
| `app/frontend/.next/standalone/.next/server/chunks/839.js` | `Route, Link` | `_none_` |
| `app/frontend/.next/standalone/.next/server/chunks/952.js` | `Route` | `_none_` |
| `app/frontend/.next/standalone/.next/server/chunks/975.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, assessment, progress, consent` |
| `app/frontend/.next/standalone/.next/server/instrumentation.js` | `path:` | `parent` |
| `app/frontend/.next/standalone/.next/server/server-reference-manifest.js` | `_none_` | `learner, dashboard, lesson, diagnostic` |
| `app/frontend/.next/standalone/server.js` | `Route, Routes, Link` | `_none_` |
| `app/frontend/.next/static/chunks/150-5744df029247e381.js` | `_none_` | `learner, parent, dashboard, lesson, diagnostic, progress, consent` |
| `app/frontend/.next/static/chunks/177-5ed9bf00901605ae.js` | `_none_` | `parent` |
| `app/frontend/.next/static/chunks/3972-5dc94851549719f3.js` | `Route, path:, Link` | `parent, progress` |
| `app/frontend/.next/static/chunks/4786-aa704dfbfc09c4e0.js` | `Route, Link` | `learner, dashboard, lesson` |
| `app/frontend/.next/static/chunks/4898-a13c5cd3211f02da.js` | `Route, href=, Link` | `_none_` |
| `app/frontend/.next/static/chunks/5324606e-5a1f20cd31d1dbc4.js` | `href=, Link` | `parent, progress` |
| `app/frontend/.next/static/chunks/5361-9441d20ebdea58e2.js` | `Link` | `_none_` |
| `app/frontend/.next/static/chunks/7310-c38983e6838bd699.js` | `Route, Routes, path:, href=, Link` | `parent` |
| `app/frontend/.next/static/chunks/7785-9c2587707b643870.js` | `Route, path:` | `parent, progress` |
| `app/frontend/.next/static/chunks/8921-0cbcce81ed4d181c.js` | `_none_` | `progress` |
| `app/frontend/.next/static/chunks/app/(auth)/login/page-e45f909be66ef8ea.js` | `Route, Link` | `learner, parent, dashboard, lesson, progress` |
| `app/frontend/.next/static/chunks/app/(auth)/register/page-0f6fefb0be32fd12.js` | `Route, Link` | `learner, parent, dashboard, lesson, diagnostic, progress, consent` |
| `app/frontend/.next/static/chunks/app/(dashboard)/admin/roadmap/page-d04344109194a642.js` | `_none_` | `learner, dashboard, lesson, diagnostic, progress` |
| `app/frontend/.next/static/chunks/app/(learner)/badges/page-511fa57743aa813d.js` | `Link` | `learner, parent, lesson, diagnostic, progress` |
| `app/frontend/.next/static/chunks/app/(learner)/dashboard/page-4e1e4cabaddb7fa7.js` | `Route, Link` | `learner, parent, dashboard, lesson, diagnostic, assessment, progress` |
| `app/frontend/.next/static/chunks/app/(learner)/diagnostic/page-516d72bf623cc30b.js` | `Route` | `learner, dashboard, diagnostic, assessment, progress` |
| `app/frontend/.next/static/chunks/app/(learner)/layout-b64fc720b237c2e2.js` | `Route, Link` | `learner, parent, dashboard, lesson, diagnostic, assessment` |
| `app/frontend/.next/static/chunks/app/(learner)/parent/page-0b83d06c90343837.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, assessment, progress, consent` |
| `app/frontend/.next/static/chunks/app/(learner)/plan/page-a5b5507807f6b41f.js` | `Route, Link` | `learner, lesson, diagnostic, assessment, progress` |
| `app/frontend/.next/static/chunks/app/(parent)/parent-dashboard/page-5fd6a387f6e4f904.js` | `Route, Link` | `learner, parent, dashboard, lesson, progress, consent` |
| `app/frontend/.next/static/chunks/app/admin/content-factory/page-97ada7441e15df01.js` | `path:` | `learner, parent, lesson, diagnostic, assessment` |
| `app/frontend/.next/static/chunks/app/auth/reset-password/page-09fef0baf348d14b.js` | `Route, Link` | `learner, parent` |
| `app/frontend/.next/static/chunks/app/auth/verify-email/page-b6ea09af5cee3317.js` | `Route, Link` | `onboarding` |
| `app/frontend/.next/static/chunks/app/error-611fa45df544997c.js` | `Link` | `_none_` |
| `app/frontend/.next/static/chunks/app/layout-ad5f2df69bfeaf2b.js` | `Route, Link` | `dashboard` |
| `app/frontend/.next/static/chunks/app/learners/[learnerId]/diagnostic/page-fcfe15dee825d768.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, assessment, progress, consent` |
| `app/frontend/.next/static/chunks/app/learners/[learnerId]/diagnostic/results/page-080f137a532fa1f2.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, assessment, progress, consent` |
| `app/frontend/.next/static/chunks/app/learners/[learnerId]/page-4726045aa512bc71.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, assessment, progress, consent` |
| `app/frontend/.next/static/chunks/app/learners/[learnerId]/plan/page-4fd2dd474bdf7054.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, assessment, progress, consent` |
| `app/frontend/.next/static/chunks/app/onboarding/page-b9440c18e9435f5f.js` | `Route, Link` | `learner, parent, dashboard, lesson, diagnostic, assessment, progress, consent, onboarding` |
| `app/frontend/.next/static/chunks/app/page-f9fca46877ab0240.js` | `Route, Link` | `learner, parent` |
| `app/frontend/.next/static/chunks/app/parent/learners/[learnerId]/consent/page-9b537aa3795712dd.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, assessment, progress, consent` |
| `app/frontend/.next/static/chunks/app/parent/learners/[learnerId]/data/page-e76b57b96b057ab5.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, assessment, progress, consent` |
| `app/frontend/.next/static/chunks/app/parent/learners/[learnerId]/report/page-1f83cf62ff8d8461.js` | `Route` | `learner, parent, dashboard, lesson, diagnostic, assessment, progress, consent` |
| `app/frontend/.next/static/chunks/app/parent-portal/page-0bccd6008b7cf3ca.js` | `Route` | `parent, dashboard` |
| `app/frontend/.next/static/chunks/app/settings/privacy/page-6151849e5146033c.js` | `_none_` | `learner, parent, lesson` |
| `app/frontend/.next/static/chunks/framework-35256df14265b061.js` | `path:, href=, Link` | `parent, progress` |
| `app/frontend/.next/static/chunks/main-9c0abf5024c4bdc4.js` | `Route, Routes, path:, href=, Link` | `parent, progress` |
| `app/frontend/.next/static/chunks/polyfills-42372ed130431b0a.js` | `path:, href=` | `parent` |
| `app/frontend/.next/static/chunks/webpack-f6b30817e1d90e62.js` | `_none_` | `parent` |
| `app/frontend/.next/static/i5LtwVRuM3lz3ARnN7S06/_buildManifest.js` | `Route` | `_none_` |
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
