# Production Teacher/Admin Scope Contract

## Purpose

This contract defines teacher/admin UX scope controls for beta and production readiness.

## Required Scope Controls

- Build teacher dashboard if in beta scope.
- Build admin console if in beta scope.
- Build audit dashboard.
- Build content review queue.
- Build class-level diagnostics.
- Build intervention groups.
- Build topic heatmaps.
- Build curriculum coverage admin view.

## Scope Boundary

Teacher/admin UX must be explicitly feature-gated until included in beta scope. Unsupported routes must show a clear forbidden or not-in-scope state rather than exposing partial privileged controls.

## Repository Evidence

- `app/frontend/src/lib/productionReadiness/contracts.ts`
- `docs/frontend/production_protected_route_guard_contract.md`
- `docs/frontend/frontend_auth_consent_denial_contract.md`
