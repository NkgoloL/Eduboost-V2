---
title: "Production Protected Route Guard Contract"
status: active
owner: frontend
reviewers: [frontend, product, privacy]
audience: developer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-06-24
review_interval_days: 60
evidence_command: "make docs-housekeeping-stage5-check"
code_anchors: [app/frontend, docs/frontend/README.md]
---

# Production Protected Route Guard Contract

## Purpose

This contract defines protected-route behavior for learner, parent, teacher, and admin entry points.

## Required Protected Route Controls

- Add protected route guard for learner dashboard.
- Add protected route guard for parent dashboard.
- Add protected route guard for teacher dashboard.
- Add protected route guard for admin dashboard.
- Add role-based redirect rules.
- Add unauthorized state.
- Add forbidden state.
- Add tests for route guards.

## Route Guard Matrix

- `/dashboard` requires learner context.
- `/parent-dashboard` requires guardian context.
- `/teacher-dashboard` is role-restricted and beta-scope gated.
- `/admin-dashboard` is role-restricted and beta-scope gated.

## Repository Evidence

- `app/frontend/src/components/eduboost/RouteGuard.tsx`
- `app/frontend/src/lib/productionReadiness/contracts.ts`
- `docs/frontend/frontend_auth_consent_denial_contract.md`
