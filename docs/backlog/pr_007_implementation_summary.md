# PR-007 Frontend core flows and accessibility

## Scope

PR-007 hardens the Next.js frontend core flows without changing backend runtime contracts. The patch focuses on browser-safe environment handling, typed API access, route guards, guardian onboarding/consent, parent privacy controls, diagnostic/lesson accessibility, and mobile usability.

## Completed work

### Environment and API safety

- Added `app/frontend/src/lib/env.ts` to define browser-safe environment handling.
- Added `scripts/validate_frontend_env.py` to fail on secret-like `NEXT_PUBLIC_*` names.
- Added frontend `env-check`, `a11y-check`, and `pr-007-check` npm scripts.
- Upgraded `app/frontend/src/lib/api/client.ts` with:
  - normalized `ApiError`
  - API envelope unwrapping
  - request ID propagation via `X-Request-ID`
  - credentialed requests for refresh-cookie flows
  - refresh-on-401 retry
  - safer JWT payload decoding
- Expanded `app/frontend/src/lib/api/types.ts` and `services.ts` for auth sessions, consent, data-rights, diagnostics, lesson metadata, and learner creation.

### Route hardening

- Added `ErrorBoundary`, `app/error.tsx`, and `app/loading.tsx`.
- Added root `SkipLink` and route-level error boundary wrapper.
- Added `RouteGuard` and wired learner/parent route groups.
- Added logout through `/auth/logout` instead of only local state clearing.

### Core UX flows

- Rebuilt registration into a guardian + learner + consent onboarding flow.
- Added guardian login improvements and controlled dev-session visibility.
- Added parent dashboard POPIA data-rights controls:
  - request learner export
  - restrict processing
  - request erasure
- Kept password reset/email verification explicitly partial because backend endpoints/templates are not yet present.

### Accessibility and mobile

- Added semantic navigation/buttons in the shell.
- Added mobile bottom navigation for primary learner flows.
- Added skip link, focus-visible, form error, screen-reader-only, and reduced-motion CSS.
- Added diagnostic progressbar/radiogroup/radio semantics.
- Added accessible form labels, `aria-invalid`, error descriptions, and autocomplete hints.
- Added static accessibility contract tests in `AccessibilityContracts.test.tsx`.

## TODO updates

Marked done:

- TODO-164 browser-safe environment separation
- TODO-165 no exposed `NEXT_PUBLIC_*` secrets
- TODO-166 error boundaries
- TODO-167 loading/empty/failure states baseline
- TODO-168 typed API client with auth/refresh/request ID/errors
- TODO-169 protected route guards baseline
- TODO-171 signup/onboarding baseline
- TODO-174 parent dashboard privacy controls baseline
- TODO-175 diagnostic UX baseline
- TODO-178 WCAG 2.1 AA baseline
- TODO-179 keyboard/accessibility contract tests baseline
- TODO-180 accessible form validation/contrast baseline
- TODO-181 semantic headings/landmarks/diagnostic ARIA
- TODO-183 mobile learner/parent usability baseline

Left partial intentionally:

- TODO-172 password reset/email verification UX needs backend endpoints/templates.
- TODO-176 richer lesson interactions and report-content issue flow remain pending.
- TODO-182 reduced motion is done; typography/audio controls remain pending.
- TODO-184 browser viewport tests remain pending due frontend test dependency/runtime issues.
- TODO-185 PWA/offline strategy was not expanded in this PR.

## Validation

Passed:

```bash
cd app/frontend && npm run type-check
python scripts/validate_frontend_env.py
git diff --check
```

Not completed:

```bash
cd app/frontend && npm run test
```

The sandbox failed before running tests because `node_modules/.bin/vitest` is not executable in the uploaded ZIP. Running Vitest via Node then exposed the existing optional Rollup native package issue: `@rollup/rollup-linux-x64-gnu` is missing from `node_modules`. This appears to be a local dependency-install artifact rather than a PR-007 TypeScript error.

Recommended local repair:

```bash
cd app/frontend
rm -rf node_modules
npm ci --legacy-peer-deps
npm run pr-007-check
```

## Next recommended PR

PR-008 DevOps/observability/DR should address production image build hygiene, environment validation, deployment target alignment, metrics, alerts, and smoke checks.
