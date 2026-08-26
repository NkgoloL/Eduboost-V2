# EduBoost V2 Learner, Parent, Onboarding, and Vertical Journeys

Maps account onboarding, learner/guardian relationships, vertical journey orchestration, progress, parent reporting, and trustworthy beta experience.

## Scope and ownership

This codemap is the primary architecture owner for:
- `app/api_v2_routers/onboarding.py`
- `app/api_v2_routers/learners.py`
- `app/api_v2_routers/parents.py`
- `app/api_v2_routers/vertical_journey.py`
- `app/modules/vertical_journey`
- `app/services/learner_service.py`

It describes current implementation paths in repository-relative form. Related cross-cutting behaviour may be referenced from other codemaps, but every maintained source file has one primary owner in `codemap_coverage_manifest.json`.

## Architectural position

This area participates in the wider EduBoost request, data, evidence, and release architecture. Read it together with `00_application_bootstrap_and_request_lifecycle.md`, `17_testing_ci_coverage_security_and_quality_gates.md`, and `18_production_readiness_release_evidence_and_live_traffic.md` when changing runtime or release-critical behaviour.

## Trace ID: 1
**Title:** Onboarding and learner profile creation

**Description:** Follows a new household from authenticated account through consent-aware learner creation and initial profile state.

**Motivation:**
Onboarding establishes the identities, relationships, consent, grade, and learning context used by every later journey.

**Details:**

**Execution path**

1. Authenticate guardian or eligible learner.
2. Capture required policy acknowledgements and consent.
3. Validate learner profile and relationship data.
4. Persist learner and guardian linkage atomically.
5. Initialize diagnostic, progress, and preference state.
6. Return the next eligible onboarding action.

**State and ownership boundaries**

Identity, relationship, learner profile, and consent records have separate lifecycles but are joined by stable IDs.

**Failure, privacy, and control points**

Duplicate learners are detected, minors cannot self-assert guardian authority, and partial onboarding is resumable.

**Verification signals**

Run onboarding, learner creation, relationship authorization, and consent integration tests.

**Trace text diagram:**
```text
1. Authenticate guardian or eligible learner [1a]
   |
   v
2. Capture required policy acknowledgements and consent [1b]
   |
   v
3. Validate learner profile and relationship data [1c]
   |
   v
4. Persist learner and guardian linkage atomically [1d]
   |
   v
5. Initialize diagnostic, progress, and preference state [1d]
   |
   v
6. Return the next eligible onboarding action [1d]
```

**Location ID: 1a**
- **Title:** Onboarding routes
- **Description:** Household onboarding transport.
- **Path:LineNumber:** app/api_v2_routers/onboarding.py:20

**Location ID: 1b**
- **Title:** Learner routes
- **Description:** Learner profile API.
- **Path:LineNumber:** app/api_v2_routers/learners.py:25

**Location ID: 1c**
- **Title:** Learner service
- **Description:** Profile and relationship business logic.
- **Path:LineNumber:** app/services/learner_service.py:12

**Location ID: 1d**
- **Title:** Learner repository
- **Description:** Persistent learner state.
- **Path:LineNumber:** app/repositories/learner_repository.py:16

### AI Guide: Onboarding and learner profile creation

**Motivation:**
Onboarding establishes the identities, relationships, consent, grade, and learning context used by every later journey.

**Details:**

**Reasoning through the execution path.** Start at [1a] and follow the ordered state transition rather than jumping directly to a downstream repository or generated artefact. The trace is designed to show which layer owns transport, orchestration, persistence, and evidence. [1a] anchors onboarding routes. [1b] anchors learner routes. [1c] anchors learner service. [1d] anchors learner repository.

**Safe change boundary.** Identity, relationship, learner profile, and consent records have separate lifecycles but are joined by stable IDs. A change that moves responsibility across these boundaries should update the owning codemap, tests, and any affected ADR or release verifier in the same change.

**Controls to preserve.** Duplicate learners are detected, minors cannot self-assert guardian authority, and partial onboarding is resumable.

**How to verify the change.** Run onboarding, learner creation, relationship authorization, and consent integration tests. Use the cited locations as navigation anchors, then inspect call sites and tests before modifying behaviour.

## Trace ID: 2
**Title:** Diagnostic-to-lesson vertical journey

**Description:** Maps the end-to-end learner progression from readiness and diagnostic evidence to lesson, completion, mastery, and next action.

**Motivation:**
The platform’s value is realized through coherent vertical journeys rather than isolated features.

**Details:**

**Execution path**

1. Resolve learner, consent, and journey readiness.
2. Start or resume a diagnostic session.
3. Calculate mastery and runtime KG projections.
4. Select or generate the next lesson or remediation.
5. Complete the lesson transactionally.
6. Update progress, study plan, and next-best action.

**State and ownership boundaries**

Journey state references authoritative diagnostic, lesson, mastery, and graph records rather than duplicating them.

**Failure, privacy, and control points**

Every transition is resumable, idempotent where retried, and blocked when consent or prerequisite state is invalid.

**Verification signals**

Run vertical journey hardening, seeded E2E, diagnostic, lesson completion, and runtime KG projection tests.

**Trace text diagram:**
```text
1. Resolve learner, consent, and journey readiness [2a]
   |
   v
2. Start or resume a diagnostic session [2b]
   |
   v
3. Calculate mastery and runtime KG projections [2c]
   |
   v
4. Select or generate the next lesson or remediation [2d]
   |
   v
5. Complete the lesson transactionally [2d]
   |
   v
6. Update progress, study plan, and next-best action [2d]
```

**Location ID: 2a**
- **Title:** Vertical journey API
- **Description:** Cross-domain learner journey endpoints.
- **Path:LineNumber:** app/api_v2_routers/vertical_journey.py:22

**Location ID: 2b**
- **Title:** Journey service
- **Description:** Cross-domain orchestration.
- **Path:LineNumber:** app/modules/vertical_journey/service.py:53

**Location ID: 2c**
- **Title:** Journey hardening
- **Description:** Acceptance and failure-mode controls.
- **Path:LineNumber:** app/modules/vertical_journey/hardening.py:36

**Location ID: 2d**
- **Title:** Transactional completion
- **Description:** Atomic lesson completion and downstream updates.
- **Path:LineNumber:** app/services/lesson_transactional_completion.py:10

### AI Guide: Diagnostic-to-lesson vertical journey

**Motivation:**
The platform’s value is realized through coherent vertical journeys rather than isolated features.

**Details:**

**Reasoning through the execution path.** Start at [2a] and follow the ordered state transition rather than jumping directly to a downstream repository or generated artefact. The trace is designed to show which layer owns transport, orchestration, persistence, and evidence. [2a] anchors vertical journey api. [2b] anchors journey service. [2c] anchors journey hardening. [2d] anchors transactional completion.

**Safe change boundary.** Journey state references authoritative diagnostic, lesson, mastery, and graph records rather than duplicating them. A change that moves responsibility across these boundaries should update the owning codemap, tests, and any affected ADR or release verifier in the same change.

**Controls to preserve.** Every transition is resumable, idempotent where retried, and blocked when consent or prerequisite state is invalid.

**How to verify the change.** Run vertical journey hardening, seeded E2E, diagnostic, lesson completion, and runtime KG projection tests. Use the cited locations as navigation anchors, then inspect call sites and tests before modifying behaviour.

## Trace ID: 3
**Title:** Parent portal, reports, progress, and trustworthy beta feedback

**Description:** Shows how authorized guardians view progress, receive explanations, and submit beta feedback without exposing private learner internals.

**Motivation:**
Guardian visibility and understandable evidence are core to trust, consent, and educational usefulness.

**Details:**

**Execution path**

1. Authenticate guardian and verify learner relationship.
2. Load consent-compatible learner summary.
3. Aggregate progress, mastery, lessons, and plan state.
4. Generate parent-safe explanations and reports.
5. Redact tutor or sensitive internal content.
6. Capture feedback and operational quality signals.

**State and ownership boundaries**

Parent reports are projections of authoritative learner data and may have independent retention and redaction rules.

**Failure, privacy, and control points**

Relationship checks occur server-side, reports minimize data, and feedback does not silently modify learner mastery.

**Verification signals**

Run parent portal, parent-review access/redaction/retention, progress, and trustworthy beta tests.

**Trace text diagram:**
```text
1. Authenticate guardian and verify learner relationship [3a]
   |
   v
2. Load consent-compatible learner summary [3b]
   |
   v
3. Aggregate progress, mastery, lessons, and plan state [3c]
   |
   v
4. Generate parent-safe explanations and reports [3d]
   |
   v
5. Redact tutor or sensitive internal content [3d]
   |
   v
6. Capture feedback and operational quality signals [3d]
```

**Location ID: 3a**
- **Title:** Parent routes
- **Description:** Guardian-facing API.
- **Path:LineNumber:** app/api_v2_routers/parents.py:32

**Location ID: 3b**
- **Title:** Parent report service
- **Description:** Guardian-safe reporting.
- **Path:LineNumber:** app/services/parent_report_service_v2.py:8

**Location ID: 3c**
- **Title:** Progress timeline
- **Description:** Learner progress projection.
- **Path:LineNumber:** app/modules/progress/progress_timeline_service.py:10

**Location ID: 3d**
- **Title:** Trustworthy beta quality
- **Description:** Product feedback and quality evidence.
- **Path:LineNumber:** app/services/trustworthy_beta_quality.py:7

### AI Guide: Parent portal, reports, progress, and trustworthy beta feedback

**Motivation:**
Guardian visibility and understandable evidence are core to trust, consent, and educational usefulness.

**Details:**

**Reasoning through the execution path.** Start at [3a] and follow the ordered state transition rather than jumping directly to a downstream repository or generated artefact. The trace is designed to show which layer owns transport, orchestration, persistence, and evidence. [3a] anchors parent routes. [3b] anchors parent report service. [3c] anchors progress timeline. [3d] anchors trustworthy beta quality.

**Safe change boundary.** Parent reports are projections of authoritative learner data and may have independent retention and redaction rules. A change that moves responsibility across these boundaries should update the owning codemap, tests, and any affected ADR or release verifier in the same change.

**Controls to preserve.** Relationship checks occur server-side, reports minimize data, and feedback does not silently modify learner mastery.

**How to verify the change.** Run parent portal, parent-review access/redaction/retention, progress, and trustworthy beta tests. Use the cited locations as navigation anchors, then inspect call sites and tests before modifying behaviour.

## Change checklist

- Update this codemap when an entry point, major dependency, persistence owner, or control flow changes.
- Keep all `Path:LineNumber` references repository-relative and line-valid.
- Update `codemap_coverage_manifest.json` when files move between architecture owners.
- Run `python scripts/maintenance/verify_codemaps.py --repo-root .` before merging.
