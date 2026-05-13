# Production Frontend UX Accessibility Mobile Contract

## Purpose

This contract defines accessibility and mobile-readiness expectations for production frontend UX.

## Required Accessibility and Mobile Controls

- Meet WCAG 2.1 AA for signup.
- Meet WCAG 2.1 AA for login.
- Meet WCAG 2.1 AA for consent.
- Meet WCAG 2.1 AA for diagnostic.
- Meet WCAG 2.1 AA for lesson.
- Meet WCAG 2.1 AA for dashboards.
- Add keyboard navigation tests.
- Ensure sufficient color contrast.
- Add accessible form validation.
- Add semantic headings.
- Add landmarks.
- Add screen-reader friendly diagnostic questions.
- Make all learner flows usable on mobile.
- Make all parent flows usable on mobile.
- Add responsive layout tests.
- Add reduced-motion mode.
- Add dyslexia-friendly typography option.
- Add text resizing.
- Add audio narration if product scope supports it.

## Repository Evidence

- `docs/frontend/frontend_accessibility_contract.md`
- `docs/frontend/frontend_accessibility_static_scan.md`
- `docs/frontend/accessibility_pwa_e2e_evidence.md`
- `app/frontend/src/components/accessibility/A11y.tsx`
- `app/frontend/src/__tests__/AccessibilityContracts.test.tsx`
