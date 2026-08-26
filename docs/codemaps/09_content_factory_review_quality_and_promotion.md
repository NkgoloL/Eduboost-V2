# EduBoost V2 Content Factory, Review, Quality, and Promotion

Maps generation planning, deterministic and LLM providers, provenance, review queues, quality scoring, staging, seeding, and production promotion.

## Scope and ownership

This codemap is the primary architecture owner for:
- `app/api_v2_routers/content_factory.py`
- `app/api_v2_routers/content_review.py`
- `app/api_v2_routers/content_quality.py`
- `app/services/content_*`
- `app/models/content_factory.py`

It describes current implementation paths in repository-relative form. Related cross-cutting behaviour may be referenced from other codemaps, but every maintained source file has one primary owner in `codemap_coverage_manifest.json`.

## Architectural position

This area participates in the wider EduBoost request, data, evidence, and release architecture. Read it together with `00_application_bootstrap_and_request_lifecycle.md`, `17_testing_ci_coverage_security_and_quality_gates.md`, and `18_production_readiness_release_evidence_and_live_traffic.md` when changing runtime or release-critical behaviour.

## Trace ID: 1
**Title:** Generation planning, run locking, execution, and reporting

**Description:** Follows a generation run from coverage gaps and scope blueprints through task execution and final report.

**Motivation:**
Batch content creation must be resumable, bounded, and reproducible rather than an untracked sequence of LLM calls.

**Details:**

**Execution path**

1. Calculate curriculum and product coverage gaps.
2. Create a scoped generation plan and immutable run identity.
3. Acquire the generation run lock.
4. Dispatch deterministic or approved LLM provider tasks.
5. Persist artefacts, source context, failures, and metrics.
6. Release the lock and publish a generation report.

**State and ownership boundaries**

Plans, runs, tasks, artefacts, and reports have distinct statuses that support restart and audit.

**Failure, privacy, and control points**

Only one conflicting run proceeds, provider failures are isolated, budgets are enforced, and partial completion is visible.

**Verification signals**

Run content planner, executor, run-lock, batch generation, and report tests.

**Trace text diagram:**
```text
1. Calculate curriculum and product coverage gaps [1a]
   |
   v
2. Create a scoped generation plan and immutable run identity [1b]
   |
   v
3. Acquire the generation run lock [1c]
   |
   v
4. Dispatch deterministic or approved LLM provider tasks [1d]
   |
   v
5. Persist artefacts, source context, failures, and metrics [1d]
   |
   v
6. Release the lock and publish a generation report [1d]
```

**Location ID: 1a**
- **Title:** Generation planner
- **Description:** Coverage-to-task planning.
- **Path:LineNumber:** app/services/content_generation_planner.py:30

**Location ID: 1b**
- **Title:** Run lock
- **Description:** Concurrent generation exclusion.
- **Path:LineNumber:** app/services/content_generation_run_lock.py:20

**Location ID: 1c**
- **Title:** Generation executor
- **Description:** Task orchestration and persistence.
- **Path:LineNumber:** app/services/content_generation_executor.py:29

**Location ID: 1d**
- **Title:** Generation reporter
- **Description:** Run outcome evidence.
- **Path:LineNumber:** app/services/content_generation_reporter.py:13

### AI Guide: Generation planning, run locking, execution, and reporting

**Motivation:**
Batch content creation must be resumable, bounded, and reproducible rather than an untracked sequence of LLM calls.

**Details:**

**Reasoning through the execution path.** Start at [1a] and follow the ordered state transition rather than jumping directly to a downstream repository or generated artefact. The trace is designed to show which layer owns transport, orchestration, persistence, and evidence. [1a] anchors generation planner. [1b] anchors run lock. [1c] anchors generation executor. [1d] anchors generation reporter.

**Safe change boundary.** Plans, runs, tasks, artefacts, and reports have distinct statuses that support restart and audit. A change that moves responsibility across these boundaries should update the owning codemap, tests, and any affected ADR or release verifier in the same change.

**Controls to preserve.** Only one conflicting run proceeds, provider failures are isolated, budgets are enforced, and partial completion is visible.

**How to verify the change.** Run content planner, executor, run-lock, batch generation, and report tests. Use the cited locations as navigation anchors, then inspect call sites and tests before modifying behaviour.

## Trace ID: 2
**Title:** Artifact validation, provenance, review, and quality scoring

**Description:** Maps generated items and lessons through schema, answer-key, source, safety, reviewer, and quality gates.

**Motivation:**
Generated educational content cannot be trusted solely because a provider returned valid JSON.

**Details:**

**Execution path**

1. Create an artefact with source citations and generation metadata.
2. Validate schema, scope, answer key, PII, and safety.
3. Calculate provenance and quality risk.
4. Place the artefact in the appropriate review queue.
5. Assign reviewers and record decisions.
6. Produce accepted, rejected, or remediation-required status.

**State and ownership boundaries**

Generated payload, validation report, reviewer decisions, and quality score are retained independently.

**Failure, privacy, and control points**

Answer keys are independently verified, source references are approved, reviewer conflicts are controlled, and rejected content never reaches learner reads.

**Verification signals**

Run artifact lifecycle, answer-key, review governance, quality, and content safety tests.

**Trace text diagram:**
```text
1. Create an artefact with source citations and generation metadata [2a]
   |
   v
2. Validate schema, scope, answer key, PII, and safety [2b]
   |
   v
3. Calculate provenance and quality risk [2c]
   |
   v
4. Place the artefact in the appropriate review queue [2d]
   |
   v
5. Assign reviewers and record decisions [2d]
   |
   v
6. Produce accepted, rejected, or remediation-required status [2d]
```

**Location ID: 2a**
- **Title:** Artifact lifecycle
- **Description:** Generated artefact state machine.
- **Path:LineNumber:** app/services/content_artifact_lifecycle.py:20

**Location ID: 2b**
- **Title:** Answer-key verification
- **Description:** Independent correctness gate.
- **Path:LineNumber:** app/services/content_answer_key_verification.py:25

**Location ID: 2c**
- **Title:** Review governance
- **Description:** Reviewer and decision controls.
- **Path:LineNumber:** app/services/content_review_governance.py:53

**Location ID: 2d**
- **Title:** Review risk
- **Description:** Risk-based review routing.
- **Path:LineNumber:** app/services/content_review_risk.py:11

### AI Guide: Artifact validation, provenance, review, and quality scoring

**Motivation:**
Generated educational content cannot be trusted solely because a provider returned valid JSON.

**Details:**

**Reasoning through the execution path.** Start at [2a] and follow the ordered state transition rather than jumping directly to a downstream repository or generated artefact. The trace is designed to show which layer owns transport, orchestration, persistence, and evidence. [2a] anchors artifact lifecycle. [2b] anchors answer-key verification. [2c] anchors review governance. [2d] anchors review risk.

**Safe change boundary.** Generated payload, validation report, reviewer decisions, and quality score are retained independently. A change that moves responsibility across these boundaries should update the owning codemap, tests, and any affected ADR or release verifier in the same change.

**Controls to preserve.** Answer keys are independently verified, source references are approved, reviewer conflicts are controlled, and rejected content never reaches learner reads.

**How to verify the change.** Run artifact lifecycle, answer-key, review governance, quality, and content safety tests. Use the cited locations as navigation anchors, then inspect call sites and tests before modifying behaviour.

## Trace ID: 3
**Title:** Staging seed, read verification, and production promotion

**Description:** Shows accepted content moving through staging previews, seed execution, read verification, promotion gates, and production availability.

**Motivation:**
Promotion is a release process: accepted content must prove storage integrity and learner-read behaviour before becoming active.

**Details:**

**Execution path**

1. Select an approved promotion candidate.
2. Build a versioned staging bundle.
3. Seed staging transactionally.
4. Verify API and learner-read behaviour against staging.
5. Evaluate production promotion gates.
6. Promote or roll back and record evidence.

**State and ownership boundaries**

Staging and production records preserve version, content hash, provenance, and promotion decision.

**Failure, privacy, and control points**

Promotion is idempotent, requires green read verification, cannot bypass review, and supports rollback to a prior content release.

**Verification signals**

Run staging readiness, seed, preview, read verification, production gate, and promotion executor tests.

**Trace text diagram:**
```text
1. Select an approved promotion candidate [3a]
   |
   v
2. Build a versioned staging bundle [3b]
   |
   v
3. Seed staging transactionally [3c]
   |
   v
4. Verify API and learner-read behaviour against staging [3d]
   |
   v
5. Evaluate production promotion gates [3d]
   |
   v
6. Promote or roll back and record evidence [3d]
```

**Location ID: 3a**
- **Title:** Staging seed executor
- **Description:** Controlled staging persistence.
- **Path:LineNumber:** app/services/content_staging_seed_executor.py:32

**Location ID: 3b**
- **Title:** Staging read verification
- **Description:** Learner-read proof.
- **Path:LineNumber:** app/services/content_staging_read_verification.py:19

**Location ID: 3c**
- **Title:** Promotion gate
- **Description:** Production eligibility decision.
- **Path:LineNumber:** app/services/content_production_promotion_gate.py:26

**Location ID: 3d**
- **Title:** Promotion executor
- **Description:** Production transition and evidence.
- **Path:LineNumber:** app/services/content_production_promotion_executor.py:24

### AI Guide: Staging seed, read verification, and production promotion

**Motivation:**
Promotion is a release process: accepted content must prove storage integrity and learner-read behaviour before becoming active.

**Details:**

**Reasoning through the execution path.** Start at [3a] and follow the ordered state transition rather than jumping directly to a downstream repository or generated artefact. The trace is designed to show which layer owns transport, orchestration, persistence, and evidence. [3a] anchors staging seed executor. [3b] anchors staging read verification. [3c] anchors promotion gate. [3d] anchors promotion executor.

**Safe change boundary.** Staging and production records preserve version, content hash, provenance, and promotion decision. A change that moves responsibility across these boundaries should update the owning codemap, tests, and any affected ADR or release verifier in the same change.

**Controls to preserve.** Promotion is idempotent, requires green read verification, cannot bypass review, and supports rollback to a prior content release.

**How to verify the change.** Run staging readiness, seed, preview, read verification, production gate, and promotion executor tests. Use the cited locations as navigation anchors, then inspect call sites and tests before modifying behaviour.

## Change checklist

- Update this codemap when an entry point, major dependency, persistence owner, or control flow changes.
- Keep all `Path:LineNumber` references repository-relative and line-valid.
- Update `codemap_coverage_manifest.json` when files move between architecture owners.
- Run `python scripts/maintenance/verify_codemaps.py --repo-root .` before merging.
