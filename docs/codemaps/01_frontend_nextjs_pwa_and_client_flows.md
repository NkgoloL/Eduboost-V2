# EduBoost V2 Frontend, Next.js PWA, and Client Flows

Maps App Router composition, authentication guards, API access, offline/PWA behaviour, and the learner, parent, and administrator user journeys.

## Scope and ownership

This codemap is the primary architecture owner for:
- `app/frontend`

It describes current implementation paths in repository-relative form. Related cross-cutting behaviour may be referenced from other codemaps, but every maintained source file has one primary owner in `codemap_coverage_manifest.json`.

## Architectural position

This area participates in the wider EduBoost request, data, evidence, and release architecture. Read it together with `00_application_bootstrap_and_request_lifecycle.md`, `17_testing_ci_coverage_security_and_quality_gates.md`, and `18_production_readiness_release_evidence_and_live_traffic.md` when changing runtime or release-critical behaviour.

## Trace ID: 1
**Title:** App Router shell, session boundary, and route guards

**Description:** Follows browser navigation through the root layout, authenticated layouts, session loading, and protected route decisions.

**Motivation:**
The frontend is the first enforcement and usability layer. It must guide users correctly without being treated as the sole security boundary.

**Details:**

**Execution path**

1. Render the root layout and shared providers.
2. Load server or browser session state.
3. Enter an auth, learner, parent, or administrator route group.
4. Apply route guard and role-aware navigation.
5. Render loading, error, or destination content.

**State and ownership boundaries**

Session hints may be cached client-side, but authorization remains authoritative in the backend.

**Failure, privacy, and control points**

Route guards fail closed for protected screens, preserve return paths safely, and never expose private data during loading.

**Verification signals**

Run routing, RouteGuard, entry-screen, and parent-dashboard tests across authenticated, expired, and unauthorized states.

**Trace text diagram:**
```text
1. Render the root layout and shared providers [1a]
   |
   v
2. Load server or browser session state [1b]
   |
   v
3. Enter an auth, learner, parent, or administrator route group [1c]
   |
   v
4. Apply route guard and role-aware navigation [1d]
   |
   v
5. Render loading, error, or destination content [1d]
```

**Location ID: 1a**
- **Title:** Root layout
- **Description:** Top-level Next.js layout and providers.
- **Path:LineNumber:** app/frontend/src/app/layout.tsx:67

**Location ID: 1b**
- **Title:** Route guard
- **Description:** Client-side route eligibility and redirects.
- **Path:LineNumber:** app/frontend/src/components/eduboost/RouteGuard.tsx:30

**Location ID: 1c**
- **Title:** Server session loader
- **Description:** Server-side session interpretation.
- **Path:LineNumber:** app/frontend/src/lib/auth/session.server.ts:8

**Location ID: 1d**
- **Title:** Next.js middleware
- **Description:** Early navigation and route handling.
- **Path:LineNumber:** app/frontend/middleware.ts:29

### AI Guide: App Router shell, session boundary, and route guards

**Motivation:**
The frontend is the first enforcement and usability layer. It must guide users correctly without being treated as the sole security boundary.

**Details:**

**Reasoning through the execution path.** Start at [1a] and follow the ordered state transition rather than jumping directly to a downstream repository or generated artefact. The trace is designed to show which layer owns transport, orchestration, persistence, and evidence. [1a] anchors root layout. [1b] anchors route guard. [1c] anchors server session loader. [1d] anchors next.js middleware.

**Safe change boundary.** Session hints may be cached client-side, but authorization remains authoritative in the backend. A change that moves responsibility across these boundaries should update the owning codemap, tests, and any affected ADR or release verifier in the same change.

**Controls to preserve.** Route guards fail closed for protected screens, preserve return paths safely, and never expose private data during loading.

**How to verify the change.** Run routing, RouteGuard, entry-screen, and parent-dashboard tests across authenticated, expired, and unauthorized states. Use the cited locations as navigation anchors, then inspect call sites and tests before modifying behaviour.

## Trace ID: 2
**Title:** API client, offline queue, and service worker

**Description:** Maps typed client requests, backend proxying, offline persistence, replay, and PWA registration.

**Motivation:**
EduBoost targets intermittent-connectivity environments. Client flows must distinguish safe reads, replayable writes, and operations that require an online authoritative response.

**Details:**

**Execution path**

1. Build a typed API request with credentials and correlation metadata.
2. Send directly or through the Next.js backend proxy.
3. Classify network or application errors.
4. Persist eligible offline work in the local queue.
5. Register the service worker and monitor connectivity.
6. Replay queued work with idempotency and conflict handling.

**State and ownership boundaries**

IndexedDB and service-worker state are device-local caches; server state remains authoritative.

**Failure, privacy, and control points**

Sensitive payloads are minimized, replay is bounded and idempotent, and non-replayable actions fail visibly.

**Verification signals**

Run API client, offlineSync, cache, service-worker, and low-data-mode tests while toggling connectivity.

**Trace text diagram:**
```text
1. Build a typed API request with credentials and correlation metadata [2a]
   |
   v
2. Send directly or through the Next.js backend proxy [2b]
   |
   v
3. Classify network or application errors [2c]
   |
   v
4. Persist eligible offline work in the local queue [2d]
   |
   v
5. Register the service worker and monitor connectivity [2d]
   |
   v
6. Replay queued work with idempotency and conflict handling [2d]
```

**Location ID: 2a**
- **Title:** Typed API client
- **Description:** Canonical browser request implementation.
- **Path:LineNumber:** app/frontend/src/lib/api/client.ts:13

**Location ID: 2b**
- **Title:** Offline synchronization
- **Description:** Queueing and replay of eligible client operations.
- **Path:LineNumber:** app/frontend/src/lib/api/offlineSync.ts:7

**Location ID: 2c**
- **Title:** Backend proxy route
- **Description:** Server-side forwarding to the API.
- **Path:LineNumber:** app/frontend/src/app/api/backend/route.ts:1

**Location ID: 2d**
- **Title:** Service worker registration
- **Description:** PWA lifecycle integration.
- **Path:LineNumber:** app/frontend/src/components/ServiceWorkerRegistration.tsx:6

### AI Guide: API client, offline queue, and service worker

**Motivation:**
EduBoost targets intermittent-connectivity environments. Client flows must distinguish safe reads, replayable writes, and operations that require an online authoritative response.

**Details:**

**Reasoning through the execution path.** Start at [2a] and follow the ordered state transition rather than jumping directly to a downstream repository or generated artefact. The trace is designed to show which layer owns transport, orchestration, persistence, and evidence. [2a] anchors typed api client. [2b] anchors offline synchronization. [2c] anchors backend proxy route. [2d] anchors service worker registration.

**Safe change boundary.** IndexedDB and service-worker state are device-local caches; server state remains authoritative. A change that moves responsibility across these boundaries should update the owning codemap, tests, and any affected ADR or release verifier in the same change.

**Controls to preserve.** Sensitive payloads are minimized, replay is bounded and idempotent, and non-replayable actions fail visibly.

**How to verify the change.** Run API client, offlineSync, cache, service-worker, and low-data-mode tests while toggling connectivity. Use the cited locations as navigation anchors, then inspect call sites and tests before modifying behaviour.

## Trace ID: 3
**Title:** Learner, parent, tutor, and content-administration journeys

**Description:** Shows how feature pages compose reusable clients and panels for diagnostic, lesson, study-plan, parent, tutor, and content-factory work.

**Motivation:**
Application-wide codemaps must cover user-visible vertical journeys, not only framework plumbing. These pages are where domain contracts become observable product behaviour.

**Details:**

**Execution path**

1. Enter the learner or parent dashboard.
2. Load learner and consent-aware data.
3. Launch diagnostic, lesson, tutor, or plan interactions.
4. Persist progress and render trust or safety labels.
5. Expose parent review and privacy controls.
6. Allow authorized administrators to review and promote content.

**State and ownership boundaries**

View state is transient; learner progress, consent, generated content, and review decisions are persisted through backend contracts.

**Failure, privacy, and control points**

Every journey handles empty, loading, error, revoked-consent, and low-connectivity states.

**Verification signals**

Run learner journey, interactive diagnostic, tutor safety, parent review, content factory, accessibility, and PWA suites.

**Trace text diagram:**
```text
1. Enter the learner or parent dashboard [3a]
   |
   v
2. Load learner and consent-aware data [3b]
   |
   v
3. Launch diagnostic, lesson, tutor, or plan interactions [3c]
   |
   v
4. Persist progress and render trust or safety labels [3d]
   |
   v
5. Expose parent review and privacy controls [3d]
   |
   v
6. Allow authorized administrators to review and promote content [3d]
```

**Location ID: 3a**
- **Title:** Learner dashboard
- **Description:** Learner-facing orchestration surface.
- **Path:LineNumber:** app/frontend/src/components/learner/DashboardClient.tsx:25

**Location ID: 3b**
- **Title:** Interactive diagnostic
- **Description:** Diagnostic item and response flow.
- **Path:LineNumber:** app/frontend/src/components/eduboost/InteractiveDiagnostic.tsx:15

**Location ID: 3c**
- **Title:** Parent portal
- **Description:** Guardian progress and consent surface.
- **Path:LineNumber:** app/frontend/src/app/parent-portal/page.tsx:6

**Location ID: 3d**
- **Title:** Content administration
- **Description:** Review and promotion control surface.
- **Path:LineNumber:** app/frontend/src/components/admin/contentFactory/ContentFactoryLiveDashboard.tsx:32

### AI Guide: Learner, parent, tutor, and content-administration journeys

**Motivation:**
Application-wide codemaps must cover user-visible vertical journeys, not only framework plumbing. These pages are where domain contracts become observable product behaviour.

**Details:**

**Reasoning through the execution path.** Start at [3a] and follow the ordered state transition rather than jumping directly to a downstream repository or generated artefact. The trace is designed to show which layer owns transport, orchestration, persistence, and evidence. [3a] anchors learner dashboard. [3b] anchors interactive diagnostic. [3c] anchors parent portal. [3d] anchors content administration.

**Safe change boundary.** View state is transient; learner progress, consent, generated content, and review decisions are persisted through backend contracts. A change that moves responsibility across these boundaries should update the owning codemap, tests, and any affected ADR or release verifier in the same change.

**Controls to preserve.** Every journey handles empty, loading, error, revoked-consent, and low-connectivity states.

**How to verify the change.** Run learner journey, interactive diagnostic, tutor safety, parent review, content factory, accessibility, and PWA suites. Use the cited locations as navigation anchors, then inspect call sites and tests before modifying behaviour.

## Change checklist

- Update this codemap when an entry point, major dependency, persistence owner, or control flow changes.
- Keep all `Path:LineNumber` references repository-relative and line-valid.
- Update `codemap_coverage_manifest.json` when files move between architecture owners.
- Run `python scripts/maintenance/verify_codemaps.py --repo-root .` before merging.
