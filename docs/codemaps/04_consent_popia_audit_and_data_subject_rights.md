# EduBoost V2 Consent, POPIA, Audit, and Data Subject Rights

Maps versioned consent, request-time enforcement, audit evidence, export, correction, objection, erasure, and privacy operations.

## Scope and ownership

This codemap is the primary architecture owner for:
- `app/api_v2_routers/consent*.py`
- `app/api_v2_routers/popia.py`
- `app/api_v2_routers/privacy_operations.py`
- `app/services/consent*`
- `app/services/data_subject_rights_service.py`
- `app/services/audit*`

It describes current implementation paths in repository-relative form. Related cross-cutting behaviour may be referenced from other codemaps, but every maintained source file has one primary owner in `codemap_coverage_manifest.json`.

## Architectural position

This area participates in the wider EduBoost request, data, evidence, and release architecture. Read it together with `00_application_bootstrap_and_request_lifecycle.md`, `17_testing_ci_coverage_security_and_quality_gates.md`, and `18_production_readiness_release_evidence_and_live_traffic.md` when changing runtime or release-critical behaviour.

## Trace ID: 1
**Title:** Consent capture, versioning, renewal, and expiry

**Description:** Follows consent from policy version selection through capture, persistence, renewal, and expiry handling.

**Motivation:**
Consent for learner data and AI-assisted experiences must be provable, versioned, revocable, and enforceable.

**Details:**

**Execution path**

1. Resolve the current policy and required consent purposes.
2. Capture guardian or eligible user decision.
3. Validate authority, scope, and policy version.
4. Persist consent and immutable audit event.
5. Schedule or evaluate renewal and expiry.
6. Expose current consent status to authorized clients.

**State and ownership boundaries**

Consent records, policy versions, and audit events are distinct persisted records linked by identifiers.

**Failure, privacy, and control points**

Consent cannot be backdated silently, expired consent is not treated as active, and policy changes trigger explicit renewal rules.

**Verification signals**

Run consent lifecycle, renewal, expiry, policy-version, and POPIA contract tests.

**Trace text diagram:**
```text
1. Resolve the current policy and required consent purposes [1a]
   |
   v
2. Capture guardian or eligible user decision [1b]
   |
   v
3. Validate authority, scope, and policy version [1c]
   |
   v
4. Persist consent and immutable audit event [1d]
   |
   v
5. Schedule or evaluate renewal and expiry [1d]
   |
   v
6. Expose current consent status to authorized clients [1d]
```

**Location ID: 1a**
- **Title:** Consent routes
- **Description:** Capture and query transport boundary.
- **Path:LineNumber:** app/api_v2_routers/consent.py:38

**Location ID: 1b**
- **Title:** Consent orchestrator
- **Description:** Runtime lifecycle coordination.
- **Path:LineNumber:** app/services/consent_runtime_orchestrator.py:14

**Location ID: 1c**
- **Title:** Renewal service
- **Description:** Consent renewal transitions.
- **Path:LineNumber:** app/services/consent_renewal_service.py:28

**Location ID: 1d**
- **Title:** Consent repository
- **Description:** Persistent consent authority.
- **Path:LineNumber:** app/repositories/consent_repository.py:16

### AI Guide: Consent capture, versioning, renewal, and expiry

**Motivation:**
Consent for learner data and AI-assisted experiences must be provable, versioned, revocable, and enforceable.

**Details:**

**Reasoning through the execution path.** Start at [1a] and follow the ordered state transition rather than jumping directly to a downstream repository or generated artefact. The trace is designed to show which layer owns transport, orchestration, persistence, and evidence. [1a] anchors consent routes. [1b] anchors consent orchestrator. [1c] anchors renewal service. [1d] anchors consent repository.

**Safe change boundary.** Consent records, policy versions, and audit events are distinct persisted records linked by identifiers. A change that moves responsibility across these boundaries should update the owning codemap, tests, and any affected ADR or release verifier in the same change.

**Controls to preserve.** Consent cannot be backdated silently, expired consent is not treated as active, and policy changes trigger explicit renewal rules.

**How to verify the change.** Run consent lifecycle, renewal, expiry, policy-version, and POPIA contract tests. Use the cited locations as navigation anchors, then inspect call sites and tests before modifying behaviour.

## Trace ID: 2
**Title:** Request-time consent gate and audit evidence

**Description:** Maps active-consent evaluation before protected services execute and the evidence written for sensitive actions.

**Motivation:**
Consent is useful only when enforced at the same boundary as data processing, generation, and disclosure.

**Details:**

**Execution path**

1. Authenticate actor and resolve learner context.
2. Determine required purposes for the requested operation.
3. Load active consent and compatible policy version.
4. Deny, degrade, or allow the operation.
5. Write canonical audit evidence with actor, purpose, and outcome.
6. Return privacy-safe response metadata.

**State and ownership boundaries**

Consent checks are evaluated from persisted authority; audit events are append-oriented evidence, not mutable application state.

**Failure, privacy, and control points**

All protected paths use the same policy semantics, denials avoid leaking learner existence, and audit canonicalization strips secrets.

**Verification signals**

Run privacy-boundary, consent-gate, audit-write, and route-contract tests.

**Trace text diagram:**
```text
1. Authenticate actor and resolve learner context [2a]
   |
   v
2. Determine required purposes for the requested operation [2b]
   |
   v
3. Load active consent and compatible policy version [2c]
   |
   v
4. Deny, degrade, or allow the operation [2d]
   |
   v
5. Write canonical audit evidence with actor, purpose, and outcome [2d]
   |
   v
6. Return privacy-safe response metadata [2d]
```

**Location ID: 2a**
- **Title:** Consent gate
- **Description:** Request-time allow/deny boundary.
- **Path:LineNumber:** app/core/consent_gate.py:8

**Location ID: 2b**
- **Title:** Consent policy
- **Description:** Purpose and policy compatibility rules.
- **Path:LineNumber:** app/core/consent_policy.py:16

**Location ID: 2c**
- **Title:** Audit service
- **Description:** Canonical audit event creation.
- **Path:LineNumber:** app/services/audit_service.py:9

**Location ID: 2d**
- **Title:** Audit persistence
- **Description:** Append and query audit records.
- **Path:LineNumber:** app/repositories/audit_repository.py:27

### AI Guide: Request-time consent gate and audit evidence

**Motivation:**
Consent is useful only when enforced at the same boundary as data processing, generation, and disclosure.

**Details:**

**Reasoning through the execution path.** Start at [2a] and follow the ordered state transition rather than jumping directly to a downstream repository or generated artefact. The trace is designed to show which layer owns transport, orchestration, persistence, and evidence. [2a] anchors consent gate. [2b] anchors consent policy. [2c] anchors audit service. [2d] anchors audit persistence.

**Safe change boundary.** Consent checks are evaluated from persisted authority; audit events are append-oriented evidence, not mutable application state. A change that moves responsibility across these boundaries should update the owning codemap, tests, and any affected ADR or release verifier in the same change.

**Controls to preserve.** All protected paths use the same policy semantics, denials avoid leaking learner existence, and audit canonicalization strips secrets.

**How to verify the change.** Run privacy-boundary, consent-gate, audit-write, and route-contract tests. Use the cited locations as navigation anchors, then inspect call sites and tests before modifying behaviour.

## Trace ID: 3
**Title:** Data subject requests and erasure orchestration

**Description:** Shows export, access, correction, objection, restriction, and erasure requests from intake to evidence.

**Motivation:**
POPIA rights require controlled workflows that find all relevant data while preserving legal and operational evidence.

**Details:**

**Execution path**

1. Accept and authenticate a data-subject request.
2. Verify requester authority and target learner.
3. Create a tracked privacy operation.
4. Discover database, object, cache, and KG targets.
5. Export, correct, restrict, anonymize, or erase as applicable.
6. Record completion, exceptions, and retained evidence.

**State and ownership boundaries**

Request records and evidence are retained according to policy even when operational learner data is erased.

**Failure, privacy, and control points**

Erasure is idempotent, cross-store targets are explicit, legal holds are respected, and generated artefacts containing PII are included.

**Verification signals**

Run DSR service, privacy operations, erasure cascade, audit, and live-data assurance tests.

**Trace text diagram:**
```text
1. Accept and authenticate a data-subject request [3a]
   |
   v
2. Verify requester authority and target learner [3b]
   |
   v
3. Create a tracked privacy operation [3c]
   |
   v
4. Discover database, object, cache, and KG targets [3d]
   |
   v
5. Export, correct, restrict, anonymize, or erase as applicable [3d]
   |
   v
6. Record completion, exceptions, and retained evidence [3d]
```

**Location ID: 3a**
- **Title:** POPIA routes
- **Description:** Data-subject request endpoints.
- **Path:LineNumber:** app/api_v2_routers/popia.py:102

**Location ID: 3b**
- **Title:** Privacy operations routes
- **Description:** Operational privacy control plane.
- **Path:LineNumber:** app/api_v2_routers/privacy_operations.py:13

**Location ID: 3c**
- **Title:** DSR service
- **Description:** Rights workflow orchestration.
- **Path:LineNumber:** app/services/data_subject_rights_service.py:42

**Location ID: 3d**
- **Title:** Privacy assurance
- **Description:** Live-data privacy controls and evidence.
- **Path:LineNumber:** app/modules/privacy_ops/assurance.py:33

### AI Guide: Data subject requests and erasure orchestration

**Motivation:**
POPIA rights require controlled workflows that find all relevant data while preserving legal and operational evidence.

**Details:**

**Reasoning through the execution path.** Start at [3a] and follow the ordered state transition rather than jumping directly to a downstream repository or generated artefact. The trace is designed to show which layer owns transport, orchestration, persistence, and evidence. [3a] anchors popia routes. [3b] anchors privacy operations routes. [3c] anchors dsr service. [3d] anchors privacy assurance.

**Safe change boundary.** Request records and evidence are retained according to policy even when operational learner data is erased. A change that moves responsibility across these boundaries should update the owning codemap, tests, and any affected ADR or release verifier in the same change.

**Controls to preserve.** Erasure is idempotent, cross-store targets are explicit, legal holds are respected, and generated artefacts containing PII are included.

**How to verify the change.** Run DSR service, privacy operations, erasure cascade, audit, and live-data assurance tests. Use the cited locations as navigation anchors, then inspect call sites and tests before modifying behaviour.

## Change checklist

- Update this codemap when an entry point, major dependency, persistence owner, or control flow changes.
- Keep all `Path:LineNumber` references repository-relative and line-valid.
- Update `codemap_coverage_manifest.json` when files move between architecture owners.
- Run `python scripts/maintenance/verify_codemaps.py --repo-root .` before merging.
