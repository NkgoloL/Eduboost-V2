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
