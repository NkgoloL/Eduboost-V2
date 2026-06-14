# Phase 3 Execution Plan — Educator Consensus and Content Governance

**Document version:** 1.0  
**Date:** 2026-06-14  
**Status:** Draft — approval required before execution  
**Phase:** 03  
**Phase owner:** TBD — Engineering Lead  
**Content owner:** TBD — Curriculum/Product Lead  
**Privacy and safeguarding reviewer:** TBD  
**Phase approver:** TBD — Product/Engineering Sponsor  
**Release manager:** TBD  
**Evidence custodian:** TBD  
**Planned phase auditor:** TBD — independent reviewer with application-security and educational-content governance competence  
**Auditor independence:** TBD before start  
**Branch:** `feature/phase-3-educator-consensus`  
**Base branch:** `master`  
**Base commit:** TBD at start gate  
**Target milestone/date:** TBD after estimation approval  
**Governing roadmap:** `roadmap.md` — Phase 3  
**Evidence directory:** `docs/release-evidence/phase-03/`

> **Mandatory control:** substantive Phase 3 implementation may not begin until this execution plan is approved and committed. Phase 3 may not be marked `Verified Complete` until its implementation report, evidence pack, and independent audit are complete and approved against the canonical post-merge source state.

---

## 1. Objective and Measurable Outcome

### 1.1 Objective

Implement a fail-closed, attributable, multi-educator review and publication-governance workflow for AI-generated learner content.

The phase must ensure that no generated diagnostic item, lesson, assessment, worked example, study-plan template, or other learner-facing content can become publishable or retrievable for learner delivery without:

- the required number of distinct, authorised reviewers;
- a completed, versioned review rubric;
- valid content and source provenance;
- conflict-of-interest controls;
- immutable review and state-transition history;
- explicit publication eligibility; and
- successful enforcement by both the application service layer and database constraints.

### 1.2 Measurable outcome

Phase 3 succeeds when all of the following are demonstrated on the canonical merged commit:

1. Fewer than the configured number of valid, independent approvals cannot make an artifact publishable.
2. Duplicate, unauthorised, conflicted, stale, or invalid review actions are rejected.
3. Rejection, quarantine, revision, and supersession remove content from learner delivery and Phase 2 retrieval.
4. Material content changes create a new version and invalidate prior approval quorum.
5. Review decisions and state transitions are append-only and attributable.
6. Concurrent final approvals produce one valid transition without overcounting or inconsistent state.
7. Approved content remains separate from published content until all publication gates pass.
8. Phase 1 and Phase 2 regression gates remain green.
9. The full plan/report/evidence/audit control set is complete.

### 1.3 Risks reduced

- Single-reviewer publication of unsafe or incorrect content.
- Reviewer impersonation or duplicate approval.
- Review-state races and inconsistent approval counts.
- Silent modification of already approved content.
- Learner exposure to rejected or quarantined artifacts.
- Loss of educator accountability and audit traceability.
- Inconsistent review quality across reviewers and languages.
- Publication of content with unresolved CAPS, safety, bias, answer-key, or source-grounding concerns.

---

## 2. Dependencies and Preconditions

| Dependency / precondition | Required state | Required evidence | Owner | Status |
|---|---|---|---|---|
| Phase 1 | `Verified Complete` | Phase 1 control set and post-merge CI | Release Manager | ☐ |
| Phase 2 | `Verified Complete` | Phase 2 control set, pgvector verification, retrieval evaluation, post-merge CI | Release Manager | ☐ |
| Canonical branch | Clean `master` checkout | `git status`, branch, commit SHA | Engineering Lead | ☐ |
| Phase 3 plan | Approved and committed before substantive code work | Approval table and plan commit SHA | Phase Approver | ☐ |
| Existing content models | Inventory completed | Model/schema inventory | Engineering Lead | ☐ |
| Existing review workflows | Inventory completed | Current-state review-flow report | Content Owner | ☐ |
| Reviewer role policy | Named roles and permissions approved | Role matrix | Product/Security | ☐ |
| Review quorum policy | Threshold and independence rules approved | Policy decision or ADR | Content Owner | ☐ |
| Review rubric | Version 1 approved | Rubric document | Curriculum Lead | ☐ |
| Phase 2 exclusion contract | Quarantined/rejected artifacts proven excludable | Retrieval contract/test inventory | Engineering Lead | ☐ |
| Disposable PostgreSQL | Available with migration support | Connection and safety check | Evidence Custodian | ☐ |
| Redis/ARQ | Available if reminders/escalations are implemented as jobs | Runtime verification | Operations | ☐ |
| Auditor | Assigned before verification begins | Independence declaration | Phase Approver | ☐ |

### Stop condition

Phase 3 must not start if Phase 2 is not formally closed, the quorum policy is undecided, the canonical content model cannot be identified, or the execution plan is not approved and committed.

---

## 3. Pre-Execution Baseline

Before implementation, record the following in:

`docs/release-evidence/phase-03/baseline/phase_03_pre_execution_baseline.md`

### 3.1 Source and environment identity

```bash
git status --short
git branch --show-current
git rev-parse HEAD
git remote -v

.venv/bin/python --version
.venv/bin/pip --version
node --version
corepack pnpm --version
docker --version
docker compose version
```

### 3.2 Current implementation inventory

Inventory and document:

- `ContentGenerationArtifact` and related status fields.
- Existing content-review assignment, action, audit, and lifecycle models.
- Existing review routers and service methods.
- Existing reviewer/admin role dependencies.
- Existing publication and learner-serving gates.
- Phase 2 semantic-retrieval eligibility filters.
- Existing content-version and source-provenance fields.
- Existing event/audit logging mechanisms.
- Existing background jobs and notification mechanisms.
- Existing OpenAPI operations for content review.

### 3.3 Current state must answer

- Can one reviewer approve or publish content?
- Can the same reviewer approve more than once?
- Is the content creator permitted to approve their own artifact?
- Are review actions mutable or deletable?
- What happens when approved content changes?
- Can rejected or quarantined content be retrieved or served?
- Is approval count stored, derived, or both?
- Are state transitions transactionally protected?
- Is artifact version part of reviewer uniqueness?
- Does publication have a separate gate from approval?
- Are stale review assignments visible?
- Are review reminders or reassignment supported?
- Is the review rubric stored with each decision?
- Are current historical completion claims supported by evidence?

### 3.4 Baseline gates

Run and retain raw output for:

```bash
# Phase 1 and Phase 2 regressions
bash scripts/verify_phase1.sh
bash scripts/verify_phase2.sh
bash scripts/verify_phase2_postgres.sh

# Architecture and migration state
.venv/bin/python scripts/verify_migration_graph.py
.venv/bin/python scripts/validate_schema_integrity.py
.venv/bin/lint-imports

# Current review-related tests
.venv/bin/python -m pytest -q \
  tests/unit \
  tests/integration \
  -k "review or approval or artifact or quarantine or publication" \
  --no-cov
```

If a command selects zero tests, the baseline must explicitly record that result; zero selected tests may not be reported as a passing gate.

---

## 4. Scope

### 4.1 In scope

- Authoritative artifact review-state machine.
- Versioned review policy and review rubric.
- Reviewer roles, permissions, independence, and conflict controls.
- Configurable review quorum.
- Review assignment lifecycle.
- Distinct reviewer enforcement.
- Duplicate decision and idempotency protection.
- Approval, rejection, quarantine, revision-required, superseded, approved, and published workflows.
- Separation of approval from publication.
- Artifact versioning and re-review after material changes.
- Concurrent-review correctness.
- Immutable audit events.
- Stale-review detection, reminders, reassignment, and escalation.
- Phase 2 retrieval exclusion for ineligible content.
- Learner-delivery exclusion for ineligible content.
- API and OpenAPI contracts.
- Metrics, alerts, and operational runbooks.
- PostgreSQL migrations and database constraints.
- Unit, integration, concurrency, authorisation, and end-to-end tests.
- Phase 3 implementation report, evidence pack, and independent audit.

### 4.2 Out of scope

- New curriculum grades or subjects.
- Broad content-authoring UI redesign unrelated to review governance.
- Automated educational approval by an LLM.
- Automatic publication immediately after quorum.
- National-scale reviewer scheduling.
- Teacher-portal functionality beyond the minimum reviewer workflow.
- Phase 4 IRT calibration or automated content self-healing.
- LoRA/fine-tuning dataset export beyond enforcing quarantine and approval eligibility.
- Replacing the canonical authentication model.
- General notification-platform redesign.

### 4.3 Non-negotiable exclusions

Phase 3 must not:

- treat an LLM review as an educator approval;
- allow approval without a completed rubric;
- allow reviewers to approve a materially changed artifact using an old decision;
- allow client-supplied approval counts or reviewer identity;
- permit direct database status mutation outside the authoritative lifecycle service;
- make quarantine advisory only;
- auto-approve stale reviews;
- silently weaken quorum or independence requirements to make tests pass.

---

## 5. Domain Policy and State Machine

### 5.1 Proposed artifact lifecycle

```text
generated
    ↓
pending_review
    ├──→ revision_required
    │         ↓ new version
    │     pending_review
    ├──→ rejected
    ├──→ quarantined
    └──→ approved
              ↓ publication checks
           published
```

Additional lineage state:

```text
previous version → superseded
```

### 5.2 Permitted transitions

| From | To | Trigger | Minimum authority | Required conditions |
|---|---|---|---|---|
| `generated` | `pending_review` | Submit for review | Content service | Valid artifact, provenance, validation report |
| `pending_review` | `approved` | Quorum reached | Lifecycle service | Distinct valid approvals, rubric complete, no blocking decision |
| `pending_review` | `revision_required` | Reviewer requests correction | Reviewer/Senior reviewer | Reason and rubric findings |
| `pending_review` | `rejected` | Reject decision | Reviewer policy | Reason code and evidence |
| Any non-terminal learner-eligible state | `quarantined` | Safety/compliance intervention | Senior reviewer/Admin | Mandatory reason |
| `approved` | `published` | Publication gate | Publisher/Curriculum lead | All publication checks pass |
| Any version | `superseded` | Material revision accepted | Lifecycle service | New artifact version created |
| `revision_required` | `pending_review` | New version submitted | Content service | Prior version preserved; quorum reset |
| `published` | `quarantined` | Post-publication safety issue | Senior reviewer/Admin | Immediate learner/retrieval removal |

### 5.3 Prohibited transitions

Examples:

- `generated → approved`
- `generated → published`
- `pending_review → published`
- `rejected → approved`
- `quarantined → published`
- `superseded → published`
- direct client mutation of approval count
- direct client mutation of artifact status

### 5.4 State enforcement

The implementation must enforce transitions through:

1. an authoritative lifecycle service;
2. PostgreSQL constraints and uniqueness rules where practical;
3. conditional updates or row locking;
4. service-level authorisation;
5. append-only review and transition events;
6. tests proving prohibited transitions fail.

---

## 6. Reviewer Roles and Authorisation Policy

### 6.1 Proposed roles

| Role | Assign review | Submit review | Approve | Reject | Quarantine | Publish | Audit read |
|---|---:|---:|---:|---:|---:|---:|---:|
| Content creator | No | No for own content unless policy explicitly permits | No | No | No | No | Limited |
| Reviewer | No | Yes | Yes | Yes | Recommend only | No | Own/actions |
| Senior reviewer | Yes | Yes | Yes | Yes | Yes | No | Yes |
| Curriculum lead | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| Administrator | Operational only | No educational approval by default | No by default | No by default | Emergency quarantine | No by default | Yes |
| Auditor | No | No | No | No | No | No | Read-only |
| Learner/Guardian | No | No | No | No | No | No | No |

### 6.2 Independence rules

The policy must explicitly decide and test:

- whether the artifact creator may review their own artifact;
- whether two reviewers from the same account or duplicated identity are prohibited;
- whether a senior reviewer may override quorum;
- whether emergency quarantine is allowed without quorum;
- how reviewer qualification and language competency are represented;
- how conflicts of interest are declared and enforced.

Default recommendation:

- creator approval does not count toward quorum;
- three distinct qualified reviewers;
- at least one reviewer with subject/CAPS competency;
- language-specific content requires at least one reviewer competent in that language;
- emergency quarantine requires one authorised actor and immediate audit logging;
- no role may bypass the publication gate through a normal API call.

### 6.3 Auth source

Reviewer identity, roles, permissions, and actor metadata must come from the canonical authenticated `AuthContext`; they must never be accepted from request payloads.

---

## 7. Versioned Review Rubric

### 7.1 Required rubric areas

Every approval must record a completed rubric covering:

1. CAPS alignment.
2. Factual or mathematical correctness.
3. Answer-key correctness and independence.
4. Grade and reading-level suitability.
5. Language quality.
6. Cultural appropriateness.
7. Bias and stereotype risk.
8. Learner safety.
9. Accessibility and clarity.
10. Source grounding and provenance.
11. Personal-information exposure.
12. Assessment quality, where applicable.
13. Reviewer comments and remediation notes.

### 7.2 Rubric versioning

The system must record:

- `rubric_id`;
- `rubric_version`;
- criteria values;
- required versus optional criteria;
- reviewer identity;
- artifact ID and artifact version;
- policy version;
- submission timestamp.

A later rubric update must not rewrite historical review decisions.

### 7.3 Blocking rubric results

The plan must define which results block approval, including at minimum:

- factual correctness failure;
- answer-key failure;
- unsafe or discriminatory content;
- unapproved source use;
- personal information exposure;
- CAPS mismatch;
- language quality below the approved threshold.

---

## 8. Data Model and Migration Plan

### 8.1 Required entities

The implementation should reuse existing models where sound and introduce only necessary changes.

Expected entities:

- `content_generation_artifacts`
- `content_artifact_versions` or equivalent version fields
- `content_review_assignments`
- `content_review_decisions`
- `content_review_rubric_results`
- `content_state_transition_events`
- optional `content_review_policies`
- optional `content_publication_records`

### 8.2 Required fields

#### Artifact/version

- artifact ID;
- version number or immutable version ID;
- content hash;
- status;
- creator/generator identity;
- source snapshot;
- prompt/model provenance;
- created/updated timestamps;
- approved timestamp;
- published timestamp;
- superseded-by version.

#### Assignment

- assignment ID;
- artifact ID/version;
- reviewer ID;
- required reviewer competency;
- assigned by;
- assigned/accepted/due/completed timestamps;
- assignment status;
- conflict declaration;
- reassignment lineage.

#### Decision

- decision ID;
- artifact ID/version;
- reviewer ID;
- action;
- rubric ID/version;
- structured rubric result;
- reason code;
- reviewer comments;
- idempotency key;
- created timestamp;
- request/correlation ID.

#### State transition

- event ID;
- artifact ID/version;
- previous status;
- new status;
- triggering decision/event;
- actor;
- policy version;
- timestamp;
- correlation ID.

### 8.3 Database constraints

At minimum:

```text
UNIQUE (artifact_id, artifact_version, reviewer_id)
UNIQUE (reviewer_id, idempotency_key)
CHECK approval_count >= 0
CHECK artifact_version > 0
```

Additional requirements:

- foreign keys to authenticated user/reviewer records where architecture permits;
- no cascade deletion of historical review decisions;
- append-only decision/event records;
- status values constrained by enum/check policy;
- optimistic version or row-lock support;
- indexes for pending, stale, assigned, and review-history queries.

### 8.4 Migration safety

The migration plan must:

- use a revision ID no longer than the supported Alembic version-column width;
- upgrade from the current Phase 2 head;
- apply cleanly to an empty database;
- apply cleanly to a database at the Phase 2 head;
- document downgrade limits;
- preserve existing review data;
- avoid setting legacy artifacts to approved without evidence;
- default legacy generated artifacts to the safest non-published state;
- include schema-integrity and migration-graph verification.

---

## 9. Work Breakdown and Execution Order

| ID | Work item | Acceptance criteria | Estimate | Owner | Depends on | Status |
|---|---|---|---:|---|---|---|
| P3-000 | Capture baseline and approve policies | Baseline, role matrix, quorum policy, rubric v1 and source state recorded | 6–10h | Engineering + Content | Preconditions | Not started |
| P3-001 | Define ADR/policy for review governance | Accepted decision for quorum, independence, publication and emergency quarantine | 4–6h | Architecture + Content | P3-000 | Not started |
| P3-010 | Implement artifact/version state model | Authoritative statuses and valid transitions represented | 8–12h | Backend | P3-001 | Not started |
| P3-011 | Add database migration and constraints | Clean and existing-head migration paths pass | 8–12h | Backend | P3-010 | Not started |
| P3-012 | Implement review policy configuration | Configurable quorum, timeout and competency rules validated | 4–6h | Backend | P3-001 | Not started |
| P3-020 | Implement assignment service | Assignment, acceptance, due date, reassignment and conflict controls work | 8–12h | Backend | P3-011 | Not started |
| P3-021 | Implement decision/rubric service | Structured, versioned, append-only decisions are persisted | 10–16h | Backend | P3-011, P3-012 | Not started |
| P3-022 | Implement quorum/lifecycle service | Distinct valid approvals transition exactly once | 12–18h | Backend | P3-021 | Not started |
| P3-023 | Implement revision/version workflow | Material changes create a new version and reset quorum | 8–12h | Backend | P3-022 | Not started |
| P3-024 | Implement quarantine/rejection enforcement | Ineligible artifacts are excluded from learner delivery, retrieval and training export | 8–12h | Backend | P3-022 | Not started |
| P3-025 | Implement publication gate | Approved and published remain separate; publication fails closed | 6–10h | Backend | P3-022 | Not started |
| P3-030 | Add protected API routes | Authenticated role-based review operations exposed consistently | 10–16h | Backend | P3-020–025 | Not started |
| P3-031 | Regenerate OpenAPI/client contracts | New operations represented and drift gate passes | 4–6h | Backend/Frontend | P3-030 | Not started |
| P3-040 | Implement stale-review job and metrics | Stale items detected, reminded, reassignable and never auto-approved | 8–12h | Backend/Ops | P3-020 | Not started |
| P3-041 | Add dashboards and alerts | Backlog, age, rejection, quarantine, completion and SLA metrics visible | 6–10h | Ops | P3-040 | Not started |
| P3-050 | Add unit and state-machine tests | All transitions, negative cases and idempotency covered | 12–20h | QA/Backend | P3-010–025 | Not started |
| P3-051 | Add PostgreSQL concurrency tests | Simultaneous approvals/rejections produce consistent results | 10–16h | QA/Backend | P3-022 | Not started |
| P3-052 | Add authorisation and API tests | Role matrix and HTTP contracts verified | 8–12h | QA/Security | P3-030 | Not started |
| P3-053 | Add Phase 2 exclusion tests | Quarantined/rejected/superseded content cannot be retrieved | 6–10h | QA/Backend | P3-024 | Not started |
| P3-054 | Add end-to-end review/publish test | Generated → reviewed → approved → published path proven | 8–12h | QA | P3-030, P3-051 | Not started |
| P3-060 | Complete implementation report | Every plan item, change and result reconciled | 4–8h | Phase Owner | All implementation | Not started |
| P3-061 | Freeze evidence pack | Evidence attributable to merge candidate | 4–8h | Evidence Custodian | Verification | Not started |
| P3-062 | Independent audit and remediation | Critical procedures reproduced; findings closed | 8–16h | Auditor | Evidence complete | Not started |
| P3-063 | Merge and post-merge closure | Master CI green; evidence/audit updated to merge SHA | 4–8h | Release Manager | P3-062 | Not started |

**Provisional engineering effort:** 138–224 hours before external review and remediation.  
**Scheduling rule:** estimates must be recalculated after the baseline inventory. WIP remains one active engineering epic unless an approved parallel external-review lane is used.

---

## 10. API and Service Contract

### 10.1 Candidate operations

Final route shapes must follow the canonical API prefix and repository conventions.

- `POST /admin/content-review/assignments`
- `GET /admin/content-review/assignments`
- `GET /admin/content-review/artifacts/{artifact_id}/versions/{version}`
- `POST /admin/content-review/artifacts/{artifact_id}/versions/{version}/decisions`
- `POST /admin/content-review/artifacts/{artifact_id}/versions/{version}/quarantine`
- `POST /admin/content-review/artifacts/{artifact_id}/versions/{version}/revise`
- `POST /admin/content-review/artifacts/{artifact_id}/versions/{version}/publish`
- `GET /admin/content-review/artifacts/{artifact_id}/history`
- `GET /admin/content-review/metrics`

### 10.2 API rules

- Actor identity derives from `AuthContext`.
- Unknown request fields are rejected.
- Idempotency key is required for mutation operations.
- HTTP conflict is returned for stale version or concurrent-state conflicts.
- Reason codes are required for reject, quarantine, revision, override, and reassignment.
- Approval count is never accepted from clients.
- Publication endpoint re-evaluates publication gates transactionally.
- History responses are read-only and redact unnecessary personal information.
- Responses include artifact/version identifiers and current state.
- OpenAPI marks any compatibility aliases deprecated with removal milestones.

---

## 11. Concurrency and Idempotency Design

### 11.1 Required protections

Use one approved pattern:

- PostgreSQL `SELECT ... FOR UPDATE`;
- optimistic locking with `row_version`;
- atomic conditional updates;
- or an equivalent transaction-safe design.

### 11.2 Mandatory race scenarios

Test:

1. Two reviewers submit the final required approval simultaneously.
2. One reviewer approves while another rejects.
3. Quarantine occurs while final approval is processing.
4. Material revision occurs while a review is submitted.
5. Duplicate request with the same idempotency key is retried.
6. Same reviewer submits two different decisions for the same version.
7. Publication is attempted while a blocking decision is committed concurrently.

### 11.3 Expected invariants

- Approval count equals the number of valid distinct approval decisions.
- At most one state transition to `approved`.
- Blocking decisions prevent approval/publication.
- Quarantine wins over learner eligibility.
- No historical decision is overwritten.
- Retried requests return the original result where appropriate.
- Stale artifact versions return a conflict and do not affect the latest version.

---

## 12. Test and Verification Plan

### 12.1 Unit and service tests

| Gate | Command / selector | Environment | Expected result | Failure policy | Evidence ID |
|---|---|---|---|---|---|
| State machine | `pytest tests/phase03/test_review_state_machine.py -q` | Python 3.12.3 | Minimum 20 tests; 0 failures/skips | Fail closed | E-03-101 |
| Quorum policy | `pytest tests/phase03/test_consensus_quorum.py -q` | Python 3.12.3 | Minimum 15 tests | Fail closed | E-03-102 |
| Rubric validation | `pytest tests/phase03/test_review_rubric.py -q` | Python 3.12.3 | Minimum 10 tests | Fail closed | E-03-103 |
| Auth policy | `pytest tests/phase03/test_review_authorization.py -q` | Python 3.12.3 | Full role matrix | Fail closed | E-03-104 |
| Versioning | `pytest tests/phase03/test_artifact_versioning.py -q` | Python 3.12.3 | Minimum 10 tests | Fail closed | E-03-105 |
| Quarantine enforcement | `pytest tests/phase03/test_quarantine_enforcement.py -q` | Python 3.12.3 | Learner/retrieval/export blocked | Fail closed | E-03-106 |

Counts are provisional until files are created. The implementation report must record final expected and actual counts.

### 12.2 PostgreSQL integration and concurrency

```bash
bash scripts/verify_phase3_postgres.sh
```

Must prove:

- migration from empty database;
- migration from Phase 2 head;
- uniqueness constraints;
- append-only history;
- row-lock/optimistic-lock behaviour;
- concurrent approval correctness;
- decision persistence after restart;
- quarantine and retrieval exclusion;
- publication-gate transactionality.

**Expected:** zero failures, zero unexpected skips, zero collection errors.

### 12.3 API and OpenAPI

```bash
.venv/bin/python -m pytest -q tests/phase03/test_review_api.py --no-cov
.venv/bin/python scripts/generate_openapi.py --check
```

Must prove:

- 401 for unauthenticated operations;
- 403 for unauthorised roles;
- valid reviewer operations;
- stale version returns conflict;
- duplicate idempotency returns stable result;
- request and response schemas match OpenAPI.

### 12.4 Phase 2 retrieval exclusion

```bash
.venv/bin/python -m pytest -q \
  tests/phase03/test_phase2_retrieval_exclusion.py \
  --no-cov
```

Must prove Phase 2 retrieval never returns:

- pending-review content;
- revision-required content;
- rejected content;
- quarantined content;
- superseded versions;
- unpublished content where publication is required.

### 12.5 Full regression

```bash
bash scripts/verify_phase1.sh
bash scripts/verify_phase1_postgres.sh
bash scripts/verify_phase2.sh
bash scripts/verify_phase2_postgres.sh
bash scripts/verify_phase3.sh
bash scripts/verify_phase3_postgres.sh

.venv/bin/lint-imports
.venv/bin/python scripts/verify_migration_graph.py
.venv/bin/python scripts/validate_schema_integrity.py
.venv/bin/python scripts/generate_openapi.py --check
```

No Phase 3 closure is allowed if Phase 1 or Phase 2 regresses.

### 12.6 Warning and skip policy

- Any unexpected skip fails the closure gate.
- Any collection error fails the gate.
- Runtime warnings involving unawaited coroutines fail the gate.
- Database tests may not be skipped in the final evidence run.
- Test count decreases require investigation and explicit approval.
- Flaky retries must be reported; repeated retries are not considered a clean pass.

---

## 13. Security, Privacy, Safety, Accessibility, Content, and Data Impact

### 13.1 Security controls

Threats to test:

- reviewer identity spoofing;
- role escalation;
- IDOR against artifacts and assignments;
- replayed review submissions;
- duplicate approval;
- state-transition tampering;
- direct status mutation;
- audit-history deletion;
- stale-version approval;
- publication bypass;
- malicious rubric payload;
- stored XSS in comments;
- concurrency races;
- emergency-quarantine abuse.

### 13.2 Privacy controls

- Store only necessary reviewer identity and professional metadata.
- Do not expose reviewer email or private profile data to learners.
- Review comments may contain personal data; classify and restrict them.
- Logs must not include full learner content where unnecessary.
- Audit history requires a documented retention period.
- Data-subject workflows must identify whether reviewer records are operational, legal, or educational records.
- Exports and deletion must not corrupt required immutable compliance records; policy must be reviewed.

### 13.3 Learner safety

Any safety-blocking decision or quarantine must immediately prevent learner delivery. This must be enforced at query and service boundaries, not only through cached UI state.

### 13.4 Accessibility

The review interface, if modified, must support:

- keyboard navigation;
- visible focus;
- form labels;
- understandable error summaries;
- accessible rubric controls;
- non-colour-only state indicators.

### 13.5 Content governance

The Curriculum Lead must approve:

- rubric version 1;
- quorum composition;
- reviewer qualification requirements;
- material-change definition;
- publication eligibility;
- language-review rules;
- emergency quarantine policy.

---

## 14. Migration, Deployment, Rollback, and Recovery

### 14.1 Deployment strategy

- Deploy schema changes before enabling the Phase 3 endpoints.
- Keep publication gate disabled until migrations and verification pass.
- Use feature flags for new review workflow if needed.
- Existing artifacts default to a non-publishable state unless prior valid evidence is migrated.
- Do not infer historical approvals from status labels alone.

### 14.2 Rollback triggers

Rollback or disable Phase 3 if:

- unauthorised approval or publication is possible;
- duplicate approvals count toward quorum;
- review history is lost or overwritten;
- migration corrupts existing artifact state;
- quarantine does not remove learner/retrieval availability;
- concurrency creates inconsistent state;
- Phase 1 or Phase 2 regression gates fail.

### 14.3 Rollback plan

- Disable Phase 3 mutation endpoints via feature flag or deployment rollback.
- Preserve new review/audit records; do not destructively downgrade evidence.
- Revert application code to the last known-good release.
- Use forward-fix for migrations where downgrade risks audit history.
- Restore from backup only for verified data corruption.
- Re-run learner-delivery and retrieval exclusion checks after rollback.

### 14.4 Recovery verification

After rollback or recovery:

- confirm no ineligible artifact is learner-accessible;
- confirm Phase 2 retrieval excludes non-approved content;
- verify review history remains readable;
- verify no duplicate or partial decisions;
- reconcile queue/reminder jobs;
- record incident and remediation evidence.

---

## 15. Observability and Operations

### 15.1 Required metrics

- pending review count;
- assignment age;
- time to first review;
- time to quorum;
- approvals/rejections/quarantines by reason;
- stale assignment count;
- reassignment count;
- duplicate/idempotent request count;
- authorisation failures;
- state-transition conflicts;
- publication-gate failures;
- post-publication quarantine count;
- reviewer workload.

### 15.2 Required logs

Privacy-safe structured events:

- assignment created/accepted/reassigned;
- decision submitted;
- quorum changed;
- state transition;
- quarantine;
- revision created;
- publication attempted/succeeded/failed;
- stale review detected;
- policy/rubric version used.

Do not log:

- access tokens;
- secrets;
- unnecessary reviewer personal information;
- full learner-facing content unless required and access-controlled;
- confidential free-text review comments in general application logs.

### 15.3 Alerts

At minimum:

- pending-review backlog above approved threshold;
- reviews older than the configured timeout;
- publication attempt without valid quorum;
- repeated state conflicts;
- audit-event persistence failure;
- quarantine enforcement failure;
- sudden spike in unauthorised review attempts.

### 15.4 Runbook requirements

Create or update:

`docs/runbooks/content_review_governance.md`

It must cover:

- reviewer assignment failure;
- stuck/stale review;
- incorrect approval;
- emergency quarantine;
- content revision and re-review;
- audit-history investigation;
- publication rollback;
- cache/retrieval invalidation;
- escalation contacts.

---

## 16. Risks, Assumptions, External Dependencies, and Stop Conditions

| ID | Risk / assumption | P | I | Mitigation | Trigger / stop condition | Owner |
|---|---|---:|---:|---|---|---|
| R3-001 | Reviewer policy remains undecided | 3 | 5 | Approve policy before coding | No approved policy | Content Owner |
| R3-002 | Existing models conflict with proposed lifecycle | 3 | 4 | Baseline inventory and migration design | Destructive migration needed | Engineering |
| R3-003 | Approval-count drift under concurrency | 4 | 5 | Derive from decisions; locking/conditional updates | Inconsistent count/state | Engineering |
| R3-004 | Creator self-approval undermines independence | 3 | 5 | Enforce creator exclusion by default | Creator decision counts | Content Owner |
| R3-005 | Quarantined content remains in caches/retrieval | 3 | 5 | Query filters, cache invalidation and tests | Any unsafe retrieval | Engineering |
| R3-006 | Review records contain sensitive personal data | 2 | 4 | Data minimisation and access controls | Sensitive log/evidence leak | Privacy Reviewer |
| R3-007 | Review capacity causes backlog | 4 | 3 | Workload metrics, stale detection, reassignment | SLA/backlog threshold exceeded | Product |
| R3-008 | Old content is incorrectly grandfathered | 3 | 5 | Default fail closed; explicit migration policy | Legacy content published without evidence | Content Owner |
| R3-009 | UI permits status assumptions not enforced by API | 3 | 4 | Service and DB enforcement | UI-only control found | Engineering |
| R3-010 | Audit not independent enough | 3 | 4 | Assign reviewer early; reproduce critical gates | Auditor conflict unresolved | Phase Approver |
| R3-011 | Phase 2 retrieval policy diverges | 3 | 5 | Shared eligibility predicate and contract tests | Ineligible artifact returned | Engineering |
| R3-012 | Material change definition is ambiguous | 3 | 4 | Approved policy and content-hash rules | Approval retained after material edit | Content Owner |

---

## 17. Roadmap and Control-Set Traceability

| Roadmap outcome / exit criterion | Planned work | Verification | Evidence ID | Audit procedure | Owner |
|---|---|---|---|---|---|
| Configurable review quorum | P3-001, P3-012, P3-022 | Quorum unit/Postgres tests | E-03-201 | Reproduce 1st, 2nd and final approvals | Engineering |
| Reviewer identity and role controls | P3-020, P3-030 | Role matrix API tests | E-03-202 | Attempt unauthorised and spoofed actions | Security |
| Duplicate review prevention | P3-011, P3-021 | Unique-constraint and idempotency tests | E-03-203 | Reproduce duplicate/concurrent submissions | Auditor |
| Reject and quarantine workflows | P3-024 | State and exclusion tests | E-03-204 | Quarantine sample and inspect retrieval/serving | Content/Security |
| Correction and re-review | P3-023 | Versioning tests | E-03-205 | Modify approved content and verify quorum reset | Content Owner |
| Stale review visibility | P3-040, P3-041 | Job/metric/alert tests | E-03-206 | Age an assignment and observe escalation | Operations |
| Immutable audit history | P3-021, P3-022 | Append-only and chain tests | E-03-207 | Sample decisions/events and attempt mutation | Auditor |
| Versioned content-owner rubric | P3-000, P3-021 | Schema and policy validation | E-03-208 | Sample completed reviews for consistency | Curriculum Lead |
| Fail-closed publication gate | P3-025 | Negative publication tests | E-03-209 | Attempt publish before quorum/blocking result | Auditor |
| Content-owner acceptance | P3-054 | End-to-end review workflow | E-03-210 | Independently follow approved scenario | Content Owner |
| Phase 2 retrieval exclusion | P3-024, P3-053 | Retrieval contract tests | E-03-211 | Query rejected/quarantined versions | Auditor |
| Full control set | P3-060–063 | Document and source-state reconciliation | E-03-212 | Trace plan → report → evidence → audit | Phase Approver |

---

## 18. Evidence-Pack Plan

### 18.1 Required index

Create:

`docs/release-evidence/phase-03/phase_03_evidence_index.md`

### 18.2 Planned evidence inventory

| Evidence ID | Claim | Artifact/raw output | Source state | Sensitivity | Custodian | Revalidation trigger |
|---|---|---|---|---|---|---|
| E-03-001 | Plan approved before execution | Plan approval and commit history | Plan commit | Internal | Evidence Custodian | Plan amendment |
| E-03-002 | Baseline attributable | Baseline report and raw commands | Base SHA | Internal | Evidence Custodian | Base change |
| E-03-101 | State machine passes | Raw pytest/JUnit | Candidate SHA | Internal | QA | State code change |
| E-03-102 | Quorum passes | Raw pytest/JUnit | Candidate SHA | Internal | QA | Policy change |
| E-03-103 | Rubric validation passes | Raw pytest/JUnit, rubric hash | Candidate SHA | Internal | Content Owner | Rubric change |
| E-03-104 | Authorisation matrix passes | API test output | Candidate SHA | Restricted | Security | Role/auth change |
| E-03-105 | Versioning works | Test output and DB samples | Candidate SHA | Internal | Engineering | Model change |
| E-03-106 | Quarantine enforced | Serving/retrieval/export tests | Candidate SHA | Restricted | Security | Eligibility change |
| E-03-201 | PostgreSQL constraints | Migration and constraint output | Candidate SHA/PG version | Internal | Engineering | Migration change |
| E-03-202 | Concurrency safe | Concurrent test output | Candidate SHA | Internal | QA | Transaction change |
| E-03-203 | Audit append-only | Audit-chain output | Candidate SHA | Restricted | Auditor | Audit model change |
| E-03-204 | Stale reviews observable | Job logs/metrics/alerts | Candidate SHA/environment | Internal | Operations | Job/SLA change |
| E-03-205 | Publication fails closed | API/DB test output | Candidate SHA | Internal | QA | Publication change |
| E-03-206 | OpenAPI correct | Generated spec and drift result | Candidate SHA | Public/Internal | API Owner | Route/schema change |
| E-03-207 | Phase 1/2 regressions green | Raw verification logs | Candidate SHA | Internal | Release Manager | Dependency change |
| E-03-208 | Post-merge CI green | CI URL and run metadata | Merge SHA | Internal | Release Manager | New merge |
| E-03-209 | Evidence hashes | SHA-256 manifest | Merge SHA | Internal | Evidence Custodian | Evidence change |
| E-03-210 | Content-owner acceptance | Signed acceptance record | Merge SHA | Restricted | Content Owner | Policy/content change |
| E-03-211 | Independent audit | Final audit report | Merge SHA | Internal | Auditor | Re-audit |
| E-03-212 | Phase closure approval | Closure record/status update | Merge SHA | Internal | Phase Approver | Reopen phase |

### 18.3 Evidence quality rules

- Raw or machine-readable output is required where practical.
- Every command records exit code, duration, environment and test count.
- Screenshots alone are insufficient where raw output exists.
- Evidence must identify branch, commit, environment and operator.
- Hash evidence files and generated artifacts.
- Record all warnings, skips, xfails, retries and collection errors.
- Final database evidence must run with zero database-gated skips.
- Evidence from a feature branch is provisional until repeated or confirmed against the merge commit.
- Sensitive reviewer information must be redacted and access-controlled.
- Evidence retention must align with the approved audit and compliance policy.

---

## 19. Independent Phase Audit Plan

### 19.1 Auditor competence

The auditor should be capable of assessing:

- backend application architecture;
- PostgreSQL transaction and constraint behaviour;
- authentication and authorisation;
- immutable audit design;
- educational-content governance;
- evidence provenance;
- concurrency and idempotency.

A curriculum or assessment specialist must review rubric and content-governance policy even when the technical auditor is separate.

### 19.2 Independence

The auditor must not be the sole author of the implementation. In a single-developer context, compensating controls may include:

- independent reviewer reproducing critical commands;
- separate curriculum/content approval;
- raw evidence and hashes;
- mandatory post-merge CI;
- documented conflict declaration;
- stricter sampling.

### 19.3 Mandatory audit procedures

| Audit area | Independent procedure | Minimum coverage | Expected evidence |
|---|---|---:|---|
| Plan timing | Verify plan approval predates substantive implementation | 100% | Git history and approvals |
| Roadmap traceability | Map each Phase 3 exit criterion to plan/report/evidence | 100% | Traceability matrix |
| Quorum | Reproduce first, second and final approvals | All critical paths | DB/API output |
| Duplicate prevention | Submit duplicate and concurrent decisions | All duplicate scenarios | Constraint/test output |
| Authorisation | Exercise each role and unauthorised actor | Full role matrix | API results |
| Rejection/quarantine | Verify immediate exclusion from learner and retrieval paths | At least 3 artifacts | DB/API/retrieval evidence |
| Versioning | Materially edit approved content and verify reset | At least 2 content types | Version/decision history |
| Audit integrity | Sample events and attempt update/delete | At least 10 events | SQL/test output |
| Publication gate | Attempt publication before quorum and with blocking finding | All block conditions | API/DB result |
| Stale workflow | Age assignment and verify escalation without approval | At least 2 assignments | Job/metric evidence |
| Migration | Upgrade empty DB and Phase 2-head DB | Both paths | Migration logs |
| Regression | Confirm Phases 1 and 2 remain green | Full required gates | Raw logs |
| Evidence provenance | Verify hashes, merge SHA, environment and CI | 100% final artifacts | Manifest/CI |
| Content rubric | Sample completed reviews for consistency | Minimum 10 or all if fewer | Rubric records |
| Closure status | Confirm no Critical/High finding remains | 100% findings | Final audit register |

### 19.4 Audit verdict

Permitted verdicts:

- **Pass**
- **Pass with non-blocking observations**
- **Fail**

Any unresolved Critical or High finding requires **Fail**.

The audit report path is:

`docs/release-evidence/phase-03/phase_03_audit_report.md`

---

## 20. Required Implementation Report

Create:

`docs/roadmap/execution/phase_03_implementation_report.md`

The report must include:

- exact source baseline and final source state;
- approved plan version;
- completed, changed, deferred and omitted tasks;
- files and migrations changed;
- implemented state machine and role policy;
- actual test commands and counts;
- database/concurrency results;
- security/privacy/content decisions;
- deviations and plan amendments;
- defects and remediation;
- evidence-index reconciliation;
- merge and post-merge CI details;
- residual risks;
- audit-readiness declaration.

A report may not label the phase complete before the audit and closure approval.

---

## 21. Change Control

Material changes require a versioned amendment approved before the affected work is accepted.

Material changes include:

- changing quorum;
- allowing creator self-approval;
- changing reviewer roles;
- weakening rubric requirements;
- combining approval and publication;
- allowing historical approvals to survive material edits;
- changing quarantine enforcement;
- deferring database/concurrency tests;
- altering evidence or audit requirements;
- introducing an override path.

### Change log

| Version | Date | Change | Reason | Evidence/audit impact | Approved by |
|---|---|---|---|---|---|
| 1.0 | 2026-06-14 | Initial Phase 3 execution plan | Establish controlled implementation | Defines complete control set | Pending |

---

## 22. Start-Gate Checklist

Phase 3 may move from `Planning` to `Ready to Start` only when all are checked:

- [ ] Canonical plan path is correct.
- [ ] Plan is approved and committed.
- [ ] Phase 1 is `Verified Complete`.
- [ ] Phase 2 is `Verified Complete`.
- [ ] Base branch and commit are recorded.
- [ ] Worktree is clean.
- [ ] Baseline inventory is complete.
- [ ] Quorum policy is approved.
- [ ] Reviewer role and independence policy is approved.
- [ ] Review rubric version 1 is approved.
- [ ] Publication policy is approved.
- [ ] Material-change and re-review policy is approved.
- [ ] Emergency quarantine policy is approved.
- [ ] Every roadmap criterion is mapped.
- [ ] Work items, owners and estimates are defined.
- [ ] Migration strategy is reviewed.
- [ ] Test commands and minimum expected counts are defined.
- [ ] Evidence inventory is approved.
- [ ] Auditor and content reviewer are assigned.
- [ ] Privacy, security, safeguarding and data impacts are reviewed.
- [ ] Stop conditions and rollback plan are accepted.

### Start approval

| Role | Name | Decision | Date | Signature/reference |
|---|---|---|---|---|
| Phase Owner | | ☐ Approve / ☐ Reject | | |
| Engineering Approver | | ☐ Approve / ☐ Reject | | |
| Content/Curriculum Approver | | ☐ Approve / ☐ Reject | | |
| Privacy/Safeguarding Reviewer | | ☐ Approve / ☐ Reject | | |
| Evidence Custodian | | ☐ Ready / ☐ Not ready | | |
| Planned Auditor | | ☐ Scope accepted / ☐ Changes required | | |

---

## 23. Phase Completion and Closure Gate

Phase 3 may move to `Verified Complete` only when:

- [ ] The approved execution plan predates substantive implementation.
- [ ] All mandatory work items are complete.
- [ ] Every roadmap exit criterion passes.
- [ ] Quorum and reviewer-independence policy are enforced.
- [ ] Duplicate and unauthorised decisions are rejected.
- [ ] Concurrent final-review scenarios are correct.
- [ ] Rejection and quarantine remove content from learner delivery.
- [ ] Rejection and quarantine remove content from Phase 2 retrieval.
- [ ] Material changes create a new version and reset quorum.
- [ ] Audit history is append-only and attributable.
- [ ] Stale reviews are observable and never auto-approved.
- [ ] Publication fails closed.
- [ ] Phase 1 and Phase 2 regressions are green.
- [ ] Empty-DB and Phase 2-head migration paths pass.
- [ ] PostgreSQL final verification has zero unexpected skips.
- [ ] OpenAPI drift check passes.
- [ ] Implementation report is complete and approved.
- [ ] Evidence pack is complete, hashed and attributable.
- [ ] Independent audit issues Pass or Pass with non-blocking observations.
- [ ] No Critical or High audit finding remains.
- [ ] Feature branch is merged into `master`.
- [ ] Post-merge CI passes on the merge commit.
- [ ] Final evidence references the merge commit.
- [ ] Phase-status register is updated only after closure approval.

### Closure approval

| Role | Name | Decision | Date | Signature/reference |
|---|---|---|---|---|
| Phase Owner | | ☐ Recommend close / ☐ Keep open | | |
| Engineering Approver | | ☐ Approve / ☐ Reject | | |
| Content/Curriculum Approver | | ☐ Approve / ☐ Reject | | |
| Security/Privacy Reviewer | | ☐ Approve / ☐ Reject | | |
| Independent Auditor | | ☐ Pass / ☐ Pass with observations / ☐ Fail | | |
| Release Manager | | ☐ Merge/CI verified / ☐ Not verified | | |
| Final Phase Approver | | ☐ Verified Complete / ☐ Not complete | | |

---

## 24. Definition of Done

Phase 3 is done only when the implementation proves, with canonical post-merge evidence, that:

- no single educator can publish learner-facing content;
- only authorised, distinct and policy-compliant reviewer decisions count;
- the full rubric is completed and versioned;
- rejected, quarantined, superseded and unpublished content cannot reach learners;
- Phase 2 cannot retrieve ineligible content;
- material changes invalidate prior quorum;
- review history cannot be silently rewritten;
- review concurrency and idempotency are correct;
- stale reviews are visible and actively managed;
- publication is a separate fail-closed transition;
- operations can monitor, investigate and contain failures;
- the implementation report reconciles the approved plan;
- the evidence pack proves every mandatory claim;
- the independent audit passes;
- the work is merged and CI-verified on `master`.

Until all conditions are satisfied, the correct status is not `Complete`; it is one of:

```text
Planning
Ready to Start
In Progress
Verification Pending
Evidence Complete
Audit Review
Closure Review
```
