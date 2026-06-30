# FE-SPIKE-001 — Next 15 + React 19 compatibility in the Docker runner

## Objective

Validate that the EduBoost frontend can run on the RC baseline (Next.js 15.5.x + React 19.x) when built through the existing `docker/Dockerfile.frontend` pipeline so we can safely fan-out FE-PR-001 and FE-PR-002.

## What changed during the spike

- Bumped `react` and `react-dom` to `19.2.6` inside `app/frontend/package.json` and regenerated the lockfile via `npm install`.
- Purged the root-owned `.next` artifacts that were left behind by older Docker runs (`docker run --rm -v $PWD/app/frontend:/app alpine rm -rf /app/.next`).

## Commands executed

1. `npm ci` — refresh local deps against the existing lock.
2. `NEXT_TELEMETRY_DISABLED=1 npm run build` — verifies the Next/React combo on bare metal.
3. `docker build -f docker/Dockerfile.frontend -t eduboost-frontend:spike --target production app/frontend` — reproduces the CI builder stage inside Node 20-alpine.

## Findings

- ✅ Next.js 15.5.18 + React 19.2.6 compile cleanly (TypeScript + ESLint pass) with the current source. Evidence: `next build` completed in 15.8s and emitted the standard route table.
- ✅ The production Docker target produced an image (`eduboost-frontend:spike`) using the existing multi-stage file, confirming no Alpine-level incompatibilities.
- ⚠️ `next build` still logs the "multiple lockfiles" warning because the app lives under `app/frontend`. We should set `outputFileTracingRoot: path.resolve(__dirname, "..", "..")` in FE-PR-001 to silence it.
- ⚠️ `.next` artifacts become root-owned whenever the app is started via `docker compose up frontend`. Add a `npm run clean` script (or document `docker run ... rm -rf`) in FE-PR-001 so future builds do not fail with `EACCES`.
- ⚠️ React hook lint warnings remain in the content factory panels. These pre-date the upgrade but must be addressed before freezing RC3 (tracked for FE-PR-006).

## Impact

- React 19 can remain pinned going forward; no regressions observed in build or lint.
- Backend contract mocks are unaffected because no runtime behavior changed.
- The Docker route is now unblocked for FE-PR-001 (ADR/rollback) and FE-PR-002 (skeleton screens) work.

## Follow-up actions (feed into FE-PR backlog)

1. Add `outputFileTracingRoot` + a `clean` npm script in FE-PR-001.
2. Capture the React hook lint violations in FE-PR-006 acceptance criteria.
3. Ensure `docker compose up frontend` runs as the project UID/GID to avoid root-owned artifacts (documented in ADR-010 once drafted).
