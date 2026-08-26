# EduBoost V2 Diagnostics, IRT, Item Bank, and Mastery

Maps diagnostic session lifecycle, adaptive item selection, transactional responses, IRT scoring, item calibration, quality controls, and mastery projection.

## Scope and ownership

This codemap is the primary architecture owner for:
- `app/api_v2_routers/diagnostics.py`
- `app/modules/diagnostics`
- `app/services/diagnostic*`
- `app/repositories/*diagnostic*`
- `app/repositories/irt_repository.py`

It describes current implementation paths in repository-relative form. Related cross-cutting behaviour may be referenced from other codemaps, but every maintained source file has one primary owner in `codemap_coverage_manifest.json`.

## Architectural position

This area participates in the wider EduBoost request, data, evidence, and release architecture. Read it together with `00_application_bootstrap_and_request_lifecycle.md`, `17_testing_ci_coverage_security_and_quality_gates.md`, and `18_production_readiness_release_evidence_and_live_traffic.md` when changing runtime or release-critical behaviour.

## Trace ID: 1
**Title:** Diagnostic session start, resume, and adaptive item selection

**Description:** Follows learner eligibility through session creation, recovery, and selection of the next valid item.

**Motivation:**
Adaptive diagnostics must be reproducible enough to audit while still selecting informative items for each learner.

**Details:**

**Execution path**

1. Authorize learner and verify active consent.
2. Create or recover an open diagnostic session.
3. Load calibrated item-bank candidates.
4. Apply curriculum, exposure, safety, and eligibility filters.
5. Rank candidates by information and coverage need.
6. Persist selection and return the next item.

**State and ownership boundaries**

Session, exposure, item-bank, and learner estimate state are persisted separately to support recovery and analysis.

**Failure, privacy, and control points**

Already exposed or invalid items are excluded, concurrent requests cannot advance twice, and empty candidate pools terminate safely.

**Verification signals**

Run session recovery, item selection, exposure, integrity, and diagnostic route tests.

**Trace text diagram:**
```text
1. Authorize learner and verify active consent [1a]
   |
   v
2. Create or recover an open diagnostic session [1b]
   |
   v
3. Load calibrated item-bank candidates [1c]
   |
   v
4. Apply curriculum, exposure, safety, and eligibility filters [1d]
   |
   v
5. Rank candidates by information and coverage need [1d]
   |
   v
6. Persist selection and return the next item [1d]
```

**Location ID: 1a**
- **Title:** Diagnostics routes
- **Description:** Diagnostic transport boundary.
- **Path:LineNumber:** app/api_v2_routers/diagnostics.py:50

**Location ID: 1b**
- **Title:** Session service
- **Description:** Diagnostic state machine.
- **Path:LineNumber:** app/modules/diagnostics/diagnostic_session_service.py:17

**Location ID: 1c**
- **Title:** Item selection
- **Description:** Adaptive candidate ranking.
- **Path:LineNumber:** app/modules/diagnostics/item_selection_service.py:10

**Location ID: 1d**
- **Title:** Session repository
- **Description:** Persistent diagnostic sessions.
- **Path:LineNumber:** app/repositories/diagnostic_session_repository.py:12

### AI Guide: Diagnostic session start, resume, and adaptive item selection

**Motivation:**
Adaptive diagnostics must be reproducible enough to audit while still selecting informative items for each learner.

**Details:**

**Reasoning through the execution path.** Start at [1a] and follow the ordered state transition rather than jumping directly to a downstream repository or generated artefact. The trace is designed to show which layer owns transport, orchestration, persistence, and evidence. [1a] anchors diagnostics routes. [1b] anchors session service. [1c] anchors item selection. [1d] anchors session repository.

**Safe change boundary.** Session, exposure, item-bank, and learner estimate state are persisted separately to support recovery and analysis. A change that moves responsibility across these boundaries should update the owning codemap, tests, and any affected ADR or release verifier in the same change.

**Controls to preserve.** Already exposed or invalid items are excluded, concurrent requests cannot advance twice, and empty candidate pools terminate safely.

**How to verify the change.** Run session recovery, item selection, exposure, integrity, and diagnostic route tests. Use the cited locations as navigation anchors, then inspect call sites and tests before modifying behaviour.

## Trace ID: 2
**Title:** Transactional response, scoring, and termination

**Description:** Maps answer submission through idempotent persistence, IRT update, mastery evidence, and stop-rule evaluation.

**Motivation:**
Response processing changes learner state and therefore must be atomic, retry-safe, and explainable.

**Details:**

**Execution path**

1. Validate response against current selected item.
2. Open a transaction and reject duplicate or stale submissions.
3. Score the response and capture timing metadata.
4. Update ability estimate and uncertainty.
5. Write mastery or knowledge-gap evidence.
6. Evaluate termination and commit the next session state.

**State and ownership boundaries**

Raw responses, scores, ability snapshots, and mastery projections remain linked but independently auditable.

**Failure, privacy, and control points**

Duplicate submissions are idempotent, answer keys are protected, scoring failures roll back, and termination cannot skip required coverage.

**Verification signals**

Run transactional response, scoring snapshot, termination, concurrency, and mastery tests.

**Trace text diagram:**
```text
1. Validate response against current selected item [2a]
   |
   v
2. Open a transaction and reject duplicate or stale submissions [2b]
   |
   v
3. Score the response and capture timing metadata [2c]
   |
   v
4. Update ability estimate and uncertainty [2d]
   |
   v
5. Write mastery or knowledge-gap evidence [2d]
   |
   v
6. Evaluate termination and commit the next session state [2d]
```

**Location ID: 2a**
- **Title:** Transactional response
- **Description:** Atomic answer processing.
- **Path:LineNumber:** app/services/diagnostic_transactional_response.py:10

**Location ID: 2b**
- **Title:** IRT engine
- **Description:** Ability estimation and information functions.
- **Path:LineNumber:** app/modules/diagnostics/irt_engine.py:52

**Location ID: 2c**
- **Title:** Termination service
- **Description:** Stop-rule evaluation.
- **Path:LineNumber:** app/modules/diagnostics/termination_service.py:7

**Location ID: 2d**
- **Title:** Mastery repository
- **Description:** Persisted mastery evidence.
- **Path:LineNumber:** app/repositories/mastery_repository.py:12

### AI Guide: Transactional response, scoring, and termination

**Motivation:**
Response processing changes learner state and therefore must be atomic, retry-safe, and explainable.

**Details:**

**Reasoning through the execution path.** Start at [2a] and follow the ordered state transition rather than jumping directly to a downstream repository or generated artefact. The trace is designed to show which layer owns transport, orchestration, persistence, and evidence. [2a] anchors transactional response. [2b] anchors irt engine. [2c] anchors termination service. [2d] anchors mastery repository.

**Safe change boundary.** Raw responses, scores, ability snapshots, and mastery projections remain linked but independently auditable. A change that moves responsibility across these boundaries should update the owning codemap, tests, and any affected ADR or release verifier in the same change.

**Controls to preserve.** Duplicate submissions are idempotent, answer keys are protected, scoring failures roll back, and termination cannot skip required coverage.

**How to verify the change.** Run transactional response, scoring snapshot, termination, concurrency, and mastery tests. Use the cited locations as navigation anchors, then inspect call sites and tests before modifying behaviour.

## Trace ID: 3
**Title:** Item generation, calibration, quality, and graph projection

**Description:** Shows the lifecycle from generated or curated items through validation, calibration, quality review, and runtime KG projection.

**Motivation:**
Adaptive quality depends on both educational validity and statistically defensible item parameters.

**Details:**

**Execution path**

1. Generate or ingest item candidates.
2. Validate schema, answer key, curriculum mapping, and safety.
3. Seed or estimate IRT parameters.
4. Collect response evidence and run calibration.
5. Review bias, quality, and exposure metrics.
6. Project accepted evidence into learner and curriculum graph state.

**State and ownership boundaries**

Draft items, approved items, IRT parameters, calibration evidence, and graph projections have explicit statuses.

**Failure, privacy, and control points**

Uncalibrated items are bounded, quality gates prevent silent promotion, and graph projections retain source evidence.

**Verification signals**

Run item-bank pipeline, calibration, IRT quality, bias review, and runtime KG diagnostic projection tests.

**Trace text diagram:**
```text
1. Generate or ingest item candidates [3a]
   |
   v
2. Validate schema, answer key, curriculum mapping, and safety [3b]
   |
   v
3. Seed or estimate IRT parameters [3c]
   |
   v
4. Collect response evidence and run calibration [3d]
   |
   v
5. Review bias, quality, and exposure metrics [3d]
   |
   v
6. Project accepted evidence into learner and curriculum graph state [3d]
```

**Location ID: 3a**
- **Title:** Item-bank pipeline
- **Description:** Generation-to-approval lifecycle.
- **Path:LineNumber:** app/modules/diagnostics/item_bank_pipeline.py:73

**Location ID: 3b**
- **Title:** Calibration service
- **Description:** IRT parameter estimation.
- **Path:LineNumber:** app/modules/diagnostics/calibration_service.py:8

**Location ID: 3c**
- **Title:** IRT quality service
- **Description:** Quality and bias evidence.
- **Path:LineNumber:** app/services/irt_quality_service.py:40

**Location ID: 3d**
- **Title:** KG diagnostic projection
- **Description:** Route-to-graph integration.
- **Path:LineNumber:** app/services/runtime_kg/route_integration.py:5

### AI Guide: Item generation, calibration, quality, and graph projection

**Motivation:**
Adaptive quality depends on both educational validity and statistically defensible item parameters.

**Details:**

**Reasoning through the execution path.** Start at [3a] and follow the ordered state transition rather than jumping directly to a downstream repository or generated artefact. The trace is designed to show which layer owns transport, orchestration, persistence, and evidence. [3a] anchors item-bank pipeline. [3b] anchors calibration service. [3c] anchors irt quality service. [3d] anchors kg diagnostic projection.

**Safe change boundary.** Draft items, approved items, IRT parameters, calibration evidence, and graph projections have explicit statuses. A change that moves responsibility across these boundaries should update the owning codemap, tests, and any affected ADR or release verifier in the same change.

**Controls to preserve.** Uncalibrated items are bounded, quality gates prevent silent promotion, and graph projections retain source evidence.

**How to verify the change.** Run item-bank pipeline, calibration, IRT quality, bias review, and runtime KG diagnostic projection tests. Use the cited locations as navigation anchors, then inspect call sites and tests before modifying behaviour.

## Change checklist

- Update this codemap when an entry point, major dependency, persistence owner, or control flow changes.
- Keep all `Path:LineNumber` references repository-relative and line-valid.
- Update `codemap_coverage_manifest.json` when files move between architecture owners.
- Run `python scripts/maintenance/verify_codemaps.py --repo-root .` before merging.
