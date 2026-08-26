# EduBoost V2 Lessons, Tutor, Study Plans, Practice, and Gamification

Maps lesson generation and validation, tutor orchestration, runtime-KG study plans, practice scheduling, completion, progress, and rewards.

## Scope and ownership

This codemap is the primary architecture owner for:
- `app/api_v2_routers/lessons.py`
- `app/api_v2_routers/tutor.py`
- `app/api_v2_routers/study_plans.py`
- `app/api_v2_routers/gamification.py`
- `app/modules/lessons`
- `app/modules/practice`
- `app/modules/study_plans`

It describes current implementation paths in repository-relative form. Related cross-cutting behaviour may be referenced from other codemaps, but every maintained source file has one primary owner in `codemap_coverage_manifest.json`.

## Architectural position

This area participates in the wider EduBoost request, data, evidence, and release architecture. Read it together with `00_application_bootstrap_and_request_lifecycle.md`, `17_testing_ci_coverage_security_and_quality_gates.md`, and `18_production_readiness_release_evidence_and_live_traffic.md` when changing runtime or release-critical behaviour.

## Trace ID: 1
**Title:** Lesson planning, grounded generation, validation, and delivery

**Description:** Follows a lesson request from learner context through curriculum grounding, generation, validation, persistence, and delivery.

**Motivation:**
Generated lessons must be curriculum-aligned, learner-appropriate, safe, reproducible, and traceable to approved sources.

**Details:**

**Execution path**

1. Authorize learner and verify consent and quota.
2. Build learner, mastery, curriculum, and graph context.
3. Plan lesson objective, difficulty, and modality.
4. Generate or assemble lesson content.
5. Validate answer keys, schema, safety, provenance, and CAPS mapping.
6. Persist the accepted lesson and return a trust-labelled response.

**State and ownership boundaries**

Lesson drafts, validation reports, source citations, and delivered lesson versions are separate auditable records.

**Failure, privacy, and control points**

Unsafe or ungrounded output is rejected or falls back deterministically; retries do not create conflicting lesson versions.

**Verification signals**

Run lesson generator, validator, answer-key, grounding, quota, and route-contract tests.

**Trace text diagram:**
```text
1. Authorize learner and verify consent and quota [1a]
   |
   v
2. Build learner, mastery, curriculum, and graph context [1b]
   |
   v
3. Plan lesson objective, difficulty, and modality [1c]
   |
   v
4. Generate or assemble lesson content [1d]
   |
   v
5. Validate answer keys, schema, safety, provenance, and CAPS mapping [1d]
   |
   v
6. Persist the accepted lesson and return a trust-labelled response [1d]
```

**Location ID: 1a**
- **Title:** Lesson routes
- **Description:** Learner lesson API.
- **Path:LineNumber:** app/api_v2_routers/lessons.py:34

**Location ID: 1b**
- **Title:** Lesson generator
- **Description:** Adaptive content assembly.
- **Path:LineNumber:** app/modules/lessons/lesson_generator.py:62

**Location ID: 1c**
- **Title:** Lesson validator
- **Description:** Quality and safety gate.
- **Path:LineNumber:** app/modules/lessons/lesson_validator.py:57

**Location ID: 1d**
- **Title:** Lesson context builder
- **Description:** Learner and curriculum grounding context.
- **Path:LineNumber:** app/services/lesson_context_builder.py:35

### AI Guide: Lesson planning, grounded generation, validation, and delivery

**Motivation:**
Generated lessons must be curriculum-aligned, learner-appropriate, safe, reproducible, and traceable to approved sources.

**Details:**

**Reasoning through the execution path.** Start at [1a] and follow the ordered state transition rather than jumping directly to a downstream repository or generated artefact. The trace is designed to show which layer owns transport, orchestration, persistence, and evidence. [1a] anchors lesson routes. [1b] anchors lesson generator. [1c] anchors lesson validator. [1d] anchors lesson context builder.

**Safe change boundary.** Lesson drafts, validation reports, source citations, and delivered lesson versions are separate auditable records. A change that moves responsibility across these boundaries should update the owning codemap, tests, and any affected ADR or release verifier in the same change.

**Controls to preserve.** Unsafe or ungrounded output is rejected or falls back deterministically; retries do not create conflicting lesson versions.

**How to verify the change.** Run lesson generator, validator, answer-key, grounding, quota, and route-contract tests. Use the cited locations as navigation anchors, then inspect call sites and tests before modifying behaviour.

## Trace ID: 2
**Title:** Tutor orchestration and runtime-KG study planning

**Description:** Maps tutor input through safety, grounded retrieval, next-best-action selection, and study-plan updates.

**Motivation:**
The tutor must move learner knowledge state toward the target graph without becoming an unconstrained conversational system.

**Details:**

**Execution path**

1. Authorize tutor interaction and evaluate consent.
2. Apply input safety and rate limits.
3. Load learner shadow, target graph, gaps, and recent activity.
4. Select grounded intervention or next-best action.
5. Generate a bounded tutor response or study-plan step.
6. Persist plan changes, evidence, and parent-review metadata.

**State and ownership boundaries**

Tutor conversations, study plans, plan steps, and KG evidence have distinct retention and review policies.

**Failure, privacy, and control points**

Responses are grounded, prompt injection is constrained, plan updates are explainable, and parent access is redacted.

**Verification signals**

Run tutor safety, route, parent-review, study-plan, and runtime-KG planner tests.

**Trace text diagram:**
```text
1. Authorize tutor interaction and evaluate consent [2a]
   |
   v
2. Apply input safety and rate limits [2b]
   |
   v
3. Load learner shadow, target graph, gaps, and recent activity [2c]
   |
   v
4. Select grounded intervention or next-best action [2d]
   |
   v
5. Generate a bounded tutor response or study-plan step [2d]
   |
   v
6. Persist plan changes, evidence, and parent-review metadata [2d]
```

**Location ID: 2a**
- **Title:** Tutor routes
- **Description:** Tutor interaction transport.
- **Path:LineNumber:** app/api_v2_routers/tutor.py:32

**Location ID: 2b**
- **Title:** Learner tutor
- **Description:** Grounded tutor orchestration.
- **Path:LineNumber:** app/services/learner_tutor.py:44

**Location ID: 2c**
- **Title:** Runtime KG planner
- **Description:** Gap-driven study plan projection.
- **Path:LineNumber:** app/modules/study_plans/runtime_kg_planner.py:9

**Location ID: 2d**
- **Title:** Study plan service
- **Description:** Plan persistence and delivery.
- **Path:LineNumber:** app/services/study_plan_service_v2.py:10

### AI Guide: Tutor orchestration and runtime-KG study planning

**Motivation:**
The tutor must move learner knowledge state toward the target graph without becoming an unconstrained conversational system.

**Details:**

**Reasoning through the execution path.** Start at [2a] and follow the ordered state transition rather than jumping directly to a downstream repository or generated artefact. The trace is designed to show which layer owns transport, orchestration, persistence, and evidence. [2a] anchors tutor routes. [2b] anchors learner tutor. [2c] anchors runtime kg planner. [2d] anchors study plan service.

**Safe change boundary.** Tutor conversations, study plans, plan steps, and KG evidence have distinct retention and review policies. A change that moves responsibility across these boundaries should update the owning codemap, tests, and any affected ADR or release verifier in the same change.

**Controls to preserve.** Responses are grounded, prompt injection is constrained, plan updates are explainable, and parent access is redacted.

**How to verify the change.** Run tutor safety, route, parent-review, study-plan, and runtime-KG planner tests. Use the cited locations as navigation anchors, then inspect call sites and tests before modifying behaviour.

## Trace ID: 3
**Title:** Completion, spaced practice, progress, and rewards

**Description:** Shows how lesson and practice completion update mastery, scheduling, progress, badges, and next actions.

**Motivation:**
Completion is the feedback loop that turns content delivery into durable learner-state change.

**Details:**

**Execution path**

1. Submit lesson or practice outcome.
2. Validate ownership and completion preconditions.
3. Persist completion and mastery evidence atomically.
4. Update spaced-repetition schedule and learning velocity.
5. Evaluate achievement and badge rules.
6. Refresh progress, study plan, and next recommended activity.

**State and ownership boundaries**

Completion events are immutable evidence; derived progress, schedules, and rewards can be rebuilt from accepted events.

**Failure, privacy, and control points**

Duplicate completion is idempotent, rewards cannot be forged client-side, and mastery updates preserve diagnostic provenance.

**Verification signals**

Run lesson completion, practice scheduler, progress model, gamification repository, and vertical journey tests.

**Trace text diagram:**
```text
1. Submit lesson or practice outcome [3a]
   |
   v
2. Validate ownership and completion preconditions [3b]
   |
   v
3. Persist completion and mastery evidence atomically [3c]
   |
   v
4. Update spaced-repetition schedule and learning velocity [3d]
   |
   v
5. Evaluate achievement and badge rules [3d]
   |
   v
6. Refresh progress, study plan, and next recommended activity [3d]
```

**Location ID: 3a**
- **Title:** Lesson completion
- **Description:** Atomic completion transition.
- **Path:LineNumber:** app/services/lesson_transactional_completion.py:10

**Location ID: 3b**
- **Title:** Practice scheduler
- **Description:** Review interval computation.
- **Path:LineNumber:** app/modules/practice/spaced_repetition_scheduler.py:8

**Location ID: 3c**
- **Title:** Gamification service
- **Description:** Points, achievements, and badges.
- **Path:LineNumber:** app/services/gamification_service_v2.py:8

**Location ID: 3d**
- **Title:** Mastery model
- **Description:** Derived learner mastery state.
- **Path:LineNumber:** app/modules/progress/mastery_model.py:7

### AI Guide: Completion, spaced practice, progress, and rewards

**Motivation:**
Completion is the feedback loop that turns content delivery into durable learner-state change.

**Details:**

**Reasoning through the execution path.** Start at [3a] and follow the ordered state transition rather than jumping directly to a downstream repository or generated artefact. The trace is designed to show which layer owns transport, orchestration, persistence, and evidence. [3a] anchors lesson completion. [3b] anchors practice scheduler. [3c] anchors gamification service. [3d] anchors mastery model.

**Safe change boundary.** Completion events are immutable evidence; derived progress, schedules, and rewards can be rebuilt from accepted events. A change that moves responsibility across these boundaries should update the owning codemap, tests, and any affected ADR or release verifier in the same change.

**Controls to preserve.** Duplicate completion is idempotent, rewards cannot be forged client-side, and mastery updates preserve diagnostic provenance.

**How to verify the change.** Run lesson completion, practice scheduler, progress model, gamification repository, and vertical journey tests. Use the cited locations as navigation anchors, then inspect call sites and tests before modifying behaviour.

## Change checklist

- Update this codemap when an entry point, major dependency, persistence owner, or control flow changes.
- Keep all `Path:LineNumber` references repository-relative and line-valid.
- Update `codemap_coverage_manifest.json` when files move between architecture owners.
- Run `python scripts/maintenance/verify_codemaps.py --repo-root .` before merging.
