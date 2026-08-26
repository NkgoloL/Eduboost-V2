# EduBoost V2 Production Readiness, Release Evidence, and Live Traffic

Maps PRD authority, implementation and evidence slices, CI convergence, controlled beta, production release, runtime restoration, go/no-go, and live-traffic controls.

## Scope and ownership

This codemap is the primary architecture owner for:
- `scripts/production_readiness`
- `scripts/roadmap_reconciliation`
- `docs/roadmap/production_readiness`
- `app/modules/controlled_beta`
- `app/modules/production_release`
- `app/api_v2_routers/controlled_beta.py`
- `app/api_v2_routers/production_release.py`

It describes current implementation paths in repository-relative form. Related cross-cutting behaviour may be referenced from other codemaps, but every maintained source file has one primary owner in `codemap_coverage_manifest.json`.

## Architectural position

This area participates in the wider EduBoost request, data, evidence, and release architecture. Read it together with `00_application_bootstrap_and_request_lifecycle.md`, `17_testing_ci_coverage_security_and_quality_gates.md`, and `18_production_readiness_release_evidence_and_live_traffic.md` when changing runtime or release-critical behaviour.

## Trace ID: 1
**Title:** PRD authority, implementation, verification, and handoff

**Description:** Follows a production-readiness slice from authorized register state through implementation, evidence, verifier, and next-slice handoff.

**Motivation:**
EduBoost uses evidence-driven gates to prevent documentation claims from outrunning merged code and hosted CI.

**Details:**

**Execution path**

1. Read the canonical PRD register and current authorized item.
2. Apply the bounded implementation slice.
3. Run focused and authority verifiers.
4. Merge authority changes under required checks.
5. Capture evidence from merged master.
6. Merge evidence and advance only the explicitly authorized next item.

**State and ownership boundaries**

Authority records, implementation commits, evidence records, and verifier output are separate linked artefacts.

**Failure, privacy, and control points**

Self-referential SHA loops are avoided, evidence is captured from merged state, and no downstream item is authorized by implementation alone.

**Verification signals**

Run the relevant `audit_prd*` verifier in authority and final modes and confirm clean master plus recorded evidence.

**Trace text diagram:**
```text
1. Read the canonical PRD register and current authorized item [1a]
   |
   v
2. Apply the bounded implementation slice [1b]
   |
   v
3. Run focused and authority verifiers [1c]
   |
   v
4. Merge authority changes under required checks [1d]
   |
   v
5. Capture evidence from merged master [1d]
   |
   v
6. Merge evidence and advance only the explicitly authorized next item [1d]
```

**Location ID: 1a**
- **Title:** Production readiness register
- **Description:** Canonical PRD state authority.
- **Path:LineNumber:** docs/roadmap/production_readiness/production_readiness_register.json:2

**Location ID: 1b**
- **Title:** PRD verifier example
- **Description:** Authority and evidence verification pattern.
- **Path:LineNumber:** scripts/production_readiness/audit_prd207_209_runtime_kg_acceptance_handoff.py:1

**Location ID: 1c**
- **Title:** Evidence capture example
- **Description:** Merged-state evidence creation.
- **Path:LineNumber:** scripts/roadmap_reconciliation/capture_prd207_209_runtime_kg_acceptance_handoff_evidence.py:146

**Location ID: 1d**
- **Title:** PRD workflow
- **Description:** Hosted authority gate.
- **Path:LineNumber:** .github/workflows/prd100-ci-release-gate-stream-authority.yml:1

### AI Guide: PRD authority, implementation, verification, and handoff

**Motivation:**
EduBoost uses evidence-driven gates to prevent documentation claims from outrunning merged code and hosted CI.

**Details:**

**Reasoning through the execution path.** Start at [1a] and follow the ordered state transition rather than jumping directly to a downstream repository or generated artefact. The trace is designed to show which layer owns transport, orchestration, persistence, and evidence. [1a] anchors production readiness register. [1b] anchors prd verifier example. [1c] anchors evidence capture example. [1d] anchors prd workflow.

**Safe change boundary.** Authority records, implementation commits, evidence records, and verifier output are separate linked artefacts. A change that moves responsibility across these boundaries should update the owning codemap, tests, and any affected ADR or release verifier in the same change.

**Controls to preserve.** Self-referential SHA loops are avoided, evidence is captured from merged state, and no downstream item is authorized by implementation alone.

**How to verify the change.** Run the relevant `audit_prd*` verifier in authority and final modes and confirm clean master plus recorded evidence. Use the cited locations as navigation anchors, then inspect call sites and tests before modifying behaviour.

## Trace ID: 2
**Title:** Controlled beta preflight, activation, monitoring, and outcome evidence

**Description:** Maps the decision to permit limited learner traffic through preflight, activation, safeguards, monitoring, and closure.

**Motivation:**
Controlled beta is a constrained production state, not a bypass around security, privacy, content, or operational readiness.

**Details:**

**Execution path**

1. Aggregate current product, privacy, security, content, and SRE readiness.
2. Confirm cohort, consent, support, rollback, and traffic limits.
3. Record authorized beta decision.
4. Activate only the approved cohort and features.
5. Monitor incidents, quality, engagement, and safety signals.
6. Pause, roll back, expand, or close with outcome evidence.

**State and ownership boundaries**

Beta authorization and runtime cohort state are explicit, time-bounded, and separate from general production release.

**Failure, privacy, and control points**

Feature flags cannot exceed authorized scope, critical signals stop traffic, parent communication is ready, and outcomes do not rewrite gate history.

**Verification signals**

Run controlled beta module/routes, preflight, launch monitoring, beta release evidence, and live-traffic handoff verifiers.

**Trace text diagram:**
```text
1. Aggregate current product, privacy, security, content, and SRE readiness [2a]
   |
   v
2. Confirm cohort, consent, support, rollback, and traffic limits [2b]
   |
   v
3. Record authorized beta decision [2c]
   |
   v
4. Activate only the approved cohort and features [2d]
   |
   v
5. Monitor incidents, quality, engagement, and safety signals [2d]
   |
   v
6. Pause, roll back, expand, or close with outcome evidence [2d]
```

**Location ID: 2a**
- **Title:** Beta preflight
- **Description:** Readiness aggregation.
- **Path:LineNumber:** app/modules/controlled_beta/preflight.py:32

**Location ID: 2b**
- **Title:** Beta authorization
- **Description:** Controlled traffic decision.
- **Path:LineNumber:** app/modules/controlled_beta/authorisation.py:32

**Location ID: 2c**
- **Title:** Controlled beta routes
- **Description:** Operational beta status API.
- **Path:LineNumber:** app/api_v2_routers/controlled_beta.py:15

**Location ID: 2d**
- **Title:** Beta approval workflow
- **Description:** Hosted launch decision gate.
- **Path:LineNumber:** .github/workflows/beta-release-approval.yml:1

### AI Guide: Controlled beta preflight, activation, monitoring, and outcome evidence

**Motivation:**
Controlled beta is a constrained production state, not a bypass around security, privacy, content, or operational readiness.

**Details:**

**Reasoning through the execution path.** Start at [2a] and follow the ordered state transition rather than jumping directly to a downstream repository or generated artefact. The trace is designed to show which layer owns transport, orchestration, persistence, and evidence. [2a] anchors beta preflight. [2b] anchors beta authorization. [2c] anchors controlled beta routes. [2d] anchors beta approval workflow.

**Safe change boundary.** Beta authorization and runtime cohort state are explicit, time-bounded, and separate from general production release. A change that moves responsibility across these boundaries should update the owning codemap, tests, and any affected ADR or release verifier in the same change.

**Controls to preserve.** Feature flags cannot exceed authorized scope, critical signals stop traffic, parent communication is ready, and outcomes do not rewrite gate history.

**How to verify the change.** Run controlled beta module/routes, preflight, launch monitoring, beta release evidence, and live-traffic handoff verifiers. Use the cited locations as navigation anchors, then inspect call sites and tests before modifying behaviour.

## Trace ID: 3
**Title:** Production release, runtime restoration, go/no-go, and deployment authority

**Description:** Shows final release state from runtime stack proof and product-critical gates through release decision, deployment, and post-deploy evidence.

**Motivation:**
A production label is valid only when the current merged runtime—not historical reports—passes the required stack, database, product, quality, and security gates.

**Details:**

**Execution path**

1. Restore and verify canonical runtime commands and dependency environment.
2. Prove disposable stack and database migration lineage.
3. Run product-critical, frontend, coverage, static, and security gates.
4. Aggregate release blockers and evidence hashes.
5. Record go/no-go and deployment authorization.
6. Deploy, smoke test, monitor, and close or roll back the release.

**State and ownership boundaries**

Release evidence is commit-specific and environment-specific; prior green evidence cannot authorize a changed runtime.

**Failure, privacy, and control points**

All blockers are explicit, advisory/required status is truthful, deployment is reversible, and post-deploy smoke is part of closure.

**Verification signals**

Run PRD-11 runtime-restore verifiers, release go/no-go, deployment readiness, staging smoke, and release evidence checks.

**Trace text diagram:**
```text
1. Restore and verify canonical runtime commands and dependency environment [3a]
   |
   v
2. Prove disposable stack and database migration lineage [3b]
   |
   v
3. Run product-critical, frontend, coverage, static, and security gates [3c]
   |
   v
4. Aggregate release blockers and evidence hashes [3d]
   |
   v
5. Record go/no-go and deployment authorization [3d]
   |
   v
6. Deploy, smoke test, monitor, and close or roll back the release [3d]
```

**Location ID: 3a**
- **Title:** Production release readiness
- **Description:** Final release aggregation.
- **Path:LineNumber:** app/modules/production_release/readiness.py:32

**Location ID: 3b**
- **Title:** True-state baseline
- **Description:** Current merged runtime authority.
- **Path:LineNumber:** app/modules/production_release/true_state_baseline.py:55

**Location ID: 3c**
- **Title:** Execution-7 verifier
- **Description:** Coverage/static/security release slice.
- **Path:LineNumber:** scripts/production_readiness/audit_prd1100r_runtime_restore_execution_7_coverage_static_security_green.py:1

**Location ID: 3d**
- **Title:** Go/no-go command
- **Description:** Final release decision assembly.
- **Path:LineNumber:** scripts/release_go_no_go.py:1

### AI Guide: Production release, runtime restoration, go/no-go, and deployment authority

**Motivation:**
A production label is valid only when the current merged runtime—not historical reports—passes the required stack, database, product, quality, and security gates.

**Details:**

**Reasoning through the execution path.** Start at [3a] and follow the ordered state transition rather than jumping directly to a downstream repository or generated artefact. The trace is designed to show which layer owns transport, orchestration, persistence, and evidence. [3a] anchors production release readiness. [3b] anchors true-state baseline. [3c] anchors execution-7 verifier. [3d] anchors go/no-go command.

**Safe change boundary.** Release evidence is commit-specific and environment-specific; prior green evidence cannot authorize a changed runtime. A change that moves responsibility across these boundaries should update the owning codemap, tests, and any affected ADR or release verifier in the same change.

**Controls to preserve.** All blockers are explicit, advisory/required status is truthful, deployment is reversible, and post-deploy smoke is part of closure.

**How to verify the change.** Run PRD-11 runtime-restore verifiers, release go/no-go, deployment readiness, staging smoke, and release evidence checks. Use the cited locations as navigation anchors, then inspect call sites and tests before modifying behaviour.

## Change checklist

- Update this codemap when an entry point, major dependency, persistence owner, or control flow changes.
- Keep all `Path:LineNumber` references repository-relative and line-valid.
- Update `codemap_coverage_manifest.json` when files move between architecture owners.
- Run `python scripts/maintenance/verify_codemaps.py --repo-root .` before merging.
