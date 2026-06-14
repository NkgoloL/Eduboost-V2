# EduBoost Full-Lifecycle Delivery and Beta Readiness Plan

**Document owner:** NkgoloL  
**Version:** 5.0  
**Date:** 2026-06-13  
**Status:** Proposed authoritative programme baseline  
**Applies to:** EduBoost V2, Phases 0–13, through controlled beta  

> This plan corrects a lifecycle omission introduced when later planning documents began at Phase 8 and implicitly treated Phases 0–7 as completed.
>
> Phases 0–7 are not accepted as complete. Existing implementation may be credited only after the current phase exit criteria pass and attributable evidence is approved.
>
> The technical audit remains outside this document. Its corrective work is governed by `audit_remediation_roadmap_2026-06-13.md`, which is independently authoritative and does not replace any roadmap phase.

---

## Executive Summary

EduBoost's roadmap is a complete Phase 0–13 programme. The earlier seven phases establish the product and platform foundations: environment and provider configuration, batch content generation, semantic retrieval, educator consensus, adaptive-item quality controls, the learner AI Tutor, production hardening, and beta content coverage. Phases 8–13 then establish architecture assurance, authoritative CI, product readiness, operational readiness, external governance, and the controlled beta.

The later seven planning documents began at Phase 8. That structure was unsafe because the historical roadmaps disagree about Phases 0–7: Roadmaps v3 and v4 claimed local completion, while Executive Roadmap v5 states that the programme is pre-implementation and no phase has started. The programme therefore cannot inherit either claim without current evidence.

This plan adopts one controlling rule:

> **A phase is complete only when its current exit criteria pass for an identified source state and environment, and the evidence is approved.**

Accordingly, all phases begin with an evidence-based status. Phases 0–7 are initially classified as **Open — completion not established**. Existing code and tests may reduce the remaining work, but they do not bypass the phase gates.

### Full delivery sequence

```text
Audit Remediation Track R
(independent, cross-cutting; does not replace roadmap phases)
             │
             ├───────────────┐
             ▼               │
Phase 0  Environment and Reproducibility
             ▼               │
Phase 1  Batch AI Content Generation
             ▼               │
Phase 2  Semantic Retrieval
             ▼               │
Phase 3  Educator Consensus and Content Governance
             ▼               │
Phase 4  IRT Quality and Self-Healing Controls
             ▼               │
Phase 5  Learner AI Tutor
             ▼               │
Phase 6  Monitoring, Budget, and Production Hardening
             ▼               │
Phase 7  Beta Content Coverage and Language Readiness
             └──────┬────────┘
                    ▼
Phase 8  Architecture and Codebase Assurance
                    ▼
Phase 9  CI Authority and Reproducible Evidence
                    ▼
Phase 10 Product Readiness
                    ▼
Phase 11 Operations Readiness
                    │
        Phase 12 External Review and Governance
          (may begin earlier where independent)
                    │
                    ▼
Phase 13 Controlled Beta
```

### Current programme status

| Item | Baseline status |
|---|---|
| Overall programme | **Open — full lifecycle not yet accepted** |
| Phases 0–7 | **Open — completion not established** |
| Audit remediation | Governed separately; status taken only from its own decision record |
| Phases 8–13 | Open; blocked by earlier phase gates and stated dependencies |
| Controlled beta | No-Go until every mandatory entry gate passes |

### Planning range

The planning range is provisional because the remaining work in Phases 0–7 has not yet been measured against their exit criteria.

| Programme segment | Provisional duration |
|---|---:|
| Phases 0–7 — verify, complete, and evidence the product foundation | 10–18 weeks |
| Phases 8–9 — architecture assurance and CI authority | 7–11 weeks |
| Phases 10–11 — product and operations readiness | 5–7 weeks |
| Phase 12 — external reviews and findings closure | 4–8 weeks, partly overlapping |
| Phase 13 — controlled beta and analysis | 5–6 weeks |

**Provisional full-lifecycle range: 27–42 calendar weeks**, plus any non-overlapped audit-remediation work or external vendor delay.

This range may contract when current evidence proves that part of a phase already satisfies its exit criteria. It may not contract merely because an older roadmap marked work complete.

---

## Programme Objective

Deliver a controlled beta that is:

- secure, privacy compliant, and appropriate for children;
- educationally credible and based on approved CAPS-aligned content;
- supported by reliable AI generation, retrieval, review, and adaptive-quality controls;
- operationally supportable and recoverable;
- governed by authoritative CI and attributable evidence;
- measurable across learning, engagement, reliability, safety, cost, and satisfaction; and
- capable of supporting a defensible Go, Extend, or No-Go decision.

The beta validates a defined launch scope. It does not prove national scalability or broad educational effectiveness.

---

## Status Reconciliation and Completion Policy

### Historical conflict

| Source | Treatment of Phases 0–7 | Programme interpretation |
|---|---|---|
| `ROADMAP_v2.md` | Defines the original Phase 0–7 work | Valid source for intended scope, not completion |
| `ROADMAP_v3.md` | Marks phases locally complete or CI pending | Historical assertion requiring revalidation |
| `ROADMAP_v4.md` | Carries the same assertions into the 13-phase roadmap | Historical assertion requiring revalidation |
| `Roadmap_v5_Executive.md` | States pre-implementation; no phase started | Conflicts with v3/v4; cannot be accepted alone |
| Seven later planning files | Begin at Phase 8 | Incomplete lifecycle; cannot govern the full programme alone |

### Controlling status model

| Status | Meaning |
|---|---|
| **Not started** | No approved execution plan exists and no substantive phase work may begin. |
| **Open — completion not established** | Implementation may exist, but the phase lacks an approved execution plan, reconciled implementation report, complete evidence pack, and passing phase audit. |
| **In progress** | The execution plan is approved and the owner is actively executing it under controlled WIP. |
| **Blocked** | A named dependency prevents progress. |
| **Verified complete** | The approved execution plan has been fully reconciled by an approved implementation report; all exit criteria pass on the canonical merged source state. |
| **Deferred** | Explicitly removed from the current release with an approved reason, owner, and target. |

### No-inheritance rule

A phase may not be marked complete because:

- a previous roadmap used a completion icon;
- code appears to implement the feature;
- a local test passed at an unknown or stale commit;
- a downstream phase was already planned;
- a later document omitted the phase;
- a related audit finding was remediated.

Each phase requires its own approved plan/report/evidence/audit control set.

---

## Scope and Relationship to Controlled Documents

This plan governs:

- the Phase 0–13 sequence and dependencies;
- phase status and exit criteria;
- capacity and WIP rules;
- beta scope, success measures, and decision bands;
- architecture and risk governance;
- evidence organisation and release approval;
- programme reporting and change control.

The independent audit-remediation roadmap governs its own findings, workstreams, exceptions, verification, and closure. It may overlap with Phase 0–7 work where dependencies permit, but it cannot be used to skip or close those phases.

Detailed tickets, ADRs, runbooks, test plans, content-review trackers, vendor reports, and release evidence remain separate linked artefacts.

---

## Governing Principles

1. **Plan before execution.** No phase may enter implementation until its execution plan exists, is approved, and is committed as the first controlled artefact for that phase.
2. **Report before completion.** No phase may be marked complete until its implementation report reconciles planned versus actual delivery, cites attributable evidence, and receives closure approval.
3. **Evidence over assertion.** Every completion claim points to current, attributable proof.
4. **One source of truth per concern.** Authentication, API contracts, content policy, package management, migrations, and KPI definitions each have one authority.
5. **Controlled WIP.** One engineering phase or epic is active at a time unless independent capacity is named.
6. **Fail closed.** Security, privacy, identity, provider configuration, source content, and release provenance cannot degrade silently.
7. **Learner safety first.** Learner-facing AI content uses approved prompts, validation, safety controls, and human review.
8. **Small, reviewable changes.** Large migrations are decomposed and evidence is produced continuously.
9. **No downstream bypass.** A later phase cannot compensate for an unaccepted prerequisite phase.

---

## Mandatory Phase Execution and Closure Protocol

This protocol applies to every roadmap phase from Phase 0 through Phase 13. It also applies to any sub-phase or workstream that is given its own phase gate. The independent audit-remediation track may use its own document structure, but it must provide equivalent approved planning, implementation, evidence, and closure records before it can satisfy a programme dependency.

### Non-negotiable control rule

> **No approved execution plan, no phase start. No complete implementation report and evidence pack, no audit. No passing audit, no phase completion.**

The roadmap status register is controlled by this rule. A checkbox, code commit, local test, historical roadmap label, verbal approval, screenshot, or unexecuted script cannot substitute for the complete four-artefact control set.

### Required phase control set

Every phase must produce and obtain approval for a complete four-artefact control set:

```text
docs/roadmap/execution/phase_<NN>_execution_plan.md
docs/roadmap/execution/phase_<NN>_implementation_report.md
docs/release-evidence/phase-<NN>/phase_<NN>_evidence_index.md
docs/release-evidence/phase-<NN>/phase_<NN>_audit_report.md
```

The evidence directory may contain raw logs, machine-readable test results, screenshots, signed reviews, scan outputs, reports, manifests, hashes, and external-review documents. The evidence index is the authoritative manifest for that directory.

The four artefacts have different purposes and may not substitute for one another:

| Artefact | Purpose | Required approval |
|---|---|---|
| Execution plan | Defines intended scope, controls, acceptance criteria, evidence, audit method, ownership, and execution order before work starts | Phase Approver and Release Manager |
| Implementation report | Reconciles the approved plan against what was actually delivered and verified | Phase Owner and Phase Approver |
| Evidence pack/index | Provides attributable, reproducible proof for every acceptance criterion and report claim | Evidence Custodian and Phase Owner |
| Phase audit report | Independently tests the plan/report/evidence chain, identifies overstatement or gaps, and issues a closure verdict | Phase Auditor and Release Manager |

For Phase 13, the implementation report and evidence pack must also include the controlled-beta results, analysis dataset lineage, incident record, and final Go, Extend, or No-Go recommendation.

A phase with only a plan and report is incomplete. A phase with evidence but no audit is `Audit Pending`, not `Verified Complete`.

### Permitted phase status transitions

```text
Not Started
    ↓
Planning
    ↓  approved execution plan
Ready to Start
    ↓  authorised implementation begins
In Progress
    ↓  implementation frozen for verification
Verification Pending
    ↓  implementation report drafted and evidence pack frozen
Evidence Complete
    ↓  independent phase audit begins
Audit Review
    ↓  audit verdict = Pass and closure package approved
Closure Review
    ↓  approval on canonical merged source state
Verified Complete
```

`Blocked` and `Deferred` may be applied from any active state, but they require a recorded reason, owner, dependency or target date, and impact on downstream phases.

A phase may not move directly from `Not Started`, `Planning`, or `In Progress` to `Verified Complete`.

### Phase start gate — execution plan required

Before substantive implementation, infrastructure change, migration, content generation, external review execution, or beta activity begins, the phase owner must create an execution plan. Planning and non-mutating discovery are permitted only to produce the plan and baseline.

The execution plan must contain, at minimum:

- document control: phase, version, date, status, owner, approver, branch, base commit, and target milestone;
- objective and measurable phase outcome;
- confirmed dependencies and preconditions;
- pre-execution baseline tied to an identified source state and environment;
- in-scope and explicitly out-of-scope work;
- work breakdown, ordering, estimates, ownership, and WIP boundaries;
- acceptance criteria mapped to the governing roadmap phase exit criteria;
- required tests, evidence, review activities, and expected minimum test counts;
- security, privacy, safeguarding, accessibility, content, data, and operational considerations where applicable;
- migration, deployment, rollback, and recovery approach where applicable;
- risks, assumptions, external dependencies, and escalation triggers;
- evidence-output paths;
- change-control rules; and
- formal approval to start.

The start gate passes only when:

- [ ] the execution plan exists at the canonical path;
- [ ] every roadmap exit criterion is represented or explicitly marked not applicable with an approved rationale;
- [ ] dependencies and preconditions are satisfied or formally accepted;
- [ ] phase owner and approver are named;
- [ ] the plan status is `Approved for Execution`;
- [ ] the plan is committed before substantive phase implementation begins; and
- [ ] the programme status register is updated to `Ready to Start` or `In Progress` only after approval.

The execution plan must be the first controlled commit or first approved artefact of the phase. Discovery that changes production code, schemas, infrastructure, content, configuration, or external commitments counts as execution and is prohibited before approval.

### Execution-plan change control

The approved plan is a controlled baseline, not a disposable checklist.

- Material scope, acceptance-criterion, architecture, security, privacy, content, schedule, or dependency changes require an amendment recorded in the plan's change log before the changed work is accepted.
- A mandatory criterion may not be silently deleted, weakened, relabelled as complete, or moved to a later phase.
- Deferral requires an approved scope amendment identifying the deferred item, reason, impact, compensating control, new owner, target phase/date, and downstream-plan updates.
- Newly discovered work must be added to the plan or residual-defect register before closure.
- The implementation report must reconcile every approved amendment.

### Evidence-pack requirements

Before a phase can enter `Audit Review`, its evidence pack must be frozen and indexed. At minimum, the evidence index must record:

- phase, roadmap version, execution-plan version, implementation-report version, and evidence-pack version;
- canonical branch, base commit, merge commit, build or image digest, environment identity, and collection timestamp;
- every roadmap exit criterion and execution-plan acceptance criterion mapped to one or more evidence items;
- exact command or review method, expected result, actual result, exit code, duration, tool version, environment, and operator;
- test counts including passed, failed, skipped, xfailed, warnings, collection errors, and flaky retries;
- immutable CI, storage, vendor, or signed-document references where available;
- hashes for generated reports, manifests, datasets, images, binaries, and configuration exports;
- defects, exceptions, scope amendments, and revalidation triggers;
- evidence sensitivity classification, redaction status, access restrictions, and retention period; and
- a signed evidence-completeness declaration by the Evidence Custodian.

The evidence pack must contain raw or machine-readable output where practical. A prose summary, screenshot without source identity, unchecked checklist, or statement that a script exists is not sufficient proof. Evidence from a different commit or environment must be labelled contextual and cannot close a criterion without an approved equivalence argument.

### Independent phase audit requirements

Every phase requires a phase audit after the implementation report is drafted and the evidence pack is frozen. The audit must be performed by a person who was not the primary implementer whenever practical. In a single-developer context, the independence limitation must be disclosed and mitigated through reproducible commands, automated checks, an external reviewer, or a separately approved release reviewer.

The phase audit report must contain:

- auditor identity, role, competence, independence declaration, and conflicts of interest;
- audit scope, criteria, sampling method, tools, limitations, and source state;
- confirmation that the execution plan was approved before substantive work started;
- traceability checks across roadmap → plan → implementation report → evidence;
- independent reproduction or observation of critical gates;
- review of failures, warnings, skipped tests, deferred work, exceptions, and residual risks;
- assessment of security, privacy, safeguarding, accessibility, content, data, migration, deployment, operations, and rollback controls as applicable;
- findings classified as Critical, High, Medium, Low, or Observation;
- required corrective actions, owner, due date, and re-audit requirement; and
- one closure verdict: `Pass`, `Pass with non-blocking observations`, or `Fail`.

`Pass with non-blocking observations` may support closure only when all observations are explicitly non-mandatory, accepted by the Phase Approver, and entered into the debt/risk register. Critical or High findings, a failed mandatory criterion, missing evidence, unapproved scope change, or material report/evidence contradiction requires a `Fail` verdict.

### Phase completion gate — implementation report required

Before a phase can enter `Evidence Complete`, the phase owner must create an implementation report based on the approved execution plan and the exact source state being proposed for closure. Before it can enter `Closure Review`, the evidence pack must be frozen and the phase audit must issue a passing verdict.

The implementation report must contain, at minimum:

- document control: phase, date, owner, approver, execution-plan version, branch, base commit, merge commit, and evidence timestamp;
- original objective and approved scope;
- delivered work and files or non-code artefacts changed;
- a traceability matrix for every planned task, acceptance criterion, and phase exit criterion;
- planned-versus-actual effort and schedule;
- deviations, amendments, scope changes, and their approvals;
- exact verification commands, environments, tool versions, test counts, pass/fail/skip/xfail results, warnings, and CI links;
- security, privacy, safeguarding, accessibility, content-quality, data, migration, deployment, observability, and rollback results where applicable;
- unresolved defects, residual risks, exceptions, and deferred work;
- evidence index with repository-relative or immutable CI-artifact references;
- clean-source and release-identity statement; and
- explicit closure recommendation and approvals.

The completion gate passes only when:

- [ ] the implementation report exists at the canonical path;
- [ ] the evidence index exists, is complete, and maps every mandatory criterion to attributable proof;
- [ ] the phase audit report exists and its verdict is `Pass` or `Pass with non-blocking observations`;
- [ ] every approved execution-plan item is reconciled as `Passed`, `Approved Scope Change`, or `Not Applicable` with evidence and approval;
- [ ] no mandatory acceptance criterion remains failed, pending, unverified, or deferred;
- [ ] required tests and reviews executed rather than merely existing as scripts or documents;
- [ ] the implementation is merged into the canonical branch;
- [ ] required post-merge CI passes on the merge commit;
- [ ] evidence refers to that merge commit and the intended environment or artefact;
- [ ] residual defects and exceptions are within policy;
- [ ] the implementation report is approved by the accountable phase approver;
- [ ] the evidence pack is signed by the Evidence Custodian;
- [ ] the audit report is signed by the Phase Auditor and accepted by the Release Manager; and
- [ ] only after approval is the roadmap status changed to `Verified Complete`.

### Closure-integrity rules

A phase must not be marked complete when any of the following is true:

- the implementation PR is still open or the phase branch has not been merged;
- the report says `complete` while mandatory criteria remain unmet;
- planned work is described as deferred without a previously approved scope amendment;
- the target was not achieved but the report unilaterally redefines success;
- a verification script, workflow, runbook, or test file exists but was not successfully executed;
- evidence comes from a different commit, branch, environment, or artefact than the one being closed;
- required CI, external review, live verification, migration, rollback, or operational proof is still pending;
- warnings, skipped tests, collection failures, or known defects that affect the phase outcome are omitted or described as unrelated without assessment;
- predecessor completion is asserted without a valid predecessor implementation report and evidence package; or
- the implementation report contradicts its own Definition of Done.

`Code Complete`, `Implementation Complete`, `Locally Verified`, `Documentation Complete`, and `Ready for Review` are intermediate states. None is equivalent to `Verified Complete`.

### Phase closure review

The closure review considers the complete four-artefact phase-control set. It must verify:

1. the execution plan was approved before substantive execution;
2. the implementation report covers the approved plan and all amendments;
3. the evidence index is complete and the evidence is attributable, reproducible, protected, and sufficient;
4. the phase audit was sufficiently independent, reproduced critical controls, and issued a passing verdict;
5. all mandatory criteria pass and all audit findings are resolved or accepted within policy;
6. the canonical branch and post-merge CI are green;
7. residual risk is acceptable;
8. downstream assumptions, risks, estimates, and execution plans are updated; and
9. the phase status may safely change to `Verified Complete`.

The closure decision must be recorded in the implementation report's sign-off section or a linked immutable decision record.

### Enforcement in CI and programme reviews

The programme must add automated or scripted checks that, at minimum:

- fail a phase-start workflow when the canonical execution plan is missing or not marked `Approved for Execution`;
- fail a phase-close workflow when the implementation report, evidence index, or audit report is missing;
- verify the report references the approved execution-plan version;
- verify all mandatory closure checklist items are checked;
- reject `Verified Complete` in the status register when required artefacts are absent;
- verify evidence paths exist and the evidence index contains required source identity and criterion mappings;
- verify the audit verdict is passing and no blocking audit finding remains open; and
- ensure the phase report records the canonical merge commit.

Until automation exists, the Release Manager must enforce the same controls manually and record the review outcome.

### Required templates

The programme-controlled templates are:

- `docs/roadmap/execution/phase_execution_plan_template.md`
- `docs/roadmap/execution/phase_implementation_report_template.md`
- `docs/roadmap/execution/phase_evidence_pack_template.md`
- `docs/roadmap/execution/phase_audit_report_template.md`

A phase may extend these templates but may not omit mandatory control fields.

---

## Capacity and Scheduling Model

| Category | Hours/week | Notes |
|---|---:|---|
| Total available | 40 | Standard full-time capacity |
| Planned engineering | 26 | Direct programme delivery |
| Meetings and administration | 4 | Reviews, coordination, external calls |
| Documentation and evidence | 4 | ADRs, runbooks, evidence packages |
| Buffer and unplanned work | 6 | Defects and interruptions |

**Effective engineering throughput: approximately 26 hours per week.**

Parallel work is permitted only when named people can execute it independently. External legal, security-vendor, educator, and cohort preparation may overlap with engineering. Findings remediation competes for the same engineering capacity.

---

## Phase Status Register

| Phase | Outcome | Initial status | Execution plan | Implementation report | Evidence index | Audit report | Primary dependency | Provisional duration |
|---|---|---|---|---|---|---|---|---:|
| R | Independent audit remediation | Refer to its own roadmap | Equivalent approved remediation plan | Approved remediation implementation/closure report | Attributable remediation evidence index | Independent remediation closure audit or equivalent decision | Own workstream dependencies | Separate estimate |
| 0 | Reproducible environment, provider, flags, and worker foundation | Open — completion not established | `phase_00_execution_plan.md` | `phase_00_implementation_report.md` | `phase-00/phase_00_evidence_index.md` | `phase-00/phase_00_audit_report.md` | None | 1–2 weeks |
| 1 | Safe batch AI content generation | Open — completion not established | `phase_01_execution_plan.md` | `phase_01_implementation_report.md` | `phase-01/phase_01_evidence_index.md` | `phase-01/phase_01_audit_report.md` | Phase 0 | 2–4 weeks |
| 2 | Grounded semantic retrieval | Open — completion not established | `phase_02_execution_plan.md` | `phase_02_implementation_report.md` | `phase-02/phase_02_evidence_index.md` | `phase-02/phase_02_audit_report.md` | Phase 1 | 1–2 weeks |
| 3 | Multi-educator content consensus | Open — completion not established | `phase_03_execution_plan.md` | `phase_03_implementation_report.md` | `phase-03/phase_03_evidence_index.md` | `phase-03/phase_03_audit_report.md` | Phase 1 | 1–3 weeks |
| 4 | Adaptive-item calibration and self-healing controls | Open — completion not established | `phase_04_execution_plan.md` | `phase_04_implementation_report.md` | `phase-04/phase_04_evidence_index.md` | `phase-04/phase_04_audit_report.md` | Phases 2–3 | 2–3 weeks |
| 5 | Safe learner AI Tutor | Open — completion not established | `phase_05_execution_plan.md` | `phase_05_implementation_report.md` | `phase-05/phase_05_evidence_index.md` | `phase-05/phase_05_audit_report.md` | Phases 1 and 6 safety controls as applicable | 2–3 weeks |
| 6 | Monitoring, budget, and production hardening | Open — completion not established | `phase_06_execution_plan.md` | `phase_06_implementation_report.md` | `phase-06/phase_06_evidence_index.md` | `phase-06/phase_06_audit_report.md` | Phases 1–5 | 1–2 weeks |
| 7 | Beta content coverage and language readiness | Open — completion not established | `phase_07_execution_plan.md` | `phase_07_implementation_report.md` | `phase-07/phase_07_evidence_index.md` | `phase-07/phase_07_audit_report.md` | Phases 1–6 | 3–6 weeks |
| 8 | Architecture and codebase assurance | Open | `phase_08_execution_plan.md` | `phase_08_implementation_report.md` | `phase-08/phase_08_evidence_index.md` | `phase-08/phase_08_audit_report.md` | Phases 0–7 and required remediation controls | 5–8 weeks |
| 9 | CI authority and reproducible evidence | Open | `phase_09_execution_plan.md` | `phase_09_implementation_report.md` | `phase-09/phase_09_evidence_index.md` | `phase-09/phase_09_audit_report.md` | Phase 8 | 2–3 weeks |
| 10 | Product readiness | Open | `phase_10_execution_plan.md` | `phase_10_implementation_report.md` | `phase-10/phase_10_evidence_index.md` | `phase-10/phase_10_audit_report.md` | Phase 9 | 3–4 weeks |
| 11 | Operations readiness | Open | `phase_11_execution_plan.md` | `phase_11_implementation_report.md` | `phase-11/phase_11_evidence_index.md` | `phase-11/phase_11_audit_report.md` | Phase 9; normally after Phase 10 for one developer | 2–3 weeks |
| 12 | External review and governance | Open | `phase_12_execution_plan.md` | `phase_12_implementation_report.md` | `phase-12/phase_12_evidence_index.md` | `phase-12/phase_12_audit_report.md` | Preparation may start early; closure requires releasable system | 4–8 weeks |
| 13 | Controlled beta | Blocked | `phase_13_execution_plan.md` | `phase_13_implementation_report.md` | `phase-13/phase_13_evidence_index.md` | `phase-13/phase_13_audit_report.md` | Phases 0–12 and release gate | 5–6 weeks |

---

# Part I — Foundational Product Phases

## Phase 0 — Environment and Reproducibility


> **Mandatory phase control:** Phase 0 may not start until `docs/roadmap/execution/phase_00_execution_plan.md` is approved for execution. It may not be marked `Verified Complete` until its implementation report and evidence index are complete, its audit report has a passing verdict, and the full control set is approved against canonical post-merge evidence.

### Phase 0 required plan/report/evidence/audit set

| Control artefact | Phase-specific minimum requirements | Canonical path |
|---|---|---|
| Execution plan | Define the environment matrix, supported toolchain versions, canonical branch and source identity, secret/configuration ownership, provider and fallback policy, feature-flag defaults, worker/bootstrap requirements, clean-checkout setup, and failure/rollback tests. | `docs/roadmap/execution/phase_00_execution_plan.md` |
| Implementation report | Reconcile every environment and configuration decision; record actual versions, generated files, configuration changes, bootstrap behaviour, provider selection, worker startup, deviations, and setup defects. | `docs/roadmap/execution/phase_00_implementation_report.md` |
| Evidence pack and index | Clean-checkout setup transcript; tool/version inventory; configuration validation output; container and worker startup logs; provider fail-closed and fallback tests; secrets scan; environment parity matrix; hashes of lockfiles and generated configuration. | `docs/release-evidence/phase-00/phase_00_evidence_index.md` |
| Independent phase audit | Independently reproduce setup from a clean checkout, verify secrets are absent, validate fail-closed configuration and provider selection, compare local/CI/container settings, and confirm later phases can rely on the recorded baseline. | `docs/release-evidence/phase-00/phase_00_audit_report.md` |

**Phase 0 closure rule:** all four artefacts must exist, reference the same canonical source state, and be approved. The audit must issue a passing verdict and every blocking finding must be closed before the phase status can change to `Verified Complete`.

**Initial status:** Open — completion not established  
**Objective:** establish a reproducible, fail-closed environment for all later work.

### Required outcomes

- documented local, CI, container, staging, and production configuration model;
- canonical LLM provider and fallback configuration;
- feature flags and safe defaults for Content Factory generation;
- secret ownership through the approved secret-management mechanism;
- worker and scheduler infrastructure required by later phases;
- deterministic setup and preflight commands;
- environment identity and configuration evidence without exposing secrets.

### Exit criteria

- [ ] A clean checkout can install and start the required services using documented commands.
- [ ] Required provider, database, Redis, storage, and worker configuration is validated.
- [ ] Production configuration fails closed when a required value is absent or unsafe.
- [ ] Secrets are not committed, logged, or embedded in generated evidence.
- [ ] Worker infrastructure starts and exposes a health or verification signal.
- [ ] Phase 0 tests and preflight pass in CI or an approved equivalent environment.
- [ ] Evidence identifies commit, environment, toolchain, owner, and approver.

---

## Phase 1 — Batch AI Content Generation


> **Mandatory phase control:** Phase 1 may not start until `docs/roadmap/execution/phase_01_execution_plan.md` is approved for execution. It may not be marked `Verified Complete` until its implementation report and evidence index are complete, its audit report has a passing verdict, and the full control set is approved against canonical post-merge evidence.

### Phase 1 required plan/report/evidence/audit set

| Control artefact | Phase-specific minimum requirements | Canonical path |
|---|---|---|
| Execution plan | Define provider abstraction, prompt/version ownership, approved-source flow, output schemas, retry/fallback policy, safety and PII controls, deterministic CI provider, cost limits, telemetry, and generation acceptance dataset. | `docs/roadmap/execution/phase_01_execution_plan.md` |
| Implementation report | Record implemented providers, prompts, schema validators, safety controls, provenance, telemetry, generation runs, rejected outputs, fallback behaviour, costs, and all deviations from the approved design. | `docs/roadmap/execution/phase_01_implementation_report.md` |
| Evidence pack and index | Typed output test results; prompt and schema versions; source-provenance records; PII and unsafe-output tests; timeout/retry/fallback logs; deterministic CI results; complete generation-run output; token/cost telemetry; sampled rejected artefacts. | `docs/release-evidence/phase-01/phase_01_evidence_index.md` |
| Independent phase audit | Reproduce critical generation and failure paths, sample generated artefacts against their sources, verify PII/safety controls and publication fail-closed behaviour, and assess whether report claims match raw provider and validation evidence. | `docs/release-evidence/phase-01/phase_01_audit_report.md` |

**Phase 1 closure rule:** all four artefacts must exist, reference the same canonical source state, and be approved. The audit must issue a passing verdict and every blocking finding must be closed before the phase status can change to `Verified Complete`.

**Initial status:** Open — completion not established  
**Objective:** generate structured, grounded, CAPS-aligned content through a production-safe provider abstraction.

### Required outcomes

- canonical batch LLM provider implementation;
- provider fallback, timeout, retry, and circuit-breaker policy;
- structured schema validation and rejection handling;
- approved prompt templates and versioning;
- approved-source grounding and source provenance;
- PII redaction before external inference and before persistence where required;
- token, latency, provider, model, version, and rejection telemetry;
- deterministic test provider for CI.

### Exit criteria

- [ ] Diagnostic items, lessons, and any in-scope content types return validated typed outputs.
- [ ] Invalid or unsafe output is rejected and cannot be published automatically.
- [ ] Approved source context and prompt version are attributable for every generated artefact.
- [ ] Provider fallback and timeout behaviour are tested.
- [ ] PII/sensitive-data controls pass with failure-path tests.
- [ ] Cost and token telemetry is emitted without personal-data leakage.
- [ ] A complete generation run succeeds in a clean controlled environment.

---

## Phase 2 — Semantic Retrieval and Grounding


> **Mandatory phase control:** Phase 2 may not start until `docs/roadmap/execution/phase_02_execution_plan.md` is approved for execution. It may not be marked `Verified Complete` until its implementation report and evidence index are complete, its audit report has a passing verdict, and the full control set is approved against canonical post-merge evidence.

### Phase 2 required plan/report/evidence/audit set

| Control artefact | Phase-specific minimum requirements | Canonical path |
|---|---|---|
| Execution plan | Define embedding model/version and dimensions, approved corpus and filters, index and migration design, fallback conditions, retrieval evaluation dataset, quality thresholds, provenance propagation, backup, rollback, and reindex strategy. | `docs/roadmap/execution/phase_02_execution_plan.md` |
| Implementation report | Record schema/index changes, migration results, retrieval implementation, evaluation scores, filter behaviour, fallback activations, provenance propagation, performance, and recovery outcomes. | `docs/roadmap/execution/phase_02_implementation_report.md` |
| Evidence pack and index | Disposable-database schema and index proof; query plans; retrieval-quality dataset and metrics; unapproved-content exclusion tests; fallback tests; migration/restore/reindex logs; source-chunk provenance samples; performance results. | `docs/release-evidence/phase-02/phase_02_evidence_index.md` |
| Independent phase audit | Validate evaluation-dataset integrity and thresholds, reproduce retrieval and filtering, inspect query/index evidence, verify fallback cannot bypass approval rules, and trace sampled generated artefacts to source chunks. | `docs/release-evidence/phase-02/phase_02_audit_report.md` |

**Phase 2 closure rule:** all four artefacts must exist, reference the same canonical source state, and be approved. The audit must issue a passing verdict and every blocking finding must be closed before the phase status can change to `Verified Complete`.

**Initial status:** Open — completion not established  
**Objective:** retrieve approved source material accurately enough to ground generation and learner experiences.

### Required outcomes

- approved embedding model and vector dimensions;
- correct vector storage and index strategy;
- scope, status, curriculum, language, and permission filters;
- deterministic full-text or approved fallback behaviour;
- retrieval-quality test dataset and metrics;
- migration, backup, and rollback/forward-fix plan;
- source citation and provenance propagated to generated content.

### Exit criteria

- [ ] Vector schema and index are verified in a disposable database.
- [ ] Retrieval excludes unapproved or out-of-scope content.
- [ ] Fallback activates only under documented conditions.
- [ ] Retrieval-quality thresholds pass on the approved evaluation set.
- [ ] Migration and recovery tests pass.
- [ ] Generation can prove which source chunks informed an artefact.

---

## Phase 3 — Educator Consensus and Content Governance


> **Mandatory phase control:** Phase 3 may not start until `docs/roadmap/execution/phase_03_execution_plan.md` is approved for execution. It may not be marked `Verified Complete` until its implementation report and evidence index are complete, its audit report has a passing verdict, and the full control set is approved against canonical post-merge evidence.

### Phase 3 required plan/report/evidence/audit set

| Control artefact | Phase-specific minimum requirements | Canonical path |
|---|---|---|
| Execution plan | Define reviewer roles and independence, quorum, rubric, workflow states, duplicate-review prevention, correction/re-review policy, stale-review escalation, publication gate, audit retention, and reviewer-capacity assumptions. | `docs/roadmap/execution/phase_03_execution_plan.md` |
| Implementation report | Reconcile implemented workflow, roles, state transitions, review UI/process, approvals/rejections/quarantines, stale items, audit records, content-owner decisions, and deviations. | `docs/roadmap/execution/phase_03_implementation_report.md` |
| Evidence pack and index | State-machine and authorization tests; duplicate-review negative tests; sampled signed review records; immutable audit-chain proof; stale-review metrics; publication-gate tests; correction and quarantine demonstrations; approved rubric. | `docs/release-evidence/phase-03/phase_03_evidence_index.md` |
| Independent phase audit | Verify reviewer independence and role enforcement, reproduce quorum and negative paths, sample audit history and content decisions, confirm unapproved content cannot publish, and assess rubric application consistency. | `docs/release-evidence/phase-03/phase_03_audit_report.md` |

**Phase 3 closure rule:** all four artefacts must exist, reference the same canonical source state, and be approved. The audit must issue a passing verdict and every blocking finding must be closed before the phase status can change to `Verified Complete`.

**Initial status:** Open — completion not established  
**Objective:** ensure learner-facing generated content cannot bypass independent educational review.

### Required outcomes

- configurable review quorum;
- reviewer identity, role, independence, and duplicate-review controls;
- approve, reject, quarantine, correct, and re-review workflows;
- stale-review visibility and escalation;
- immutable or attributable audit history;
- content-owner rubric covering CAPS alignment, correctness, language, age appropriateness, bias, and safety;
- publication gate that fails closed.

### Exit criteria

- [ ] Fewer than the required independent approvals cannot publish an artefact.
- [ ] Duplicate or unauthorised review actions are rejected.
- [ ] Reject and quarantine actions remove content from learner availability.
- [ ] Corrections trigger the approved re-review policy.
- [ ] Stale items are measurable and owned.
- [ ] Audit history identifies the artefact, version, action, reviewer, and timestamp.
- [ ] Content-owner acceptance tests and workflow evidence pass.

---

## Phase 4 — IRT Quality and Self-Healing Controls


> **Mandatory phase control:** Phase 4 may not start until `docs/roadmap/execution/phase_04_execution_plan.md` is approved for execution. It may not be marked `Verified Complete` until its implementation report and evidence index are complete, its audit report has a passing verdict, and the full control set is approved against canonical post-merge evidence.

### Phase 4 required plan/report/evidence/audit set

| Control artefact | Phase-specific minimum requirements | Canonical path |
|---|---|---|
| Execution plan | Define IRT model, minimum sample/data-quality policy, calibration schedule, intervention thresholds, state machine, bias controls, idempotency, retries, manual override, rewrite review policy, dashboards, and statistical/content reviewers. | `docs/roadmap/execution/phase_04_execution_plan.md` |
| Implementation report | Record calibration implementation, model/version, sample checks, scheduled jobs, intervention results, retries, failures, quarantines, rewrites, dashboards, overrides, and deviations. | `docs/roadmap/execution/phase_04_implementation_report.md` |
| Evidence pack and index | Synthetic and approved historical calibration datasets; statistical test output; state-machine tests; answer-position bias tests; scheduler/restart/retry logs; quarantine serving tests; rewrite-to-review proof; intervention dashboard exports. | `docs/release-evidence/phase-04/phase_04_evidence_index.md` |
| Independent phase audit | Have a qualified statistical or assessment reviewer validate thresholds and samples; reproduce critical state transitions; verify healthy items remain unchanged, quarantined items are not served, and rewritten items cannot bypass human review. | `docs/release-evidence/phase-04/phase_04_audit_report.md` |

**Phase 4 closure rule:** all four artefacts must exist, reference the same canonical source state, and be approved. The audit must issue a passing verdict and every blocking finding must be closed before the phase status can change to `Verified Complete`.

**Initial status:** Open — completion not established  
**Objective:** monitor assessment-item performance and safely remove or correct low-quality items.

### Required outcomes

- approved IRT/calibration model and minimum sample policy;
- scheduled calibration workflow;
- explicit thresholds for retain, review, quarantine, retire, and rewrite;
- no answer-position bias or uncontrolled automatic mutation;
- human-review requirement for rewritten learner-facing content;
- idempotency, retries, job-state tracking, alerts, and manual override;
- quality and intervention dashboards.

### Exit criteria

- [ ] Calibration uses the approved minimum response count and data-quality checks.
- [ ] Healthy items are not changed by the intervention workflow.
- [ ] Low-quality items follow the approved state machine.
- [ ] Quarantined and retired items cannot be served.
- [ ] Rewritten items return to review rather than automatic publication.
- [ ] Scheduled execution, retries, failure alerts, and recovery are proven.
- [ ] Statistical and content-owner review accepts the intervention policy.

---

## Phase 5 — Learner AI Tutor


> **Mandatory phase control:** Phase 5 may not start until `docs/roadmap/execution/phase_05_execution_plan.md` is approved for execution. It may not be marked `Verified Complete` until its implementation report and evidence index are complete, its audit report has a passing verdict, and the full control set is approved against canonical post-merge evidence.

### Phase 5 required plan/report/evidence/audit set

| Control artefact | Phase-specific minimum requirements | Canonical path |
|---|---|---|
| Execution plan | Define supported learner journeys, context boundaries, authentication/ownership, prompt-injection and PII controls, response safety policy, streaming/cancellation, rate and budget limits, accessibility/browser matrix, fallback UX, quality evaluation, and escalation. | `docs/roadmap/execution/phase_05_execution_plan.md` |
| Implementation report | Record tutor implementation, context handling, safety filters, ownership checks, interaction results, failures, accessibility/browser results, rate/budget behaviour, quality scores, incidents, and deviations. | `docs/roadmap/execution/phase_05_implementation_report.md` |
| Evidence pack and index | Critical E2E journeys; authorization and cross-learner negative tests; PII/prompt-injection and unsafe-output tests; streaming/cancellation/provider-failure logs; browser/device results; accessibility report; rate/budget tests; sampled tutor-quality evaluation. | `docs/release-evidence/phase-05/phase_05_evidence_index.md` |
| Independent phase audit | Independently sample conversations and safety failures, reproduce ownership and fallback controls, review accessibility evidence, verify non-deceptive failure messaging, and assess whether quality and safeguarding thresholds are met. | `docs/release-evidence/phase-05/phase_05_audit_report.md` |

**Phase 5 closure rule:** all four artefacts must exist, reference the same canonical source state, and be approved. The audit must issue a passing verdict and every blocking finding must be closed before the phase status can change to `Verified Complete`.

**Initial status:** Open — completion not established  
**Objective:** deliver safe, context-aware, resilient interactive learner support.

### Required outcomes

- learner-context and lesson-context integration;
- streaming or equivalent interaction with cancellation and timeout handling;
- PII redaction and prompt-injection protections;
- age-appropriate safety policy and response validation;
- rate limits, token budgets, and abuse controls;
- connectivity-loss and provider-failure fallback;
- accessibility, browser, device, and critical-journey coverage;
- educator/content escalation for unsafe or low-quality responses.

### Exit criteria

- [ ] The learner can ask a question and receive a contextual response through the supported journey.
- [ ] Free text is processed under the approved privacy and safety controls.
- [ ] Unsafe, malformed, or policy-violating outputs fail safely.
- [ ] Connectivity and provider failures produce a usable, non-deceptive fallback.
- [ ] Rate, budget, authentication, and learner-ownership controls pass.
- [ ] Accessibility and critical interaction tests pass.
- [ ] Tutor-quality evaluation meets the approved threshold.

---

## Phase 6 — Monitoring, Budget, and Production Hardening


> **Mandatory phase control:** Phase 6 may not start until `docs/roadmap/execution/phase_06_execution_plan.md` is approved for execution. It may not be marked `Verified Complete` until its implementation report and evidence index are complete, its audit report has a passing verdict, and the full control set is approved against canonical post-merge evidence.

### Phase 6 required plan/report/evidence/audit set

| Control artefact | Phase-specific minimum requirements | Canonical path |
|---|---|---|
| Execution plan | Define telemetry schema and allowed fields, dashboards, alerts and owners, cost model and limits, production guards, secret/key rotation, security headers, dependency/configuration scanning, degradation modes, and runbook updates. | `docs/roadmap/execution/phase_06_execution_plan.md` |
| Implementation report | Record instrumentation, dashboards, alert routing/tests, budgets, production guards, security configuration, scans, key rotation, observed failure modes, runbooks, and deviations. | `docs/roadmap/execution/phase_06_implementation_report.md` |
| Evidence pack and index | Telemetry and dashboard exports; privacy-safe log samples; alert simulations and receipt proof; budget threshold/exhaustion tests; production mock-provider guard tests; security-header and configuration scans; secrets/dependency scan reports; rotation drill logs. | `docs/release-evidence/phase-06/phase_06_evidence_index.md` |
| Independent phase audit | Verify live metrics and alert delivery, inspect logs for personal-data leakage, reproduce budget and production guards, review security scans and key rotation, and confirm every critical background path is observable and owned. | `docs/release-evidence/phase-06/phase_06_audit_report.md` |

**Phase 6 closure rule:** all four artefacts must exist, reference the same canonical source state, and be approved. The audit must issue a passing verdict and every blocking finding must be closed before the phase status can change to `Verified Complete`.

**Initial status:** Open — completion not established  
**Objective:** make the product observable, cost-controlled, securely configured, and operationally bounded.

### Required outcomes

- application, background-job, AI, retrieval, review, and learner-journey telemetry;
- privacy-safe structured logging;
- provider and per-learner cost measurement;
- budget thresholds and hard/soft limits;
- production environment guards and removal of test/mock behaviour;
- security headers, secret rotation, dependency scanning, and configuration validation;
- initial dashboards and alerts with named owners;
- documented degradation and containment behaviour.

### Exit criteria

- [ ] Required metrics, traces, and logs are visible and privacy safe.
- [ ] Budget thresholds and exhaustion behaviour are tested.
- [ ] Production cannot use mock/deterministic providers unintentionally.
- [ ] Security and configuration controls pass in the intended deployment shape.
- [ ] Alert delivery is tested and owned.
- [ ] Failure modes and containment procedures are documented.
- [ ] No critical learner or admin path depends on unobservable background behaviour.

---

## Phase 7 — Beta Content Coverage and Language Readiness


> **Mandatory phase control:** Phase 7 may not start until `docs/roadmap/execution/phase_07_execution_plan.md` is approved for execution. It may not be marked `Verified Complete` until its implementation report and evidence index are complete, its audit report has a passing verdict, and the full control set is approved against canonical post-merge evidence.

### Phase 7 required plan/report/evidence/audit set

| Control artefact | Phase-specific minimum requirements | Canonical path |
|---|---|---|
| Execution plan | Define exact beta curriculum scope, coverage counts, source/version policy, generation and review capacity, educator rubric, language inclusion and reviewer qualifications, validation thresholds, launch manifest, correction/quarantine/rollback, and explicit exclusions. | `docs/roadmap/execution/phase_07_execution_plan.md` |
| Implementation report | Record content generated, approved, rejected, quarantined, corrected, and deferred; coverage by CAPS objective; language review; validation findings; reviewer signoffs; launch manifest; and deviations from scope. | `docs/roadmap/execution/phase_07_implementation_report.md` |
| Evidence pack and index | Versioned scope and coverage registry; source provenance; content inventory and hashes; coverage/duplication/readability/answer-key reports; signed educator reviews; language-review samples; launch manifest; quarantine and rollback demonstration. | `docs/release-evidence/phase-07/phase_07_evidence_index.md` |
| Independent phase audit | Independently sample content against CAPS and the rubric, verify counts and approval identities, confirm no unreviewed or out-of-scope content is in the launch manifest, and test content withdrawal and rollback. | `docs/release-evidence/phase-07/phase_07_audit_report.md` |

**Phase 7 closure rule:** all four artefacts must exist, reference the same canonical source state, and be approved. The audit must issue a passing verdict and every blocking finding must be closed before the phase status can change to `Verified Complete`.

**Initial status:** Open — completion not established  
**Objective:** create and approve the exact content slice required for the controlled beta.

### Beta content decision

The beta scope remains Grade 4 Mathematics, English primary. Other languages may be included only when the scope document, reviewer capacity, translation quality process, tests, and measurement plan explicitly support them.

LoRA or other fine-tuning is **not a beta prerequisite** unless a separate ADR proves it is required for quality, privacy, cost, or availability.

### Required outcomes

- versioned curriculum scope and coverage targets;
- complete source provenance for the beta content slice;
- generated and educator-approved diagnostic items and lessons;
- coverage, quality, duplication, answer-key, and readability checks;
- language-specific review where a language is included;
- content correction, quarantine, rollback, and publication controls;
- approved launch manifest tied to content versions.

### Exit criteria

- [ ] Every in-scope CAPS objective meets the approved coverage target.
- [ ] Every learner-facing artefact has the required educator approval.
- [ ] Content validation reports show no unresolved release-blocking defect.
- [ ] Included languages have qualified review and test evidence.
- [ ] The launch manifest identifies all content versions and approvals.
- [ ] Quarantine and rollback of content are proven.
- [ ] Deferred grades, subjects, languages, and fine-tuning are explicitly out of scope.

---

# Part II — Engineering Assurance and Release Authority

## Phase 8 — Architecture and Codebase Assurance


> **Mandatory phase control:** Phase 8 may not start until `docs/roadmap/execution/phase_08_execution_plan.md` is approved for execution. It may not be marked `Verified Complete` until its implementation report and evidence index are complete, its audit report has a passing verdict, and the full control set is approved against canonical post-merge evidence.

### Phase 8 required plan/report/evidence/audit set

| Control artefact | Phase-specific minimum requirements | Canonical path |
|---|---|---|
| Execution plan | Rebaseline against completed remediation, define architecture/domain rules, route and API inventory, code-quality policy, auth ownership, migration governance, exception policy, ticket sequence, and evidence/audit methods without duplicating already closed work. | `docs/roadmap/execution/phase_08_execution_plan.md` |
| Implementation report | Record dependency and route changes, code-quality results, auth consolidation decisions, migration controls, exceptions, actual effort, re-estimated downstream work, and any remediation overlap. | `docs/roadmap/execution/phase_08_implementation_report.md` |
| Evidence pack and index | Dependency graph and ownership map; import-linter output; route/OpenAPI inventory; duplicate-operation checks; code-quality reports; auth contract tests and coverage; migration graph/schema/upgrade evidence; ADRs and exception register. | `docs/release-evidence/phase-08/phase_08_evidence_index.md` |
| Independent phase audit | An architecture reviewer must verify contracts reflect the intended design rather than current accidents, sample route/auth/migration controls, confirm no hidden baseline suppresses defects, and validate the Phase 9 rebaseline. | `docs/release-evidence/phase-08/phase_08_audit_report.md` |

**Phase 8 closure rule:** all four artefacts must exist, reference the same canonical source state, and be approved. The audit must issue a passing verdict and every blocking finding must be closed before the phase status can change to `Verified Complete`.

### Objective

Establish durable architecture, ownership, route, code-quality, authentication, and migration governance on top of the remediated baseline.

The Phase 8 backlog must be rebaselined when the audit remediation gate closes. Work already completed by the remediation roadmap must not be recreated as duplicate Phase 8 tickets.

### Workstream A — Architecture boundary coverage

**Goal:** ensure automated architecture rules reflect the intended dependency model rather than only the currently configured contracts.

Deliverables:

- machine-readable dependency graph;
- documented layer and domain ownership rules;
- explicit allowed and prohibited dependency directions;
- CI enforcement for approved import contracts;
- owned plan for every confirmed violation;
- review of whether event, AI, compliance, content, and persistence boundaries require additional contracts.

Acceptance criteria:

- [ ] `DOMAIN_OWNERSHIP.md` identifies every material domain, owner, and allowed dependencies.
- [ ] Boundary rules are reviewed and approved.
- [ ] CI blocks new violations.
- [ ] Existing approved exceptions have owners and removal milestones.

### Workstream B — Route and API governance

**Goal:** maintain one authoritative route location and an intentional, versioned API surface.

Deliverables:

- route inventory generated from the canonical runtime;
- duplicate path/method and operation-ID detection;
- route ownership map;
- API deprecation policy;
- deterministic OpenAPI generation and review process;
- compatibility-alias expiry rules.

Acceptance criteria:

- [ ] Every public route has an owner and canonical module.
- [ ] Duplicate route registrations and operation IDs are zero.
- [ ] Deprecated routes are marked, measured, and assigned removal dates.
- [ ] OpenAPI changes are reviewed as part of pull requests.

### Workstream C — Code-quality baseline

**Goal:** adopt a transparent, enforceable code-quality policy without disguising unresolved defects behind a broad baseline.

Severity policy:

| Class | Treatment |
|---|---|
| Security and correctness defects | Must be fixed before merge unless a specifically permitted exception exists |
| Undefined names, invalid syntax, broken imports | Always blocking |
| Unused or dead production code | Blocking unless intentionally retained and documented |
| Complexity and maintainability findings | Remediate to agreed thresholds or create an owned debt item |
| Formatting and low-risk style findings | Automated or advisory according to the agreed tool configuration |

Acceptance criteria:

- [ ] Blocking rules are documented in one configuration.
- [ ] New blocking findings fail CI.
- [ ] Suppressions include a reason and are periodically reviewed.
- [ ] Code-quality reports are attributable to the exact commit.

### Workstream D — Authentication ownership

**Goal:** preserve one canonical authentication and token-lifecycle model.

Deliverables:

- named canonical owner and module;
- token contract covering issuance, refresh, expiry, revocation, audience, issuer, type, and key rotation;
- compatibility-path inventory and retirement plan;
- protected-route and cross-session security tests;
- architecture controls preventing reintroduction of retired paths.

Acceptance criteria:

- [ ] One token and session contract is approved.
- [ ] Login, registration, refresh, expiry, revocation, and protected-route tests pass.
- [ ] Compatibility code is isolated and has a removal milestone.
- [ ] Auth-related code meets at least 90% line coverage or an equivalent risk-based test standard.

### Workstream E — Migration governance

**Goal:** make database changes safe, reviewable, and reversible where policy allows.

The current plan does **not** require a pre-beta migration-history squash by default. A squash may proceed only through an approved ADR demonstrating that its benefits exceed its release risk.

Deliverables:

- migration authoring rules;
- upgrade-path verification from supported environments;
- disposable-database CI testing;
- backup requirement for high-risk schema changes;
- rollback or forward-fix policy;
- schema compatibility requirements for application rollback;
- decision on migration retention or consolidation.

Acceptance criteria:

- [ ] Migration graph and schema checks are required CI controls.
- [ ] New migrations apply from a clean database.
- [ ] Supported upgrade paths are documented and tested.
- [ ] High-risk changes have backup, recovery, and rollback/forward-fix plans.
- [ ] Any squash has a separately approved ADR and successful staging rehearsal.

### Phase 8 exit criteria

- [ ] Architecture and domain ownership maps are approved.
- [ ] Import contracts enforce the intended design.
- [ ] Public routes have canonical ownership and no duplicate registrations.
- [ ] Blocking code-quality findings are zero.
- [ ] Authentication ownership and compatibility retirement are documented.
- [ ] Migration governance is approved and verified.
- [ ] All evidence is archived under `docs/release-evidence/phase-08/`.
- [ ] Phase 9 backlog is re-estimated from actual Phase 8 throughput.

---

## Phase 9 — CI Authority and Reproducible Evidence


> **Mandatory phase control:** Phase 9 may not start until `docs/roadmap/execution/phase_09_execution_plan.md` is approved for execution. It may not be marked `Verified Complete` until its implementation report and evidence index are complete, its audit report has a passing verdict, and the full control set is approved against canonical post-merge evidence.

### Phase 9 required plan/report/evidence/audit set

| Control artefact | Phase-specific minimum requirements | Canonical path |
|---|---|---|
| Execution plan | Define canonical branch, workflow ownership, package manager and lockfiles, required checks, coverage/test policy, security gates, disposable services, artifact retention, branch protection, failure-injection tests, and evidence provenance. | `docs/roadmap/execution/phase_09_execution_plan.md` |
| Implementation report | Record workflow changes, required checks, test/coverage results, build artifacts, branch rules, green runs, failure-injection results, evidence retention, exceptions, and deviations. | `docs/roadmap/execution/phase_09_implementation_report.md` |
| Evidence pack and index | Validated workflow files; package-manager/lockfile proof; branch-protection export; at least three consecutive green canonical-branch runs where required; full test/coverage/security/build logs; failing control fixtures; CI artifacts; commit/image/source identity. | `docs/release-evidence/phase-09/phase_09_evidence_index.md` |
| Independent phase audit | Independently inspect and rerun critical CI gates, verify failures cannot be suppressed, validate required checks and branch protection, confirm evidence belongs to the exact commit, and test that a seeded defect fails the pipeline. | `docs/release-evidence/phase-09/phase_09_audit_report.md` |

**Phase 9 closure rule:** all four artefacts must exist, reference the same canonical source state, and be approved. The audit must issue a passing verdict and every blocking finding must be closed before the phase status can change to `Verified Complete`.

### Objective

Make CI the authoritative quality and release-control system for the canonical default branch.

### Required CI gates

| Gate | Minimum policy |
|---|---|
| Backend unit and integration tests | Passing; overall backend line coverage at least 80% |
| High-risk backend areas | Auth, privacy, security, consent, and payment paths at least 90% coverage or approved risk-based equivalent |
| Frontend unit tests | Passing; line coverage at least 70% |
| API integration coverage | All public routes mapped to tests; critical routes include success and failure cases |
| Contract tests | All external provider and frontend/backend boundaries covered |
| Type and static checks | Passing under approved configurations |
| Architecture checks | No unapproved violations |
| Migration and schema checks | Passing against disposable database infrastructure |
| API contract | Deterministic OpenAPI and client-contract gates pass |
| Security checks | Secrets, SAST, dependency, and configuration checks pass at approved thresholds |
| Build checks | Backend and frontend release artefacts build reproducibly |
| Deployment smoke test | Staging deployment and critical health checks pass |

### Test-policy alignment

The canonical coverage policy is:

- backend overall: **at least 80% line coverage**;
- high-risk backend domains: **at least 90%**, or an approved risk-based test matrix;
- frontend overall: **at least 70% line coverage**;
- API coverage: every public route mapped to automated tests;
- critical learner journey: end-to-end coverage;
- no release-critical suite may pass by selecting zero tests.

### Security scan cadence

- SAST, secrets scanning, dependency policy, configuration validation, and lightweight security tests run on pull requests.
- Full DAST runs against staging on a scheduled and pre-release basis, not on every pull request.
- External penetration testing remains a Phase 12 release requirement.

### Evidence requirements

Every required CI run records:

- branch and commit SHA;
- workflow and tool versions;
- test count and coverage;
- artefact identifiers;
- environment or runner identity;
- result and duration;
- links to machine-readable reports.

### Phase 9 exit criteria

- [ ] Three consecutive required CI runs are green on the canonical default branch.
- [ ] Branch protection requires all mandatory checks.
- [ ] Coverage policy is enforced consistently.
- [ ] Release artefacts are built once and promoted without rebuilding.
- [ ] Staging smoke tests run against the built release artefact.
- [ ] Release evidence is attributable and reproducible.
- [ ] Failure suppression is governed by the approved exception process.

---

# Part III — Product and Operations Readiness

## Phase 10 — Product Readiness


> **Mandatory phase control:** Phase 10 may not start until `docs/roadmap/execution/phase_10_execution_plan.md` is approved for execution. It may not be marked `Verified Complete` until its implementation report and evidence index are complete, its audit report has a passing verdict, and the full control set is approved against canonical post-merge evidence.

### Phase 10 required plan/report/evidence/audit set

| Control artefact | Phase-specific minimum requirements | Canonical path |
|---|---|---|
| Execution plan | Define frozen beta scope, critical E2E journeys, browser/device matrix, accessibility method, performance profile, analytics taxonomy, content readiness, survey/feedback validation, support UX, and defect thresholds. | `docs/roadmap/execution/phase_10_execution_plan.md` |
| Implementation report | Record E2E, browser, accessibility, performance, analytics, content, survey, support, and usability results; defects; retests; scope changes; and product signoffs. | `docs/roadmap/execution/phase_10_implementation_report.md` |
| Evidence pack and index | E2E reports and videos/traces; browser/device matrix; automated and manual accessibility reports; load/performance outputs; analytics event captures; content-review signoffs; survey/feedback test records; usability defect register and retests. | `docs/release-evidence/phase-10/phase_10_evidence_index.md` |
| Independent phase audit | Independent QA/product/content reviewers must trace scope to journeys and evidence, reproduce selected critical flows, inspect accessibility and performance methods, verify content signoff, and confirm no critical product defect remains. | `docs/release-evidence/phase-10/phase_10_audit_report.md` |

**Phase 10 closure rule:** all four artefacts must exist, reference the same canonical source state, and be approved. The audit must issue a passing verdict and every blocking finding must be closed before the phase status can change to `Verified Complete`.

### Objective

Demonstrate that the complete beta experience is usable, accessible, performant, measurable, and content-ready for the frozen beta scope.

### Critical learner and guardian journeys

Automated E2E coverage must include:

1. account creation or onboarding;
2. parent/guardian consent;
3. learner authentication;
4. diagnostic assessment;
5. lesson recommendation and completion;
6. progress persistence;
7. parent dashboard review;
8. privacy-request initiation where included in the beta interface;
9. feedback submission;
10. session expiry and recovery.

At least three scenario families must cover happy path, policy/validation denial, and recoverable failure behaviour.

### Product gates

- cross-browser testing for supported Chrome, Edge, Firefox, and Safari versions;
- desktop and tablet viewport validation;
- WCAG 2.1 AA automated and manual review of critical journeys;
- performance testing against the agreed beta load profile;
- beta analytics event validation;
- content review completion;
- survey and feedback mechanism validation;
- support contact visibility and escalation paths;
- no unresolved critical usability defect.

### Content readiness

All learner-facing Grade 4 Mathematics content in beta scope must:

- map to the agreed CAPS domain and objective;
- identify its source and version;
- pass the approved educator/content review rubric;
- have no unresolved critical factual, pedagogical, safety, or language error;
- support traceable correction and republication;
- distinguish authored, generated, and translated content.

### Localization decision

The controlled beta is **English-primary**.

- The internationalisation framework may be implemented in Phase 10.
- isiZulu and Afrikaans may be used for reviewed interface experiments or future preparation.
- Full translated curriculum delivery is outside the beta unless separately approved through scope change and educator review.
- Machine translation alone is not sufficient approval for learner-facing content.

### Phase 10 exit criteria

- [ ] Critical E2E journeys pass on the supported browser matrix.
- [ ] No critical accessibility violation remains.
- [ ] Performance meets the beta profile.
- [ ] All beta content is reviewed and signed off.
- [ ] Analytics, surveys, and feedback capture are proven end to end.
- [ ] Beta scope is frozen and traceable to tests and content inventory.

---

## Phase 11 — Operations Readiness


> **Mandatory phase control:** Phase 11 may not start until `docs/roadmap/execution/phase_11_execution_plan.md` is approved for execution. It may not be marked `Verified Complete` until its implementation report and evidence index are complete, its audit report has a passing verdict, and the full control set is approved against canonical post-merge evidence.

### Phase 11 required plan/report/evidence/audit set

| Control artefact | Phase-specific minimum requirements | Canonical path |
|---|---|---|
| Execution plan | Define SLO/SLI queries and windows, dashboard/alert ownership, backup and retention, restore and rollback drills, runbooks, on-call/escalation, incident simulation, evidence retention, RTO/RPO, and first-72-hours monitoring. | `docs/roadmap/execution/phase_11_execution_plan.md` |
| Implementation report | Record implemented SLOs, dashboards, alerts, backup/restore/rollback results, runbooks, on-call acceptance, incident exercise, achieved RTO/RPO, failures, and deviations. | `docs/roadmap/execution/phase_11_implementation_report.md` |
| Evidence pack and index | Dashboard and alert configuration exports; alert receipt tests; backup hashes and logs; restore row/integrity comparisons; rollback timing and smoke tests; runbook approvals; on-call roster; incident-exercise record; privacy-safe operational logs. | `docs/release-evidence/phase-11/phase_11_evidence_index.md` |
| Independent phase audit | An operations reviewer must observe or independently repeat critical restore/rollback/alert drills, verify RTO/RPO claims, inspect runbook usability and ownership, and confirm evidence retention and logging are safe and sufficient. | `docs/release-evidence/phase-11/phase_11_audit_report.md` |

**Phase 11 closure rule:** all four artefacts must exist, reference the same canonical source state, and be approved. The audit must issue a passing verdict and every blocking finding must be closed before the phase status can change to `Verified Complete`.

### Objective

Prove that the platform can be observed, supported, restored, rolled back, and operated safely during the controlled beta.

### Service objectives

| Measure | Beta target | Alert or review threshold |
|---|---:|---:|
| Availability | At least 99.5% | Review below 99.5%; mandatory action below 99.0% |
| P95 API latency | Below 500 ms | Warning above 750 ms; critical above 1 second sustained |
| 5xx error rate | Below 1% | Alert above agreed rolling threshold |
| Recovery Time Objective | Below 4 hours | Restore drill must demonstrate capability |
| Recovery Point Objective | At most 24 hours | Aligned with verified backup schedule |
| Critical learner-journey success | At least 98% synthetic success | Alert on sustained failure |

Thresholds must be translated into explicit queries, windows, and alert routing before Phase 11 closes.

### Required operational controls

- Azure Application Insights/OpenTelemetry telemetry for APIs, jobs, dependencies, and AI calls;
- Grafana or approved dashboard layer for error, latency, throughput, dependencies, database, cache, and AI-cost views;
- tested alerts and named on-call ownership;
- daily database backups and documented retention;
- full staging restore test from the latest backup;
- rollback rehearsal using the release candidate;
- runbooks for deployment, rollback, restore, privacy requests, AI-provider failure, content correction, and incidents;
- incident severity model and communication procedure;
- first-72-hours beta monitoring plan;
- privacy-safe logging and evidence retention.

### Phase 11 exit criteria

- [ ] Dashboards and alerts are active and tested.
- [ ] Backup and restore drills pass.
- [ ] Rollback completes within the agreed two-hour objective.
- [ ] Runbooks are approved and accessible.
- [ ] On-call and escalation responsibilities are accepted.
- [ ] Incident simulation results are archived.
- [ ] Operational evidence is stored under `docs/release-evidence/phase-11/`.

---

# Part IV — Security, Privacy, AI, and Content Governance

## Phase 12 — External Review and Governance


> **Mandatory phase control:** Phase 12 may not start until `docs/roadmap/execution/phase_12_execution_plan.md` is approved for execution. It may not be marked `Verified Complete` until its implementation report and evidence index are complete, its audit report has a passing verdict, and the full control set is approved against canonical post-merge evidence.

### Phase 12 required plan/report/evidence/audit set

| Control artefact | Phase-specific minimum requirements | Canonical path |
|---|---|---|
| Execution plan | Define external reviewers/vendors, review scopes, release-candidate environment, legal and DPA deliverables, educator and AI-governance reviews, finding classification, remediation SLAs, retest rules, independence, scheduling, and evidence custody. | `docs/roadmap/execution/phase_12_execution_plan.md` |
| Implementation report | Record reviews performed, reviewer identities, findings, remediation, retests, signed legal/DPA/content/AI decisions, unresolved items, exceptions, dates, environment identity, and deviations. | `docs/roadmap/execution/phase_12_implementation_report.md` |
| Evidence pack and index | Signed POPIA opinion and legal records; DPA tracker and executed agreements; penetration-test scope/report/retest; educator signoffs; AI-governance review; consent/data-rights walkthroughs; finding register; remediation PRs and verification; authenticity and expiry metadata. | `docs/release-evidence/phase-12/phase_12_evidence_index.md` |
| Independent phase audit | A governance/release reviewer must verify documents are authentic, current, scoped to the release candidate, and independent; confirm all Critical/High findings are closed; reconcile conflicts among legal, security, content, and engineering evidence. | `docs/release-evidence/phase-12/phase_12_audit_report.md` |

**Phase 12 closure rule:** all four artefacts must exist, reference the same canonical source state, and be approved. The audit must issue a passing verdict and every blocking finding must be closed before the phase status can change to `Verified Complete`.

### Objective

Obtain independent assurance and formal signoff for privacy, security, educational content, and AI controls before beta launch.

### Phase 12A — Preparation and review

Start procurement and scheduling before Phase 12 so vendor lead time does not become the critical path.

Required activities:

- external POPIA review;
- signed Data Processing Agreements where required;
- data-flow and retention review;
- data-subject request walkthrough;
- external penetration test against the release-candidate staging environment;
- educator review of all beta content;
- AI safety, prompt, output-validation, and review-process assessment;
- review of learner safeguarding and incident escalation;
- review of consent records and auditability.

### Phase 12B — Findings remediation

Every finding must have:

- severity and rationale;
- owner;
- target date;
- remediation or risk-treatment decision;
- retest evidence;
- approver;
- release impact.

Critical and High security, privacy, consent, safeguarding, or educational correctness findings are non-waivable for beta.

### AI governance requirements

- provider-neutral gateway and approved fallback policy;
- prompt templates under version control;
- structured output validation;
- age-appropriate safety policies;
- human approval for publishable learner content;
- privacy-safe AI request and response audit records;
- model, prompt version, latency, token, cost, and rejection metrics;
- provider outage and unsafe-output procedures;
- retention and access controls for AI audit data.

### Phase 12 exit criteria

- [ ] External POPIA review is signed off.
- [ ] Penetration test is complete and required retests pass.
- [ ] No unresolved Critical or High finding remains.
- [ ] DPAs and required legal documents are signed.
- [ ] All beta content has educator approval.
- [ ] AI governance controls are tested and approved.
- [ ] Consent and data-rights evidence is complete.
- [ ] Findings closure evidence is archived under `docs/release-evidence/phase-12/`.

---

# Part V — Controlled Beta

## Phase 13 — Controlled Beta


> **Mandatory phase control:** Phase 13 may not start until `docs/roadmap/execution/phase_13_execution_plan.md` is approved for execution. It may not be marked `Verified Complete` until its implementation report and evidence index are complete, its audit report has a passing verdict, and the full control set is approved against canonical post-merge evidence.

### Phase 13 required plan/report/evidence/audit set

| Control artefact | Phase-specific minimum requirements | Canonical path |
|---|---|---|
| Execution plan | Define cohort eligibility and recruitment, consent and safeguarding, onboarding, measurement and analysis plan, KPI formulas and data lineage, support/on-call, stop rules, incident handling, scope control, communication, monitoring cadence, beta exit and decision method. | `docs/roadmap/execution/phase_13_execution_plan.md` |
| Implementation report | Record actual cohort and consent, onboarding, usage, learning and engagement results, reliability, safety incidents, privacy requests, support, survey results, deviations/interventions, data-quality limits, and Go/Extend/No-Go recommendation. | `docs/roadmap/execution/phase_13_implementation_report.md` |
| Evidence pack and index | Cohort and consent manifests; de-identified KPI extracts and query/version lineage; baseline/follow-up assessment results; uptime/latency/error dashboards; AI/content safety records; support and incident logs; survey datasets; privacy-request log; analysis notebook/report; decision minutes and signoffs. | `docs/release-evidence/phase-13/phase_13_evidence_index.md` |
| Independent phase audit | An independent beta-results reviewer must reproduce KPI calculations from approved data, verify consent and cohort inclusion, assess missing data and intervention bias, reconcile incidents and support logs, and confirm the final recommendation follows the pre-approved decision framework. | `docs/release-evidence/phase-13/phase_13_audit_report.md` |

**Phase 13 closure rule:** all four artefacts must exist, reference the same canonical source state, and be approved. The audit must issue a passing verdict and every blocking finding must be closed before the phase status can change to `Verified Complete`.

### 12.1 Beta objective

Validate that EduBoost provides a secure, privacy-compliant, operationally stable, educationally appropriate, and meaningfully useful Grade 4 Mathematics experience for a controlled South African cohort.

### 12.2 In scope

#### Learner features

- diagnostic assessment;
- adaptive AI-tutor lessons through the approved AI Gateway;
- lesson completion and progress tracking;
- learner results and recommendations;
- parent/guardian progress dashboard.

#### Curriculum

Grade 4 Mathematics content covering:

- Numbers, Operations and Relationships;
- Patterns, Functions and Algebra;
- Space and Shape;
- Measurement;
- Data Handling.

English is the primary learner language for beta. Unreviewed machine-translated curriculum content is not included.

#### Platform

- responsive web application;
- supported desktop and tablet browsers;
- email/password authentication through the canonical model;
- parent/guardian consent capture and audit trail;
- privacy-request support for the approved beta workflows;
- analytics required by the approved measurement plan.

#### Support and feedback

- email-based beta support during published hours;
- 24-hour response objective during those hours;
- in-application feedback;
- structured learner/parent/educator survey process;
- incident and safeguarding escalation.

### 12.3 Out of scope

| Item | Position |
|---|---|
| Grade 5 or additional subjects | Post-beta |
| Native iOS or Android applications | Post-beta |
| Offline learning mode | Post-beta |
| Teacher/educator portal | Post-beta; educator processes may be manual during beta |
| Parent mobile push notifications | Post-beta |
| Social login | Post-beta unless separately approved |
| Gamification and leaderboards | Excluded to avoid confounding core-value measurement |
| Marketplace or third-party content | Not planned for beta |
| Real-time learner collaboration | Post-beta |
| Full multilingual curriculum delivery | Post-beta unless formally added through scope control |

### 12.4 Cohort design

| Parameter | Plan |
|---|---|
| Minimum operational cohort | 50 consented learners |
| Maximum cohort | 200 learners |
| Educators | Approximately 5 |
| Schools | 1–3 partner schools |
| Active beta duration | 30 consecutive days |
| Analysis period | Up to 5 business days after beta close |
| Eligibility | Grade 4 learner, partner-school participation, valid parent/guardian consent |

The minimum cohort is an operational pilot threshold, not a guarantee of statistical significance. Before recruitment, the Product Owner must approve:

- primary and secondary outcomes;
- analysis population;
- baseline and follow-up instruments;
- missing-data treatment;
- minimum response counts;
- school/cohort segmentation;
- rules for mid-beta intervention;
- the decision framework.

### 12.5 Beta success criteria

#### Engagement and experience

| Criterion | Target | Minimum acceptable |
|---|---:|---:|
| Diagnostic completion | Above 80% | At least 65% |
| Lesson completion | Above 70% | At least 55% |
| 7-day learner retention | Above 40% | At least 25% |
| Educator satisfaction | Above 80% positive | At least 60% positive |
| Parent satisfaction | Above 80% positive | At least 60% positive |
| Support requests answered within objective | Above 90% | At least 80% |

Survey measures require a predefined minimum valid response count and a documented scoring method.

#### Educational outcome

The approved measurement plan must define one primary educational outcome. Recommended starting measures are:

| Criterion | Target | Minimum acceptable |
|---|---:|---:|
| Median diagnostic-to-follow-up mastery gain | At least 10 percentage points | At least 5 percentage points |
| Learners with a positive mastery change | At least 65% | At least 50% |
| Critical factual or curriculum errors in delivered content | 0 | 0 |
| Material non-critical content error rate | Below 1% of reviewed learner-facing items | Below 2% |

These thresholds must be validated by the Content Owner and Product Owner before data collection. The beta should report confidence intervals and cohort limitations rather than claim broad causal impact.

#### Reliability and performance

| Criterion | Target | Minimum acceptable |
|---|---:|---:|
| Platform availability | Above 99.5% | At least 99.0% |
| P95 API response time | Below 500 ms | Below 1 second |
| Critical learner-journey synthetic success | At least 98% | At least 95% |
| Successful scheduled backup completion | 100% | 100% |
| Critical data-integrity incident | 0 | 0 |

#### Safety, privacy, and AI quality

| Criterion | Target | Minimum acceptable |
|---|---:|---:|
| Critical security, privacy, consent, or safeguarding incident | 0 | 0 |
| Confirmed cross-learner data exposure | 0 | 0 |
| Unsafe learner-facing AI response with Critical severity | 0 | 0 |
| Learner-facing content delivered without required approval | 0 | 0 |
| Structured AI-output validation success | Above 98% | At least 95% |
| AI-provider fallback success in planned test | 100% | 100% |

### 12.6 Decision bands

- **Green — Go candidate:** all targets met, or minor target misses with all minimums and all non-waivable controls met.
- **Amber — Extend or remediate:** all non-waivable controls and minimums met, but one or more targets missed or evidence is inconclusive. A time-boxed extension or remediation plan is required.
- **Red — No-Go:** any non-waivable control fails, any critical incident occurs, or any minimum criterion is missed without an approved measurement-quality explanation.

A production decision is not automatic even when beta targets are met. Cost, supportability, residual risk, content readiness, and external review findings remain part of the decision.

### 12.7 Scope change control

The beta scope must be frozen before Phase 10 implementation is finalised.

Any proposed addition requires:

1. written request;
2. impact on timeline, capacity, privacy, security, content review, analytics, and support;
3. approval by Product, Engineering, and any affected control owner;
4. updated tests, evidence, measurement plan, and communications;
5. documented decision.

Default rule: **if it is not explicitly included, it is out of scope.**

---

# Part VI — Architecture and Risk Governance

## Architecture Decision Governance

The ADR repository remains the detailed decision log. The following programme-level status should be adopted:

| ADR | Programme position |
|---|---|
| ADR-001 Authentication Strategy | Accepted; one canonical native Postgres/JWT lifecycle, with compatibility retirement controlled separately |
| ADR-002 AI Provider Strategy | Accepted; operational fallback, data handling, and cost controls require verification |
| ADR-003 Content Governance | Accepted with wording amendment: human approval is an EduBoost quality and learner-safety control; legal claims require external legal support |
| ADR-004 Event Architecture | Proposed until one event technology and delivery model are selected |
| ADR-005 Deployment Strategy | Proposed until one Azure Container Apps traffic and rollback strategy is selected |
| ADR-006 Migration Strategy | Proposed; pre-beta squash is not mandatory without a separate evidence-based approval |
| ADR-007 Observability Strategy | Accepted; implementation and alert ownership remain phase gates |
| ADR-008 Testing Toolchain | Accepted with clarification: full DAST is scheduled/pre-release, not per pull request |
| ADR-009 Localization | Accepted with clarification: framework preparation is allowed; controlled beta remains English-primary |

### ADR-004 amendment requirements

The final event decision must define:

- selected technology;
- event schema ownership and versioning;
- delivery semantics;
- ordering assumptions;
- retries and dead-letter handling;
- idempotency;
- retention;
- replay controls;
- personal-data classification and redaction;
- operational ownership and cost.

### ADR-005 amendment requirements

The final deployment decision must define:

- revision, blue-green, or equivalent mechanism;
- health and promotion criteria;
- traffic-shift process;
- rollback trigger and authority;
- database compatibility requirements;
- artefact provenance;
- staging-to-production parity.

### ADR-006 decision rule

Migration history consolidation may proceed only when:

- supported environments are inventoried;
- measurable benefit is demonstrated;
- upgrade and rollback/forward-fix paths are proven;
- backup and restore controls pass;
- the risk is approved by Engineering and Operations;
- it does not threaten beta readiness.

### Minimum ADR template

Every ADR must include:

- title and status;
- owner and approvers;
- date;
- context and problem;
- considered alternatives;
- decision;
- security, privacy, operational, cost, and migration consequences;
- implementation and rollback plan;
- evidence required for acceptance;
- replacement or deprecation relationship.

---

## Programme Risk Register

Probability and impact use the existing 1–5 scale; exposure equals probability multiplied by impact.

| ID | Risk | P | I | Exposure | Accountable owner | Treatment |
|---|---|---:|---:|---:|---|---|
| R-000 | Roadmap status inheritance falsely marks incomplete phases as complete | 5 | 5 | 25 | Release Manager | Reset all phase statuses; require phase-level evidence; prohibit inherited completion labels; reconcile status weekly |
| R-001 | Single-developer throughput and key-person dependency | 5 | 4 | 20 | Engineering Lead | WIP limit, weekly capacity review, documentation, backup reviewer, early escalation |
| R-002 | External POPIA, DPA, or legal review delay | 4 | 5 | 20 | Compliance Owner | Procure early, prepare data maps, reserve remediation capacity, maintain legal evidence checklist |
| R-003 | Audit-remediation track closes later than planned | 4 | 5 | 20 | Release Manager | Track independently, report weekly, prevent duplicate work, rebaseline programme on closure |
| R-004 | Phases 0–7 contain more unfinished work than historical roadmaps indicate | 4 | 5 | 20 | Engineering Lead | Run acceptance-based inventory; credit only proven work; re-estimate after every phase verification |
| R-005 | Security or penetration-test findings delay beta | 4 | 4 | 16 | Security Owner | Early threat modelling, continuous controls, vendor booking, remediation buffer |
| R-006 | Educator content review delay or insufficient reviewer capacity | 3 | 5 | 15 | Content Owner | Start early, structured rubric, review tracker, backup reviewers |
| R-007 | Low cohort recruitment or learner engagement | 3 | 5 | 15 | Product Owner | Partner commitments, onboarding rehearsal, educator support, monitored recruitment funnel |
| R-008 | Educational outcome is inconclusive | 3 | 4 | 12 | Product and Content Owners | Pre-register outcome, validate instruments, protect measurement integrity, report uncertainty |
| R-009 | Partner school, consent, or safeguarding readiness is incomplete | 3 | 4 | 12 | Product and Compliance Owners | School readiness checklist, consent rehearsal, escalation contacts, onboarding gate |
| R-010 | Operational restore or rollback cannot meet objectives | 2 | 5 | 10 | Operations Owner | Rehearse before release, verify compatibility, maintain runbooks and rollback authority |
| R-011 | AI provider outage or degraded output quality | 3 | 3 | 9 | Engineering Lead | Provider fallback, health metrics, safety validation, resilience tests |
| R-012 | LLM costs exceed the beta budget | 3 | 3 | 9 | Product Owner | Budget cap, per-session cost metrics, alert at 80%, prompt and model optimisation |
| R-013 | Support demand exceeds available beta capacity | 3 | 3 | 9 | Operations Owner | Cohort cap, published hours, triage rules, FAQ, escalation and response metrics |
| R-014 | Scope growth compromises readiness or measurement | 3 | 4 | 12 | Product Owner | Early scope freeze, formal change control, capacity and KPI impact assessment |

### Risk-control rules

- Exposure of 15 or more is reviewed weekly.
- R-000 remains open until every phase has an evidence-backed status and the phase-status register is operating.
- Other open risks are reviewed monthly and at every phase gate.
- A risk is not marked Mitigated because a control is planned.
- Mitigated status requires operating evidence and a residual score.
- Every risk has a trigger, contingency action, evidence link, last review date, and next review date.
- Critical risks and mandatory controls may not remain ownerless.

---

# Part VII — Release Governance

## Release Evidence Model

Evidence is stored in the phase that produced it. Every phase evidence package must contain the canonical evidence index and audit report and must reference its approved execution plan and implementation report. The final Phase 13 index references all prerequisite phase control sets, including the separate audit-remediation decision.

```text
docs/release-evidence/
├── programme-baseline/
├── audit-remediation/      # Path defined by the independent remediation roadmap
├── phase-00/
├── phase-01/
├── phase-02/
├── phase-03/
├── phase-04/
├── phase-05/
├── phase-06/
├── phase-07/
├── phase-08/
├── phase-09/
├── phase-10/
├── phase-11/
├── phase-12/
└── phase-13/
    └── release-evidence-index.md
```

Every phase evidence directory must contain or reference:

- the approved phase execution plan and version;
- the reconciled phase implementation report;
- the canonical phase evidence index and all indexed raw evidence;
- the final independent phase audit report and any re-audit records;
- the canonical merge commit, built-artifact digest, environment identity, and post-merge CI run;
- evidence-custodian, auditor, phase-approver, and Release Manager signoffs; and
- any approved amendments, exceptions, defects, risk acceptances, or deferred-work decisions.

Every evidence item records:

- control or checklist ID;
- source commit and artefact digest where applicable;
- environment;
- tool and version;
- timestamp;
- owner and approver;
- result;
- machine-readable report or CI link;
- expiry or revalidation rule.

Screenshots are supporting evidence, not sole proof where machine-readable output is available.

The final evidence index must reference, not duplicate, the audit remediation evidence package.

---

## Three-Stage Release Gate

### Gate A — Go/No-Go meeting entry criteria

The meeting may be scheduled only when all mandatory entry criteria are met.

#### Prerequisites

- [ ] Phases 0–12 have each passed their defined exit gates; no phase is credited by inheritance from an older roadmap.
- [ ] Every Phase 0–12 package contains the full approved control set: execution plan, implementation report, evidence index/pack, and independent phase audit report.
- [ ] The phase-status register identifies the execution plan, implementation report, evidence index, audit report/verdict, canonical merge commit, environment, owner, custodian, auditor, and closure approval for every completed phase.
- [ ] No completed phase has an open implementation PR, unmerged phase branch, failed mandatory criterion, missing evidence, failed/pending audit, unresolved blocking audit finding, or unapproved deferred scope.
- [ ] The separate audit remediation roadmap has reached its approved release-ready state.
- [ ] Its decision record and evidence package reference the same intended release source state.

#### Engineering

- [ ] Three consecutive required CI runs are green on the canonical default branch.
- [ ] Backend and frontend coverage policies are met.
- [ ] Architecture, code-quality, API-contract, migration, and build gates pass.
- [ ] Production artefacts build reproducibly.
- [ ] Staging smoke and critical journey tests pass.

#### Security and privacy

- [ ] Threat model is current.
- [ ] External penetration testing is complete.
- [ ] No unresolved Critical or High security, privacy, consent, or safeguarding finding remains.
- [ ] Secrets, dependency, key-management, and configuration controls pass.
- [ ] External POPIA review and required DPAs are complete.
- [ ] Consent and data-subject workflows are proven.

#### Product and content

- [ ] Critical E2E journeys pass.
- [ ] Accessibility and browser reviews are complete.
- [ ] Performance meets the beta profile.
- [ ] All beta content has educator approval.
- [ ] Analytics, surveys, and feedback mechanisms are proven.
- [ ] Cohort, consent, onboarding, and support arrangements are ready.

#### Operations

- [ ] Monitoring and alerts are active and tested.
- [ ] Backup and restore drill passes.
- [ ] Rollback rehearsal meets the agreed objective.
- [ ] Runbooks and on-call coverage are ready.
- [ ] First-72-hours monitoring and communication plans are approved.

### Gate B — Decision criteria

The decision group records one of:

- **Go** — all mandatory controls pass and residual risks are accepted.
- **Conditional Go** — only permitted non-critical conditions remain. Each condition has an owner, due date, verification method, compensating control, expiry, and explicit approver.
- **No-Go** — a mandatory control fails, evidence is invalid, a condition is expired, or residual risk exceeds tolerance.

The following are non-waivable:

- Critical or High unresolved security, privacy, consent, or safeguarding finding;
- authentication/authorization bypass or cross-learner data exposure;
- unproven release identity or artefact provenance;
- failed backup/restore or rollback rehearsal;
- failed critical learner journey;
- unapproved learner-facing content;
- incomplete audit-remediation non-waivable gate;
- any prerequisite phase falsely marked complete, lacking an approved pre-start execution plan, lacking an approved implementation report, or lacking attributable post-merge exit evidence;
- missing required parent/guardian consent capability.

### Gate C — Launch activation

After a Go or satisfied Conditional Go decision:

- [ ] The approved artefact is promoted without rebuilding.
- [ ] The cohort and stakeholders receive approved communication.
- [ ] Support, on-call, and safeguarding coverage are active.
- [ ] Monitoring cadence begins.
- [ ] The evidence index is locked to the deployed commit and artefact digest.
- [ ] Rollback authority and trigger are confirmed.

---

## Roles and Accountability

One person may hold multiple roles, but each accountability must be explicitly accepted.

| Role | Core accountability |
|---|---|
| Product Owner | Scope, outcomes, cohort, priorities, measurement plan, risk acceptance |
| Engineering Lead | Architecture, implementation, CI, technical quality and evidence |
| Security Owner | Threat model, security gates, vulnerability treatment, penetration-test closure |
| Compliance Owner | POPIA evidence, DPAs, privacy workflows, consent, external review |
| Content Owner | CAPS alignment, educator review, content quality and correction |
| Operations Owner | Monitoring, support, backup, restore, incident response, on-call |
| Release Manager | Phase gates, evidence index, exceptions, decision records, deployment control |
| Data/Measurement Owner | KPI definitions, analytics validation, analysis integrity and reporting |

No mandatory control or exposure-15+ risk may retain a `TBD` owner after programme-baseline approval.

---

# Part VIII — Programme Control

## Definition of Done

A ticket is Done only when:

- implementation or non-code deliverable is complete;
- acceptance criteria pass;
- expected and failure behaviour is tested where applicable;
- security, privacy, safety, and accessibility implications are addressed;
- required CI passes;
- documentation and ADRs are updated;
- observability is added where needed;
- evidence is archived;
- the accountable owner accepts the result.

A phase is Done only when:

- its execution plan was approved before substantive implementation began;
- every approved plan item and amendment is reconciled in the implementation report;
- every mandatory exit criterion is met;
- the work is merged into the canonical branch;
- required post-merge CI and environment verification pass;
- the evidence package is attributable to the canonical merge commit;
- the implementation report receives closure approval; and
- the roadmap status is updated only after that approval.

A permitted exception cannot replace the execution plan or implementation report. A status from an earlier roadmap, local code presence, an open PR, a partial test result, a written-but-unexecuted script, or a report that contains unmet mandatory work cannot establish phase completion. Critical and High security, privacy, consent, safeguarding, backup/restore, rollback, content-approval, and core-journey controls cannot be waived.

---

## Exception Policy

Every permitted exception must identify:

- failed control or acceptance criterion;
- business justification;
- security, privacy, safety, operational, educational, and schedule impact;
- compensating control;
- accountable owner and approver;
- creation and expiry date;
- target fix milestone;
- monitoring and rollback/containment plan.

Exceptions expire automatically. An expired exception is a failed gate.

The exception process cannot override a non-waivable control in this plan or the separate audit remediation roadmap.

---

## Change Control

Material changes to architecture, beta scope, release gates, KPI definitions, supported languages, cohort design, or timeline require:

1. written problem and proposed decision;
2. considered alternatives;
3. impact on capacity, schedule, privacy, security, operations, content review, and evidence;
4. approval by affected accountable owners;
5. updated ADR or decision record;
6. updated linked plans, tests, risks, and communications.

KPI definitions, analysis rules, and thresholds are frozen before beta data collection begins.

---

## Reporting Cadence

### Weekly programme review

Report:

- current phase and active epic;
- execution-plan version, approval status, and amendment status;
- completed acceptance criteria and evidence;
- implementation-report readiness when approaching closure;
- failed or threatened gates;
- audit remediation prerequisite status by reference only;
- risk movement;
- actual versus planned engineering hours;
- external dependency status;
- decisions required;
- next-week WIP commitment.

### Phase start review

Confirm before execution begins:

- canonical execution plan exists and is approved;
- dependencies and preconditions are satisfied;
- scope, acceptance criteria, evidence, risks, rollback, and ownership are complete;
- the plan is committed before substantive changes;
- status moves only to `Ready to Start` or `In Progress`.

### Phase closure review

Confirm before completion is recorded:

- approved execution plan and amendment history;
- implementation report traceability against every plan item and exit criterion;
- frozen evidence index and evidence pack with source identity, hashes, raw outputs, test counts, warnings, and environment identity;
- independent phase audit report with a passing verdict and no unresolved blocking finding;
- canonical merge commit and post-merge CI evidence;
- residual risks, permitted exceptions, and formally approved deferrals;
- no mandatory work remains pending, failed, unverified, or unaudited;
- signed approval from the Phase Approver, Evidence Custodian, Phase Auditor, and Release Manager; and
- roadmap status changes to `Verified Complete` only after the full control set is approved.

### Beta operations review

During the beta:

- operational, privacy, safety, and content-quality signals reviewed daily;
- first 72 hours reviewed at least every two hours during published support coverage;
- weekly KPI trend review;
- immediate escalation for security, privacy, safeguarding, or data-integrity incidents;
- intervention only under the approved measurement rules, except where learner safety requires immediate action.

---

## First 30 Days After Programme-Baseline Approval

### Week 1 — Reset and reconcile

- Approve this full-lifecycle programme baseline.
- Create a phase-status register covering Phases 0–13.
- Set Phases 0–7 to **Open — completion not established** until their current exit evidence is accepted.
- Record the historical contradiction between Roadmaps v3/v4 and Executive Roadmap v5.
- Assign every phase owner, approver, target, evidence path, and current blocker.
- Confirm the independent audit-remediation track and identify any safe overlap with Phase 0 verification.

### Week 2 — Verify Phase 0 and inventory Phases 1–7

- Draft, review, and approve `phase_00_execution_plan.md` before any Phase 0 verification or implementation that changes the system.
- Execute the Phase 0 environment and reproducibility gate only after the start gate passes.
- Inventory implementation evidence for Phases 1–7 without assigning completion credit.
- Map existing code, tests, migrations, documentation, and open defects to each phase exit criterion.
- Identify missing acceptance tests and stale assumptions.
- Re-estimate Phases 0–7 from remaining work rather than historical day estimates.

### Week 3 — Activate the first incomplete phase

- Create `phase_00_implementation_report.md`, freeze `phase_00_evidence_index.md`, and complete `phase_00_audit_report.md`; close Phase 0 only if the report reconciles the approved plan, all evidence passes on the canonical merge commit, the audit verdict passes, and closure approval is recorded.
- Draft and approve `phase_01_execution_plan.md` before activating Phase 1 as the sole engineering WIP item; otherwise retain Phase 0 if it remains open.
- Start external Phase 12 procurement and educator-review preparation where it does not interrupt engineering WIP.
- Finalise the beta measurement plan, content-review rubric, and supported-language decision.
- Review all exposure-15+ risks, especially R-000 and R-004.

### Week 4 — Publish the corrected programme forecast

- Hold the first phase gate under this baseline.
- Publish actual hours, accepted evidence, unresolved controls, and the active phase.
- Recalculate the full Phase 0–13 critical path.
- Remove any remaining downstream document that implies Phases 0–7 are complete.
- Approve the next four-week WIP commitment and external dependency schedule.

---

## Final Programme Position

EduBoost must be governed as a **Phase 0–13 lifecycle**, not as a Phase 8–13 continuation.

Historical implementation claims may be useful leads, but they are not a substitute for the required plan/report/evidence/audit control set. The programme baseline is therefore reset as follows:

1. Phases 0–7 are open until each phase passes its current exit gate.
2. Every Phase 0–13 start requires a prior approved execution plan, and every completion requires an approved implementation report, frozen evidence pack, and passing independent phase audit tied to canonical post-merge evidence.
3. The independent audit-remediation roadmap remains authoritative for its corrective scope and may run in parallel only where dependencies permit.
4. Phase 8 begins only after Phases 0–7 and the required remediation controls are verified.
5. Phase 9 makes the complete lifecycle evidence authoritative in CI.
6. Phases 10–12 prove product, operational, privacy, security, AI, and content readiness.
7. Phase 13 runs the controlled beta and produces the final Go, Extend, or No-Go recommendation.

This correction increases the apparent programme length, but it removes a much larger delivery risk: building late-stage release governance on top of foundational phases that were never formally accepted.

The controlled beta may begin only when every prerequisite phase, the release candidate, approved content, operations controls, external reviews, cohort plan, and measurement plan refer to the same verified source state and scope.

---

## Appendix A — Controlled Programme Documents

Mandatory phase-control templates:

- `docs/roadmap/execution/phase_execution_plan_template.md`
- `docs/roadmap/execution/phase_implementation_report_template.md`
- `docs/roadmap/execution/phase_evidence_pack_template.md`
- `docs/roadmap/execution/phase_audit_report_template.md`


- `EduBoost_Full_Lifecycle_Delivery_and_Beta_Readiness_Plan_2026-06-13.md` — programme-level authority after approval
- `audit_remediation_roadmap_2026-06-13.md` — independently authoritative audit-remediation track
- phase backlogs, ADRs, runbooks, vendor reports, review trackers, and release evidence — supporting controlled artefacts

## Appendix B — Historical Roadmaps and Status Conflict

- `ROADMAP_v2.md` — defines Phases 0–7 and their intended work.
- `ROADMAP_v3.md` — first labels Phases 0–7 as locally completed or CI pending.
- `ROADMAP_v4.md` — carries those completion labels forward while adding Phases 8–13.
- `Roadmap_v5_Executive.md` — states the programme is pre-implementation and no roadmap phase has started.
- the seven later planning documents — begin at Phase 8 and therefore omit the unresolved Phase 0–7 lifecycle.

The conflict is resolved by the evidence rule in this plan: **no phase is complete until its current exit criteria pass and its complete plan/report/evidence/audit control set is approved.**

## Appendix C — Supersession Rule

Upon approval:

- this document governs the complete Phase 0–13 programme sequence, status model, capacity, gates, scope, risks, evidence organisation, and beta governance;
- older roadmap completion labels are historical claims only and confer no current completion credit;
- `ROADMAP_v2.md` remains a source for the intended Phase 0–7 scope where this plan does not redefine it;
- the independent audit-remediation roadmap remains authoritative for its own scope;
- the seven planning documents remain supporting inputs only where they do not conflict with this full-lifecycle plan;
- implementation tickets, ADRs, runbooks, vendor reports, and checklists remain controlled supporting artefacts.
