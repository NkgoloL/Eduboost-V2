# Known Issues and Follow-up Remediation

This file tracks identified issues that are not prerequisites for the current
TSR-B01 closure. Each item preserves its scope, evidence, and required follow-up
without authorising release, deployment, traffic expansion, or payment processing.

## Frontend build-time API URL wiring

**Status:** Identified remediation debt; not a TSR-B01 closure prerequisite.

The active `codex` branch does not currently provide `NEXT_PUBLIC_API_URL` to the
Next.js builder stage. `app/frontend/next.config.js` requires this value outside
development/test and the value is embedded at build time; a runtime Compose
environment variable cannot reliably rewrite the already-built client bundle.

The fix-only change in `9d4c2dd383` adds `ARG NEXT_PUBLIC_API_URL` and matching
builder-stage `ENV` lines to `docker/Dockerfile.frontend`, but its localhost
default is not sufficient as a production deployment contract.
`docker-compose.prod.yml` currently supplies `NEXT_PUBLIC_API_URL` under
`environment`, not `build.args`.

**Required follow-up:** Decide and implement explicit build-time argument wiring
for production (and verify local/staging Compose behavior), with tests or build
evidence proving the intended API URL is present in the built frontend.

This item is tracked separately from B01 governance evidence and does not
authorise release, deployment, traffic expansion, or payment processing.
