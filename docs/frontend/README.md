# Frontend

The frontend is a Next.js app in `app/frontend` serving learner, parent, auth, and admin experiences.

## Runtime map

- App routes: `app/frontend/src/app/`
- Shared components: `app/frontend/src/components/`
- API client and services: `app/frontend/src/lib/api/`
- Frontend tests: `app/frontend/src/__tests__/` and `app/frontend/__tests__/`

## Current implementation notes

- API calls should go through the typed service/client layer in `src/lib/api`.
- Mocked Playwright or mock dashboard modes are test/local only.
- `NEXT_PUBLIC_CONTENT_FACTORY_MOCK=true` is ignored in production by design.
- Learner-facing pages must not render misleading success/fallback content after API failures.

## Verification

From `app/frontend`:

```bash
npm run type-check
npm test
npm run lint
npm run build
```

Back to the main index: [docs/README.md](../README.md). Root overview: [README.md](../../README.md).
