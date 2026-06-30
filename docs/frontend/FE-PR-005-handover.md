# FE-PR-005 Handover — Typed API Client, Auth Proxy, Middleware

## Scope
- Browser API client now forces all relative requests through `/api/backend/*` and injects request IDs + retry-on-401 refresh logic
- `/api/auth/login`, `/api/auth/register`, `/api/auth/logout`, `/api/auth/refresh`, and `/api/auth/session` proxy routes mediate every auth flow
- Server-only session helpers (`getSessionToken`, `getSessionClaims`, `setSessionCookie`, `clearSessionCookie`) centralize token handling
- HttpOnly cookie `eduboost_session` replaces legacy localStorage tokens across runtime and tests
- Middleware protects RC1 routes based purely on cookie presence (no backend call)
- RouteGuard uses `/api/auth/session` to gate parent/teacher views and LearnerContext to gate learner flows
- Legacy localStorage token persistence removed (see `pnpm --filter frontend test` + `grep` evidence below)

## Cookie Policy
| Property | Value |
| --- | --- |
| Name | `eduboost_session` |
| httpOnly | `true` |
| sameSite | `strict` |
| secure | `process.env.NODE_ENV === "production"` |
| path | `/` |
| maxAge | 30 days (set by backend refresh cycle) |

The cookie is written only via server routes (login/register/refresh) and cleared via logout + refresh failures.

## Protected Routes
Middleware currently guards:
- `/dashboard`
- `/parent-dashboard`
- `/teacher`
- `/teacher/*`
- `/admin`
- `/admin/*`
- `/settings`
- `/onboarding`

Routes outside this list remain public by design (auth/login/register, marketing, etc.).

## Proxy Safety
- `/api/backend/[...path]` sanitizes every segment (rejects `..`, encodes path parts) before contacting the backend origin
- Only `accept`, `content-type`, and `x-request-id` headers are forwarded from the browser request
- Request bodies are streamed verbatim but only for non-GET/HEAD methods
- Backend origin is defined server-side (no user-controlled host input)
- Set-Cookie headers coming from backend are replayed through NextResponse for server-driven session rotation
- Browser never forwards `Authorization` headers or stores tokens

## Test Coverage
- `src/__tests__/authRoutes.test.ts` — covers login/logout/refresh/session proxy routes, backend proxy sanitization, and middleware redirects
- `__tests__/client.api.test.ts` — validates `/api/backend` routing, 204 handling, ApiError surfacing, and `/api/auth/refresh` retry
- `__tests__/RouteGuard.test.tsx` — asserts guardian/teacher flows fetch `/api/auth/session` and show the correct prompts & navigation
- `__tests__/services.smoke.test.ts` & `src/__tests__/ApiLayer.test.ts` — verify AuthService/LearnerService wiring with proxy routes plus job polling
- `src/__tests__/LearnerJourneys.test.ts` — confirms learner dashboards remain wired without token storage hacks
- Legacy localStorage token usage removed; the latest `grep -R "guardian_token|learner_token|localStorage.*token"` only matches backend payload type names and mock API responses (see run output in terminal history)

## Verification
| Command | Result |
| --- | --- |
| `pnpm run type-check` | ✅ (tsc --noEmit) |
| `pnpm run lint` | ✅ (`next lint --no-cache`) |
| `pnpm test` | ✅ (Vitest, 104 tests) |
| `pnpm run build` | ✅ (Next.js 15.5.18 production bundle) |
| `ANALYZE=true pnpm run build` | ✅ (bundle reports in `.next/analyze/{client,edge,nodejs}.html`) |

## Guardrails
- PPR remains disabled — no partial prerendering or streaming introduced
- All auth tests/middleware rely on synthetic data only; no production secrets captured
- No RC5/guardian-dashboard/WhatsApp/etc. dependencies were added per scope guardrails
- Learner/diagnostic feature surfaces unchanged aside from auth plumbing
- FE-PR-003 strict SSR + auth requirements remain intact (cookies only, no token storage)
- `exactOptionalPropertyTypes` deferment remains under FE-TS-EXACT-OPTIONAL-001 so TS config is untouched
