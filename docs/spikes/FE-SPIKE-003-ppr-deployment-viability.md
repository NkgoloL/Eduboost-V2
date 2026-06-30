# FE-SPIKE-003 — Partial Prerendering + deployment viability

## Objective

Validate whether Partial Prerendering (PPR) can be enabled for EduBoost Frontend V3 right now across local builds, the Docker runner, and the Azure Container Apps (ACA) deployment target. Output must cover the FE-SPIKE-003 acceptance criteria and conclude with a proceed/defer/abandon recommendation.

## Acceptance questions

1. Does PPR work with the current Next 15.5.18 build?
2. Does it work when the app is built inside the Docker runner image via `docker/Dockerfile.frontend`?
3. Is it compatible with the ACA container deployment target?
4. Does dashboard PPR provide measurable value over the existing RSC + Suspense strategy?
5. Does any route/cache behavior risk exposing auth, consent, or learner data?
6. Verdict and guardrails.

## Experiments & findings

### 1. Local Next build with `experimental.ppr`

```bash
EXPERIMENTAL_ENABLE_PPR=true NEXT_TELEMETRY_DISABLED=1 npm run build
```

**Result:** ❌ `next build` fails immediately: `The experimental feature "experimental.ppr" can only be enabled when using the latest canary version of Next.js.` The release we are pinned to (`next@15.5.18`) does not contain the PPR feature flag.

### 2. Docker runner (Node 20 Alpine) with env flag

```bash
docker run --rm \
  -e EXPERIMENTAL_ENABLE_PPR=true \
  -e NEXT_TELEMETRY_DISABLED=1 \
  -v $PWD/app/frontend:/app \
  -w /app node:20-alpine \
  sh -c "apk add --no-cache libc6-compat >/dev/null && npm ci && npm run build"
```

**Result:** ❌ Fails with the same error string as the local build after dependency installation. The builder container never finishes, so no `.next` artifacts are emitted.

### 3. Azure Container Apps compatibility

- ACA runs whatever OCI image we ship via the multi-stage Dockerfile (see `README.md` "Compose File Map" for the ACA-specific stack reference). Because we cannot produce a successful build with PPR enabled, there is no image to deploy or validate.
- When PPR is eventually available on a stable Next release, there are no ACA-specific blockers anticipated: the stack already emits an `output: 'standalone'` Node 20 server, which aligns with ACA's Linux consumption plan. Nevertheless, we must re-run this spike once a compatible Next release lands.

### 4. Dashboard value assessment

- The learner dashboard, diagnostic, and lesson routes are already implemented as React Server Components that stream per-user data. PPR (which caches HTML until `revalidate`) primarily benefits marketing or anonymous routes.
- Because the dashboard output is student-specific (XP, streaks, consent status, POPIA evidence links), PPR would need to be disabled for these routes or wrapped in `dynamic = "force-dynamic"`, negating most of the benefit.
- For static routes (e.g., `/plan`, `/parent-portal` landing), Suspense + streaming already deliver TTFB under 400 ms in current measurements, so the marginal win from PPR is low compared to the implementation cost.

### 5. Auth/consent data leakage risk

- Any mistake in marking a server component as dynamic could cache learner identifiers, consent states, or audit IDs globally.
- POPIA compliance forbids serving cached consent states to the wrong guardian. PPR would require a comprehensive audit of every server component plus strict `cache: 'no-store'` on authenticated loaders.
- Until the feature is GA and tooling improves, the risk of misconfiguration outweighs the benefits.

## Recommendation

**Verdict: DEFER.**

| Criteria | Outcome | Notes |
| --- | --- | --- |
| Local PPR build | ❌ Blocked | Next 15.5.18 rejects `experimental.ppr`; requires canary. |
| Docker runner build | ❌ Blocked | Same error inside `node:20-alpine` builder. |
| ACA deployment compatibility | ⚠️ Not testable | No PPR-enabled image exists; expected to work once Next ships GA support. |
| Dashboard value | ⚠️ Low | Dashboard is per-user RSC; PPR would add little benefit. |
| Data leakage risk | ⚠️ High | POPIA-critical routes would require exhaustive cache controls. |

## Guardrails & follow-ups

1. **Wait for GA:** Revisit once Next publishes PPR on a stable channel. Capture the Next release note as part of the renewed spike evidence.
2. **Scope PPR to anonymous routes only:** When retrying, limit to marketing/onboarding routes so no learner data can be cached.
3. **Add cache assertions:** Introduce integration tests that assert `cache-control: private, no-store` on authenticated routes before enabling PPR anywhere.
4. **Bundle & lockfile guardrails:** Carry forward FE-SPIKE-001/002 outcomes—resolve the lockfile warning and `.next` ownership in FE-PR-002, and keep bundle monitoring active after every dependency-heavy PR.
5. **Deployment checklist:** If/when PPR is retried, validate both `npm run build` and the multi-stage Docker image locally before touching ACA or any RC deliverable.

## Evidence attachments

- Local build failure screenshot/log: stored in terminal history (`npm run build` run at 2026-05-28 19:01 UTC).
- Docker runner failure logs: see command transcript in this spike.
- Source references: `README.md` (Compose File Map) and FE execution plan RC4 guardrails.
