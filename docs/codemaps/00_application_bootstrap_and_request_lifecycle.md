# EduBoost V2 Application Bootstrap and Request Lifecycle

Maps process startup, FastAPI composition, request middleware, response envelopes, readiness checks, and graceful shutdown for the canonical V2 backend.

## Scope and ownership

This codemap is the primary architecture owner for:
- `app/api_v2.py`
- `app/core`
- `app/middleware`
- `app/api_v2_routers/system.py`

It describes current implementation paths in repository-relative form. Related cross-cutting behaviour may be referenced from other codemaps, but every maintained source file has one primary owner in `codemap_coverage_manifest.json`.

## Architectural position

This area participates in the wider EduBoost request, data, evidence, and release architecture. Read it together with `00_application_bootstrap_and_request_lifecycle.md`, `17_testing_ci_coverage_security_and_quality_gates.md`, and `18_production_readiness_release_evidence_and_live_traffic.md` when changing runtime or release-critical behaviour.

## Trace ID: 1
**Title:** Canonical FastAPI startup and router composition

**Description:** Follows application construction from lifespan entry through middleware setup and dual-prefix router registration.

**Motivation:**
The application bootstrap is the root of every backend execution path. A correct map prevents changes to startup ordering, route prefixes, or dependency initialization from silently splitting runtime behaviour.

**Details:**

**Execution path**

1. Enter the FastAPI lifespan context and initialize runtime dependencies.
2. Create the FastAPI application with canonical OpenAPI metadata.
3. Install security, tracing, rate-limit, and envelope middleware.
4. Register every API router under the supported V2 prefixes.
5. Publish startup state and unwind resources during shutdown.

**State and ownership boundaries**

Startup state is process-scoped; database, Redis, provider, and worker readiness must not leak between test and production modes.

**Failure, privacy, and control points**

Router registration is centralized, startup failures are surfaced instead of hidden, and degraded-mode behaviour remains explicit.

**Verification signals**

Run application import/startup tests, dump the OpenAPI document, and probe `/health`, `/ready`, and both V2 route prefixes.

**Trace text diagram:**
```text
1. Enter the FastAPI lifespan context and initialize runtime dependencies [1a]
   |
   v
2. Create the FastAPI application with canonical OpenAPI metadata [1b]
   |
   v
3. Install security, tracing, rate-limit, and envelope middleware [1c]
   |
   v
4. Register every API router under the supported V2 prefixes [1d]
   |
   v
5. Publish startup state and unwind resources during shutdown [1d]
```

**Location ID: 1a**
- **Title:** Lifespan entry
- **Description:** Canonical startup and shutdown context.
- **Path:LineNumber:** app/api_v2.py:68

**Location ID: 1b**
- **Title:** FastAPI construction
- **Description:** Application object and API metadata.
- **Path:LineNumber:** app/api_v2.py:117

**Location ID: 1c**
- **Title:** Router registry
- **Description:** Central list of routers mounted by the application.
- **Path:LineNumber:** app/api_v2.py:189

**Location ID: 1d**
- **Title:** Dual V2 prefixes
- **Description:** Supported API prefix compatibility contract.
- **Path:LineNumber:** app/api_v2.py:188

### AI Guide: Canonical FastAPI startup and router composition

**Motivation:**
The application bootstrap is the root of every backend execution path. A correct map prevents changes to startup ordering, route prefixes, or dependency initialization from silently splitting runtime behaviour.

**Details:**

**Reasoning through the execution path.** Start at [1a] and follow the ordered state transition rather than jumping directly to a downstream repository or generated artefact. The trace is designed to show which layer owns transport, orchestration, persistence, and evidence. [1a] anchors lifespan entry. [1b] anchors fastapi construction. [1c] anchors router registry. [1d] anchors dual v2 prefixes.

**Safe change boundary.** Startup state is process-scoped; database, Redis, provider, and worker readiness must not leak between test and production modes. A change that moves responsibility across these boundaries should update the owning codemap, tests, and any affected ADR or release verifier in the same change.

**Controls to preserve.** Router registration is centralized, startup failures are surfaced instead of hidden, and degraded-mode behaviour remains explicit.

**How to verify the change.** Run application import/startup tests, dump the OpenAPI document, and probe `/health`, `/ready`, and both V2 route prefixes. Use the cited locations as navigation anchors, then inspect call sites and tests before modifying behaviour.

## Trace ID: 2
**Title:** Request middleware, context, and response envelope

**Description:** Shows how an inbound HTTP request gains correlation context, security controls, metrics, and the canonical API response shape.

**Motivation:**
Cross-cutting request behaviour must be consistent across all routers so observability, security, and client error handling do not depend on endpoint-specific implementation.

**Details:**

**Execution path**

1. Accept request at the ASGI boundary.
2. Attach request and correlation context.
3. Apply security headers, rate limiting, and structured logging.
4. Dispatch to the selected route handler.
5. Normalize success or error output into the response envelope.
6. Emit latency and outcome metrics.

**State and ownership boundaries**

Request identifiers and actor context are request-local; response envelopes are public contracts consumed by the frontend and generated clients.

**Failure, privacy, and control points**

Middleware ordering preserves exception visibility, avoids double wrapping, and keeps sensitive values out of logs.

**Verification signals**

Exercise envelope contract tests and verify headers, request IDs, status codes, and structured error payloads.

**Trace text diagram:**
```text
1. Accept request at the ASGI boundary [2a]
   |
   v
2. Attach request and correlation context [2b]
   |
   v
3. Apply security headers, rate limiting, and structured logging [2c]
   |
   v
4. Dispatch to the selected route handler [2d]
   |
   v
5. Normalize success or error output into the response envelope [2d]
   |
   v
6. Emit latency and outcome metrics [2d]
```

**Location ID: 2a**
- **Title:** Middleware implementation
- **Description:** Cross-cutting ASGI request processing.
- **Path:LineNumber:** app/core/middleware.py:22

**Location ID: 2b**
- **Title:** Request context
- **Description:** Request-local identity and correlation state.
- **Path:LineNumber:** app/core/context.py:2

**Location ID: 2c**
- **Title:** Envelope route
- **Description:** Canonical success and error response normalization.
- **Path:LineNumber:** app/core/envelope_route.py:4

**Location ID: 2d**
- **Title:** Application exceptions
- **Description:** Typed exceptions translated at the API boundary.
- **Path:LineNumber:** app/core/exceptions.py:23

### AI Guide: Request middleware, context, and response envelope

**Motivation:**
Cross-cutting request behaviour must be consistent across all routers so observability, security, and client error handling do not depend on endpoint-specific implementation.

**Details:**

**Reasoning through the execution path.** Start at [2a] and follow the ordered state transition rather than jumping directly to a downstream repository or generated artefact. The trace is designed to show which layer owns transport, orchestration, persistence, and evidence. [2a] anchors middleware implementation. [2b] anchors request context. [2c] anchors envelope route. [2d] anchors application exceptions.

**Safe change boundary.** Request identifiers and actor context are request-local; response envelopes are public contracts consumed by the frontend and generated clients. A change that moves responsibility across these boundaries should update the owning codemap, tests, and any affected ADR or release verifier in the same change.

**Controls to preserve.** Middleware ordering preserves exception visibility, avoids double wrapping, and keeps sensitive values out of logs.

**How to verify the change.** Exercise envelope contract tests and verify headers, request IDs, status codes, and structured error payloads. Use the cited locations as navigation anchors, then inspect call sites and tests before modifying behaviour.

## Trace ID: 3
**Title:** Health, readiness, degraded mode, and shutdown

**Description:** Maps the distinction between liveness, dependency readiness, deep readiness, and controlled degradation.

**Motivation:**
Deployment systems need truthful health signals. Conflating process liveness with database, Redis, migration, or provider readiness can route learner traffic to an unsafe runtime.

**Details:**

**Execution path**

1. Receive health or readiness probe.
2. Evaluate process liveness independently of downstream dependencies.
3. Check database, migration, cache, and service readiness.
4. Return degraded or not-ready state with evidence.
5. Allow orchestration to drain or restart the instance.
6. Close resources through lifespan shutdown.

**State and ownership boundaries**

Readiness snapshots are evidence about current dependency state, not a substitute for persistent release evidence.

**Failure, privacy, and control points**

Deep probes remain bounded, no probe mutates learner data, and degraded mode is never reported as fully ready.

**Verification signals**

Run health contract tests and deployment probe checks with healthy, unavailable, and partially degraded dependencies.

**Trace text diagram:**
```text
1. Receive health or readiness probe [3a]
   |
   v
2. Evaluate process liveness independently of downstream dependencies [3b]
   |
   v
3. Check database, migration, cache, and service readiness [3c]
   |
   v
4. Return degraded or not-ready state with evidence [3d]
   |
   v
5. Allow orchestration to drain or restart the instance [3d]
   |
   v
6. Close resources through lifespan shutdown [3d]
```

**Location ID: 3a**
- **Title:** Health checks
- **Description:** Dependency and application health evaluation.
- **Path:LineNumber:** app/core/health.py:18

**Location ID: 3b**
- **Title:** Runtime readiness
- **Description:** Canonical readiness aggregation.
- **Path:LineNumber:** app/core/runtime_readiness.py:61

**Location ID: 3c**
- **Title:** Degraded mode
- **Description:** Explicit reduced-capability runtime state.
- **Path:LineNumber:** app/core/degraded_mode.py:20

**Location ID: 3d**
- **Title:** System routes
- **Description:** Public health and system endpoints.
- **Path:LineNumber:** app/api_v2_routers/system.py:9

### AI Guide: Health, readiness, degraded mode, and shutdown

**Motivation:**
Deployment systems need truthful health signals. Conflating process liveness with database, Redis, migration, or provider readiness can route learner traffic to an unsafe runtime.

**Details:**

**Reasoning through the execution path.** Start at [3a] and follow the ordered state transition rather than jumping directly to a downstream repository or generated artefact. The trace is designed to show which layer owns transport, orchestration, persistence, and evidence. [3a] anchors health checks. [3b] anchors runtime readiness. [3c] anchors degraded mode. [3d] anchors system routes.

**Safe change boundary.** Readiness snapshots are evidence about current dependency state, not a substitute for persistent release evidence. A change that moves responsibility across these boundaries should update the owning codemap, tests, and any affected ADR or release verifier in the same change.

**Controls to preserve.** Deep probes remain bounded, no probe mutates learner data, and degraded mode is never reported as fully ready.

**How to verify the change.** Run health contract tests and deployment probe checks with healthy, unavailable, and partially degraded dependencies. Use the cited locations as navigation anchors, then inspect call sites and tests before modifying behaviour.

## Change checklist

- Update this codemap when an entry point, major dependency, persistence owner, or control flow changes.
- Keep all `Path:LineNumber` references repository-relative and line-valid.
- Update `codemap_coverage_manifest.json` when files move between architecture owners.
- Run `python scripts/maintenance/verify_codemaps.py --repo-root .` before merging.
