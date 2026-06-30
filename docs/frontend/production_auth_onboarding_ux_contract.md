# Production Auth and Onboarding UX Contract

## Purpose

This contract records the production auth and onboarding UX requirements for guardian, learner, and consent flows.

## Required Auth and Onboarding UX

- Complete guardian signup screen.
- Complete guardian login screen.
- Complete logout UX.
- Complete session-expiry UX.
- Complete password reset request screen.
- Complete password reset completion screen.
- Complete email verification UX.
- Complete learner profile creation.
- Complete grade selection.
- Complete subject selection.
- Complete parental consent capture.
- Complete onboarding completion route.
- Add onboarding progress indicator.
- Add recoverable onboarding state.
- Add onboarding E2E test.

## Required States

- loading
- validation error
- canonical API error
- session expired
- unauthorized
- forbidden
- consent required
- onboarding complete

## Repository Evidence

- `app/frontend/src/app/(auth)/login/page.tsx`
- `app/frontend/src/app/(auth)/register/page.tsx`
- `app/frontend/src/components/eduboost/EntryScreens.tsx`
- `app/frontend/src/context/LearnerContext.tsx`
- `app/frontend/src/app/(learner)/parent/page.tsx`
- `app/frontend/src/lib/productionReadiness/contracts.ts`
