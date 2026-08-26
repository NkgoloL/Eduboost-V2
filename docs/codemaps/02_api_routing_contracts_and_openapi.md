# EduBoost V2 API Routing, Contracts, and OpenAPI

Maps router discovery, dependency injection, canonical envelopes, error semantics, OpenAPI generation, and contract drift controls.

## Scope and ownership

This codemap is the primary architecture owner for:
- `app/api_v2_routers`
- `app/api_v2_deps`
- `app/domain/api_v2_models.py`
- `openapi`
- `scripts/generate_openapi.py`

It describes current implementation paths in repository-relative form. Related cross-cutting behaviour may be referenced from other codemaps, but every maintained source file has one primary owner in `codemap_coverage_manifest.json`.

## Architectural position

This area participates in the wider EduBoost request, data, evidence, and release architecture. Read it together with `00_application_bootstrap_and_request_lifecycle.md`, `17_testing_ci_coverage_security_and_quality_gates.md`, and `18_production_readiness_release_evidence_and_live_traffic.md` when changing runtime or release-critical behaviour.

## Trace ID: 1
**Title:** Router registration and endpoint dispatch

**Description:** Follows an API request from prefix matching through router dispatch and dependency resolution.

**Motivation:**
Central router composition keeps public API surface, tags, prefixes, and compatibility aliases reviewable as one contract.

**Details:**

**Execution path**

1. Match `/api/v2` or `/v2` prefix.
2. Select the registered router and operation.
3. Resolve authentication, consent, repository, and service dependencies.
4. Validate request data with domain schemas.
5. Execute the endpoint and return an envelope.

**State and ownership boundaries**

Routers own transport concerns; business state transitions belong in services and repositories.

**Failure, privacy, and control points**

Endpoints avoid hidden globals, duplicate prefixes, and transport-specific business logic.

**Verification signals**

Compare registered routes with generated OpenAPI and run route-contract tests.

**Trace text diagram:**
```text
1. Match `/api/v2` or `/v2` prefix [1a]
   |
   v
2. Select the registered router and operation [1b]
   |
   v
3. Resolve authentication, consent, repository, and service dependencies [1c]
   |
   v
4. Validate request data with domain schemas [1d]
   |
   v
5. Execute the endpoint and return an envelope [1d]
```

**Location ID: 1a**
- **Title:** Router mounting
- **Description:** Application-level router composition.
- **Path:LineNumber:** app/api_v2.py:189

**Location ID: 1b**
- **Title:** API router root
- **Description:** Shared V2 router configuration.
- **Path:LineNumber:** app/api_v2_routers/api_v2.py:1

**Location ID: 1c**
- **Title:** Dependencies
- **Description:** Shared dependency providers.
- **Path:LineNumber:** app/core/dependencies.py:28

**Location ID: 1d**
- **Title:** API domain models
- **Description:** Validated request and response schemas.
- **Path:LineNumber:** app/domain/api_v2_models.py:19

### AI Guide: Router registration and endpoint dispatch

**Motivation:**
Central router composition keeps public API surface, tags, prefixes, and compatibility aliases reviewable as one contract.

**Details:**

**Reasoning through the execution path.** Start at [1a] and follow the ordered state transition rather than jumping directly to a downstream repository or generated artefact. The trace is designed to show which layer owns transport, orchestration, persistence, and evidence. [1a] anchors router mounting. [1b] anchors api router root. [1c] anchors dependencies. [1d] anchors api domain models.

**Safe change boundary.** Routers own transport concerns; business state transitions belong in services and repositories. A change that moves responsibility across these boundaries should update the owning codemap, tests, and any affected ADR or release verifier in the same change.

**Controls to preserve.** Endpoints avoid hidden globals, duplicate prefixes, and transport-specific business logic.

**How to verify the change.** Compare registered routes with generated OpenAPI and run route-contract tests. Use the cited locations as navigation anchors, then inspect call sites and tests before modifying behaviour.

## Trace ID: 2
**Title:** Dependency boundaries, envelope semantics, and errors

**Description:** Maps how endpoint dependencies establish actor and consent context and how exceptions become stable client-facing errors.

**Motivation:**
Stable errors and envelopes let the frontend distinguish authentication, validation, consent, conflict, and server failures without parsing ad hoc messages.

**Details:**

**Execution path**

1. Resolve actor and token state.
2. Resolve consent or domain repositories as required.
3. Invoke transport-independent service logic.
4. Raise typed domain or infrastructure exceptions.
5. Translate exceptions into canonical error envelopes.
6. Attach request and audit identifiers.

**State and ownership boundaries**

Dependency objects are request-scoped; error codes and response fields are versioned public contracts.

**Failure, privacy, and control points**

PII is excluded from messages, internal stack details are not exposed, and authorization failures are indistinguishable where enumeration risk exists.

**Verification signals**

Run API envelope, auth boundary, privacy boundary, and generated-client contract tests.

**Trace text diagram:**
```text
1. Resolve actor and token state [2a]
   |
   v
2. Resolve consent or domain repositories as required [2b]
   |
   v
3. Invoke transport-independent service logic [2c]
   |
   v
4. Raise typed domain or infrastructure exceptions [2d]
   |
   v
5. Translate exceptions into canonical error envelopes [2d]
   |
   v
6. Attach request and audit identifiers [2d]
```

**Location ID: 2a**
- **Title:** Authentication dependency
- **Description:** Actor resolution at endpoint entry.
- **Path:LineNumber:** app/api_v2_deps/auth.py:58

**Location ID: 2b**
- **Title:** Consent dependency
- **Description:** Consent enforcement at route entry.
- **Path:LineNumber:** app/api_v2_deps/consent_lifecycle.py:15

**Location ID: 2c**
- **Title:** Envelope translator
- **Description:** Stable API output shape.
- **Path:LineNumber:** app/core/envelope_route.py:4

**Location ID: 2d**
- **Title:** Typed failures
- **Description:** Domain-to-HTTP failure taxonomy.
- **Path:LineNumber:** app/core/exceptions.py:23

### AI Guide: Dependency boundaries, envelope semantics, and errors

**Motivation:**
Stable errors and envelopes let the frontend distinguish authentication, validation, consent, conflict, and server failures without parsing ad hoc messages.

**Details:**

**Reasoning through the execution path.** Start at [2a] and follow the ordered state transition rather than jumping directly to a downstream repository or generated artefact. The trace is designed to show which layer owns transport, orchestration, persistence, and evidence. [2a] anchors authentication dependency. [2b] anchors consent dependency. [2c] anchors envelope translator. [2d] anchors typed failures.

**Safe change boundary.** Dependency objects are request-scoped; error codes and response fields are versioned public contracts. A change that moves responsibility across these boundaries should update the owning codemap, tests, and any affected ADR or release verifier in the same change.

**Controls to preserve.** PII is excluded from messages, internal stack details are not exposed, and authorization failures are indistinguishable where enumeration risk exists.

**How to verify the change.** Run API envelope, auth boundary, privacy boundary, and generated-client contract tests. Use the cited locations as navigation anchors, then inspect call sites and tests before modifying behaviour.

## Trace ID: 3
**Title:** OpenAPI generation, canonicalization, and drift gates

**Description:** Shows how the runtime schema is generated, normalized, stored, and checked against frontend and CI expectations.

**Motivation:**
OpenAPI is an executable interface contract. Generated artefacts must be reproducible so route changes cannot bypass review or leave the frontend stale.

**Details:**

**Execution path**

1. Import the canonical application in a controlled environment.
2. Generate the OpenAPI schema.
3. Normalize nondeterministic ordering or metadata.
4. Write the canonical generated artifact.
5. Compare it with committed authority.
6. Run route and frontend contract gates.

**State and ownership boundaries**

The committed schema is generated evidence; Python schemas and router declarations remain the implementation authority.

**Failure, privacy, and control points**

Generation is deterministic, test-only routes are excluded as intended, and drift fails CI.

**Verification signals**

Run OpenAPI generation twice, compare hashes, and execute openapi-contract, openapi-drift, and frontend contract workflows.

**Trace text diagram:**
```text
1. Import the canonical application in a controlled environment [3a]
   |
   v
2. Generate the OpenAPI schema [3b]
   |
   v
3. Normalize nondeterministic ordering or metadata [3c]
   |
   v
4. Write the canonical generated artifact [3d]
   |
   v
5. Compare it with committed authority [3d]
   |
   v
6. Run route and frontend contract gates [3d]
```

**Location ID: 3a**
- **Title:** OpenAPI generator
- **Description:** Canonical schema generation command.
- **Path:LineNumber:** scripts/generate_openapi.py:103

**Location ID: 3b**
- **Title:** OpenAPI dumper
- **Description:** Runtime schema serialization.
- **Path:LineNumber:** scripts/dump_openapi.py:16

**Location ID: 3c**
- **Title:** OpenAPI contract workflow
- **Description:** Hosted contract verification.
- **Path:LineNumber:** .github/workflows/openapi-contract.yml:6

**Location ID: 3d**
- **Title:** OpenAPI drift workflow
- **Description:** Generated artifact drift gate.
- **Path:LineNumber:** .github/workflows/openapi-drift.yml:1

### AI Guide: OpenAPI generation, canonicalization, and drift gates

**Motivation:**
OpenAPI is an executable interface contract. Generated artefacts must be reproducible so route changes cannot bypass review or leave the frontend stale.

**Details:**

**Reasoning through the execution path.** Start at [3a] and follow the ordered state transition rather than jumping directly to a downstream repository or generated artefact. The trace is designed to show which layer owns transport, orchestration, persistence, and evidence. [3a] anchors openapi generator. [3b] anchors openapi dumper. [3c] anchors openapi contract workflow. [3d] anchors openapi drift workflow.

**Safe change boundary.** The committed schema is generated evidence; Python schemas and router declarations remain the implementation authority. A change that moves responsibility across these boundaries should update the owning codemap, tests, and any affected ADR or release verifier in the same change.

**Controls to preserve.** Generation is deterministic, test-only routes are excluded as intended, and drift fails CI.

**How to verify the change.** Run OpenAPI generation twice, compare hashes, and execute openapi-contract, openapi-drift, and frontend contract workflows. Use the cited locations as navigation anchors, then inspect call sites and tests before modifying behaviour.

## Change checklist

- Update this codemap when an entry point, major dependency, persistence owner, or control flow changes.
- Keep all `Path:LineNumber` references repository-relative and line-valid.
- Update `codemap_coverage_manifest.json` when files move between architecture owners.
- Run `python scripts/maintenance/verify_codemaps.py --repo-root .` before merging.
