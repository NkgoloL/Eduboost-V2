# Render Frontend/Backend Connectivity Report

Date: 2026-05-24

## Live services checked

- Frontend: `srv-d88nokn7f7vs73beo9dg`, `https://eduboos-frontend.onrender.com`
- Backend: `srv-d86pc7mk1jcs739h4r0g`, `https://eduboost-api.onrender.com`

## Findings

1. The deployed frontend bundle is compiled with `NEXT_PUBLIC_API_URL=https://eduboost-api.onrender.com`. The app client expects the API base to include `/api/v2`, so browser calls are aimed at paths such as `/auth/login` instead of `/api/v2/auth/login`. Set frontend `NEXT_PUBLIC_API_URL=https://eduboost-api.onrender.com/api/v2` and redeploy the frontend.
2. Backend CORS preflight from `https://eduboos-frontend.onrender.com` returned `400 Disallowed CORS origin`. The deployed Render config used `CORS_ORIGINS`, while the FastAPI settings read `ALLOWED_ORIGINS`. `render.yaml` now uses `ALLOWED_ORIGINS`, and the settings class accepts `CORS_ORIGINS` as a backward-compatible alias.
3. The live backend is healthy, but free-tier Render cold starts caused an initial health request to time out before a later `/health` returned `200`. Expect the first user request after idle to be slow unless the backend is moved off the free plan or warmed.
4. Render service metadata says both services deploy from branch `main`, while this local checkout tracks `origin/master`. Confirm which branch Render should follow; fixes pushed only to `master` will not deploy if the service remains pinned to `main`.
5. Backend logs show `ENVIRONMENT=production` but `APP_ENV=development`. `render.yaml` now sets both to `production` so production-only behavior and logging agree.
6. The production backend intentionally returns `404` for `/api/v2/auth/dev-session`. The frontend bundle still contains the dev-session flow, so production must have `NEXT_PUBLIC_ENABLE_DEV_SESSION=false` and real login/register must be used for smoke tests.

## Required Render environment values

Backend service:

```env
ENVIRONMENT=production
APP_ENV=production
FRONTEND_URL=https://eduboos-frontend.onrender.com
ALLOWED_ORIGINS=https://eduboos-frontend.onrender.com,http://localhost:3050,http://127.0.0.1:3050
API_BASE_URL=https://eduboost-api.onrender.com
```

Frontend service:

```env
NEXT_PUBLIC_API_URL=https://eduboost-api.onrender.com/api/v2
NEXT_PUBLIC_APP_ENV=production
NEXT_PUBLIC_ENABLE_DEV_SESSION=false
```

## Admin test account

A production-safe seed script was added at `scripts/ensure_admin_account.py`. It creates a guardian account with `role=admin` or promotes an existing guardian with the same email. It reads credentials from environment variables only, so no test password is committed.

Run it in the backend service environment after setting:

```env
DEV_ADMIN_EMAIL=<test-admin-email>
DEV_ADMIN_PASSWORD=<strong-test-password>
DEV_ADMIN_DISPLAY_NAME=EduBoost Admin
RESET_DEV_ADMIN_PASSWORD=true
```

Command:

```bash
python scripts/ensure_admin_account.py
```

## Outstanding feature and readiness list

- Frontend/backend connection is not fully live until the frontend API base includes `/api/v2`, backend `ALLOWED_ORIGINS` includes the Render frontend URL, and both services are redeployed.
- Supabase/Resend auth integration exists in local WIP branch `codex/supabase-resend-auth` and is not reflected in the currently deployed `master`/Render flow unless it is merged into the Render deploy branch.
- Real production login/register smoke tests are still outstanding after env fixes. The dev-session shortcut cannot be used in production.
- Admin account creation still needs one production execution with the chosen test email/password.
- Lesson generation still needs live proof with a guardian, learner, active consent, and configured LLM provider credentials. Missing consent or provider secrets will block or degrade generation.
- Diagnostic tests still need live proof with seeded/available diagnostic items for the learner grade and subject. If the item bank is empty or migrations/seeds are missing, learners cannot take diagnostics.
- Parent/learner onboarding still needs an end-to-end production smoke: register/login, create learner, grant consent, switch learner context, and return to parent dashboard.
- Study-plan and recommendation flows still need live proof after diagnostics and consent are working.
- Email confirmation/password reset/onboarding flows depend on the Supabase/Resend work being merged and configured in the deployed branch.
- Background job behavior for lesson generation should be checked under Render restarts/cold starts, because in-memory job state can be lost if the service restarts.
- The frontend production bundle should be rebuilt after env changes and rechecked to confirm it no longer contains the wrong API base.
- Branch alignment is unresolved: Render currently reports `main`; local active branch is `master`.
