# Phase 2R Execution Plan — Authoritative CAPS Corpus, Grounded Generation, and Tutor Retrieval

**Document version:** 1.5
**Plan date:** 2026-06-16
**Status:** Gate 2R.6 verified complete; Gate 2R.7 authorised
**Execution authorisation:** Gate 2R.7 only
**Phase:** 02R
**Programme position:** Mandatory foundation reset before Phases 8–13
**Sprint codename / documentation namespace:** `atlas`
**Canonical plan path:** `docs/roadmap/execution/atlas/phase_02r_execution_plan.md`
**Required implementation report:** `docs/roadmap/execution/atlas/phase_02r_implementation_report.md`
**Evidence directory:** `docs/release-evidence/atlas/phase-02r/`
**Required evidence index:** `docs/release-evidence/atlas/phase-02r/phase_02r_evidence_index.md`
**Required audit report:** `docs/release-evidence/atlas/phase-02r/phase_02r_audit_report.md`
**Proposed branch:** `feature/atlas-phase-02r-authoritative-caps-corpus`
**Canonical base branch:** `origin/master`
**Base commit SHA:** `4b3805b700869aaeacce4141bb565e1963777163`
**Actual Alembic head on the current implementation branch:** `20260618_1200_phase02r_grounding`
**Source baseline reviewed:** corrected `Eduboost-V2-master(8).zip` plus the Phase 2R handover and review memorandum
**Gate 2R.0 initial report:** `docs/roadmap/execution/atlas/phase_02r_gate_2r0_initial_report.md`
**Gate 2R.0 closure report:** `docs/roadmap/execution/atlas/phase_02r_gate_2r0_closure_report.md`
**Start-gate control:** `docs/roadmap/execution/atlas/phase_02r_start_gate_control.json`
**baseline_capture_sha:** `81735c51a7cf71c8b9fa110d1d152fb8d7103278`
**initial_gate_report_commit_sha:** `8d972b5f`
**remediation_candidate_sha:** `f039d523fe9c771383c36d61028297a6a808e820`
**remediation_code_commit_sha:** `f039d523fe9c771383c36d61028297a6a808e820`
**evidence_run_source_sha:** `f039d523fe9c771383c36d61028297a6a808e820`
**evidence_commit_sha:** `851f3e16b83d8d1cd9b531ed29dbfe2f5b278e73`
**remote_branch_sha:** `d2b243ca4a3f75e4b50a0afaed046bacabf7c7b9`
**approval_authority_rule:** Gate 2R.0 approval commit `d2b243ca4a3f75e4b50a0afaed046bacabf7c7b9` authorises Gate 2R.1 only and records evidence commit `851f3e16b83d8d1cd9b531ed29dbfe2f5b278e73`.
**Gate 2R.0 approval commit SHA:** `d2b243ca4a3f75e4b50a0afaed046bacabf7c7b9`
**Phase owner:** Nkgolo Lebelo
**Engineering owner:** Nkgolo Lebelo
**Curriculum owner/reviewer:** Nkgolo Lebelo — self-review conflict disclosed; independent reproduction/review remains a closure compensating control
**Rights reviewer:** Nkgolo Lebelo — legal-competence limitation disclosed; ambiguous rights require fail-closed or legal/rights-holder confirmation
**Security/privacy/safeguarding reviewer:** Nkgolo Lebelo
**Language-quality reviewers:** Nkgolo Lebelo for `en`, `af`, and `nso`; human-language review limitation disclosed
**Evidence custodian:** Nkgolo Lebelo
**Release manager:** Nkgolo Lebelo
**Independent technical auditor:** Nkgolo Lebelo acting as self-auditor for Gate 2R.0 only
**Auditor independence:** Independence conflict disclosed; compensating controls require clean-checkout reproduction, raw evidence hashes, post-merge CI, and explicit conflict declarations
**Planning estimate:** 79–121 engineering person-days plus curriculum, rights, language, security, legal, operational, accessibility, and audit review time; re-estimated after Gate 2R.0

```text
PHASE_02R_START_APPROVED=true
```

> **Control statement:** Gate 2R.6 has been verified complete under the
> disclosed self-review exception. Gate 2R.7 is authorised for controlled
> execution only. Gate 2R.8 and every later gate remain blocked until Gate
> 2R.7 has passing evidence, approvals, and a separate immutable transition
> commit.

> **Current implementation boundary:** Gate 2R.1 authority and rights records
> are present for the controlled first closure slice, but those authority
> tables are not yet wired into production retrieval, generation, tutor, or
> activation paths. That integration remains a hard Gate 2R.2/2R.3-or-later
> requirement and cannot be used as evidence that Gate 2R.1 is closed or Gate
> 2R.2 is authorised.


## Document amendments

### Version 1.1 amendments incorporated

This revision incorporates the formal review recommendations and adds:

- an explicit Phase 0/reproducibility prerequisite;
- a precise corpus activation resolution key and multilingual activation model;
- mandatory study-plan, Phase 6 accounting, and Phase 7 coverage integrations;
- a supported human-review interface requirement;
- pre-approved numerical retrieval and grounding thresholds;
- legal escalation rules for ambiguous rights decisions;
- an explicit extracted-text storage decision;
- a multilingual closure matrix;
- compatibility tests for the non-numeric `02R` phase identifier;
- scenario-first test sufficiency language;
- provenance-display requirements;
- controlled appendices and mandatory re-estimation after Gate 2R.0.


These amendments do not authorise execution. All start-gate conditions and named approvals remain mandatory.

### Version 1.2 corrections applied

This revision fixes structural defects identified during document review:

- duplicate section numbers corrected: §10.4 → §10.5 (`Training prohibition by default`); §15.3/§15.4/§15.5 → §15.4/§15.5/§15.6 (`Atomic activation`, `Rollback`, `Activation tests`); §20.4 → §20.5 (`Retrieval behaviour`);
- evidence-item descriptions in the evidence inventory disambiguated: E-02R-014 (start-gate dependency) versus E-02R-127 (closure-gate verification), and E-02R-015 (start-gate dependency) versus E-02R-128 (closure-gate verification);
- table of contents added.

These corrections do not alter scope, success criteria, controls, thresholds, evidence requirements, or approval authority.


### Version 1.3 execution-readiness amendments incorporated

This revision incorporates the second formal review and adds or corrects:

- estimate reconciliation so gate totals equal the headline engineering range;
- executable baseline and verifier command forms;
- explicit activation-key columns and separation of immutable activation events from the current active binding;
- storage-mode-aware page and chunk schemas;
- authoritative source-inventory version tables;
- versioned reviewed translation records;
- gate-aware apply, verify, and evidence scripts;
- candidate-audit, canonical-merge, post-merge evidence, and final-audit ordering;
- graded and pooled retrieval relevance judgments;
- a separate reproducible retrieval-performance workload;
- “zero observed” evaluation wording while preserving zero-tolerance operational policy;
- distinct start-gate, candidate, and post-merge evidence lifecycles;
- top-level human-review/provenance and cross-phase integration sections;
- maker-checker separation-of-duty rules;
- SSRF, DNS-rebinding, parser-sandbox, and resource-containment controls;
- immediate rights-expiry enforcement;
- staging-only first corpus activation before release approval;
- complete negative-class evaluation coverage;
- database and object-store restoration proof;
- immediate use of controlled appendices.

These amendments do not authorise execution. All start-gate conditions and named approvals remain mandatory.


### Version 1.5 Gate 2R.1 integrity-remediation amendments

This revision corrects the premature Gate 2R.1 transition and adds:

- an append-only authoritative source, source-version, rights, inventory, and review-ledger schema;
- explicit `may_translate` and `may_publish_translation` permissions;
- a fail-closed, structured-condition rights policy engine;
- a bounded Grade 4 Mathematics completeness register and deterministic validator;
- gate-state validation that blocks unsupported automation and contradictory plan/evidence states;
- implementation versus closure verification modes;
- clean-worktree evidence collection that emits candidate evidence only and never self-approves;
- archival of the invalid dirty-worktree Gate 2R.1 evidence; and
- restoration of the truthful state: Gate 2R.1 in progress, Gate 2R.2 blocked.

### Version 1.4 control-consistency and implementation-safety amendments incorporated

This revision incorporates the third formal review and adds or corrects:

- a PostgreSQL transactional-outbox activation model instead of claiming that external cache, audit, and metric publication is atomic with the database transaction;
- versioned cache keys and binding-version checks so delayed outbox delivery cannot produce mixed-corpus reads;
- an explicit pre-start/read-only Gate 2R.0 and a hard boundary that authorises production changes only from Gate 2R.1 onward;
- separate, machine-enforceable translation and translation-publication rights plus structured conditional-use constraints;
- a single stronger negative-evaluation minimum everywhere in the plan;
- corrected backup-restoration evidence identity and ordered evidence numbering;
- explicit separation of immutable authority/event ledgers from mutable, rebuildable status projections;
- separate evidence identities for the pre-merge candidate audit and post-merge auditor addendum/final verdict;
- a complete operational control-surface matrix covering inventory, rights, extraction, translation, corpus review, source change, stale-artifact disposition, and review assignments;
- subgroup retrieval reporting by language, strand, term, authority/translation state, and same-language versus cross-lingual mode;
- source lifecycle semantics that derive active use from corpus memberships and active bindings rather than a global source status;
- minimum database constraints, append-only enforcement, idempotency, activation/binding consistency, and answer-verification hash rules;
- package-level revision notes, machine-readable manifest, and validation report.

These amendments do not authorise execution. All start-gate conditions and named approvals remain mandatory.

---

## Table of Contents

  - [Version 1.5 Gate 2R.1 integrity-remediation amendments](#version-15-gate-2r1-integrity-remediation-amendments)
  - [Version 1.1 amendments incorporated](#version-11-amendments-incorporated)
  - [Version 1.2 corrections applied](#version-12-corrections-applied)
  - [Version 1.3 execution-readiness amendments incorporated](#version-13-execution-readiness-amendments-incorporated)
  - [Version 1.4 control-consistency and implementation-safety amendments incorporated](#version-14-control-consistency-and-implementation-safety-amendments-incorporated)
- [1. Mandate](#1-mandate)
- [2. Objective and Learner Risk Reduced](#2-objective-and-learner-risk-reduced)
  - [2.1 Objective](#21-objective)
  - [2.2 Learner and programme risks reduced](#22-learner-and-programme-risks-reduced)
- [3. Measurable Outcomes](#3-measurable-outcomes)
- [4. Bounded First-Closure Source Scope](#4-bounded-first-closure-source-scope)
  - [4.1 Included curriculum scope](#41-included-curriculum-scope)
  - [4.2 Meaning of “complete”](#42-meaning-of-complete)
  - [4.3 Required source-completeness register](#43-required-source-completeness-register)
  - [4.4 Initial inventory categories](#44-initial-inventory-categories)
  - [4.5 Language authority rule](#45-language-authority-rule)
- [5. Dependencies and Preconditions](#5-dependencies-and-preconditions)
  - [5.1 Separate audit-remediation workstream](#51-separate-audit-remediation-workstream)
  - [5.2 Phase 0 and reproducibility prerequisite](#52-phase-0-and-reproducibility-prerequisite)
  - [5.3 `02R` identifier compatibility prerequisite](#53-02r-identifier-compatibility-prerequisite)
- [6. Pre-Execution Baseline](#6-pre-execution-baseline)
  - [6.1 Provisional archive observations](#61-provisional-archive-observations)
  - [6.2 Baseline limitations](#62-baseline-limitations)
  - [6.3 Required baseline commands](#63-required-baseline-commands)
- [7. Scope](#7-scope)
  - [7.1 In scope](#71-in-scope)
  - [7.2 Out of scope](#72-out-of-scope)
- [8. Governing Architecture Decisions](#8-governing-architecture-decisions)
- [9. Required Immutable Data Layers](#9-required-immutable-data-layers)
- [10. Rights Policy and Review Model](#10-rights-policy-and-review-model)
  - [10.1 Fail-closed decision rule](#101-fail-closed-decision-rule)
  - [10.2 Decision evidence](#102-decision-evidence)
  - [10.3 Rights review states](#103-rights-review-states)
  - [10.4 Immediate rights-expiry and withdrawal enforcement](#104-immediate-rights-expiry-and-withdrawal-enforcement)
  - [10.5 Rights-review authority and legal escalation](#105-rights-review-authority-and-legal-escalation)
  - [10.6 Training prohibition by default](#106-training-prohibition-by-default)
- [11. Source Lifecycle](#11-source-lifecycle)
  - [11.1 Lifecycle states](#111-lifecycle-states)
  - [11.2 Supersession and effective dates](#112-supersession-and-effective-dates)
  - [11.3 Source-change triggers](#113-source-change-triggers)
- [12. Secure Acquisition](#12-secure-acquisition)
  - [12.1 Supported methods](#121-supported-methods)
  - [12.2 Required controls](#122-required-controls)
  - [12.3 Acquisition record](#123-acquisition-record)
- [13. Extraction and Structure-Aware Chunking](#13-extraction-and-structure-aware-chunking)
  - [13.1 Extraction preference](#131-extraction-preference)
  - [13.2 Page provenance](#132-page-provenance)
  - [13.3 Chunking rules](#133-chunking-rules)
  - [13.4 Extraction quality gates](#134-extraction-quality-gates)
- [14. Curriculum Knowledge Graph and Mapping Review](#14-curriculum-knowledge-graph-and-mapping-review)
  - [14.1 Mapping authority](#141-mapping-authority)
  - [14.2 Required mapping outputs](#142-required-mapping-outputs)
  - [14.3 Mapping review states](#143-mapping-review-states)
  - [14.4 Maker-checker and segregation-of-duty rules](#144-maker-checker-and-segregation-of-duty-rules)
- [15. Corpus Build, Freeze, Activation, and Rollback](#15-corpus-build-freeze-activation-and-rollback)
  - [15.1 Build eligibility](#151-build-eligibility)
  - [15.2 Freeze](#152-freeze)
  - [15.3 Corpus activation resolution key](#153-corpus-activation-resolution-key)
  - [15.4 Database-atomic activation with transactional outbox](#154-database-atomic-activation-with-transactional-outbox)
  - [15.5 Rollback](#155-rollback)
  - [15.6 Activation tests](#156-activation-tests)
- [16. Mandatory Generation-Grounding Contract](#16-mandatory-generation-grounding-contract)
  - [16.1 Required inputs resolved server-side](#161-required-inputs-resolved-server-side)
  - [16.2 Grounding sufficiency](#162-grounding-sufficiency)
  - [16.3 Persisted generation provenance](#163-persisted-generation-provenance)
  - [16.4 Failure behaviour](#164-failure-behaviour)
- [17. Claim Validation and Copying Controls](#17-claim-validation-and-copying-controls)
  - [17.1 Claim classes](#171-claim-classes)
  - [17.2 Support rules](#172-support-rules)
  - [17.3 Unsupported-claim detection](#173-unsupported-claim-detection)
  - [17.4 Mathematical validation](#174-mathematical-validation)
  - [17.5 Textual overlap](#175-textual-overlap)
- [18. Independent Assessment Answer Verification](#18-independent-assessment-answer-verification)
  - [18.1 Independence rule](#181-independence-rule)
  - [18.2 Verification preference order](#182-verification-preference-order)
  - [18.3 Verification record](#183-verification-record)
- [19. Grounded Learner Tutor](#19-grounded-learner-tutor)
  - [19.1 Grounding hierarchy](#191-grounding-hierarchy)
  - [19.2 Tutor request requirements](#192-tutor-request-requirements)
  - [19.3 Tutor provenance](#193-tutor-provenance)
  - [19.4 Safe fallback](#194-safe-fallback)
- [20. Multilingual Delivery and Review](#20-multilingual-delivery-and-review)
  - [20.1 Language codes](#201-language-codes)
  - [20.2 Required metadata](#202-required-metadata)
  - [20.3 Translation workflow](#203-translation-workflow)
  - [20.4 Multilingual closure matrix](#204-multilingual-closure-matrix)
  - [20.5 Retrieval behaviour](#205-retrieval-behaviour)
- [21. Legacy Artifact Migration](#21-legacy-artifact-migration)
  - [21.1 Inventory](#211-inventory)
  - [21.2 Classification rules](#212-classification-rules)
  - [21.3 Migration policy](#213-migration-policy)
- [22. Human Review and Provenance Interfaces](#22-human-review-and-provenance-interfaces)
- [23. Cross-Phase Integration Requirements](#23-cross-phase-integration-requirements)
- [24. APIs and Authorisation](#24-apis-and-authorisation)
- [25. Durable Jobs](#25-durable-jobs)
- [26. Security, Privacy, Safety, and Data Controls](#26-security-privacy-safety-and-data-controls)
  - [26.1 Threats](#261-threats)
  - [26.2 Mandatory controls](#262-mandatory-controls)
- [27. Observability and Operations](#27-observability-and-operations)
  - [27.1 Metrics](#271-metrics)
  - [27.2 Alerts](#272-alerts)
  - [27.3 Required runbooks](#273-required-runbooks)
- [28. Internal Delivery Gates and Execution Order](#28-internal-delivery-gates-and-execution-order)
  - [28.1 Gate summary](#281-gate-summary)
  - [28.2 Detailed work breakdown](#282-detailed-work-breakdown)
- [29. Migration, Compatibility, Deployment, Rollback, and Recovery](#29-migration-compatibility-deployment-rollback-and-recovery)
  - [29.1 Migration approach](#291-migration-approach)
  - [29.2 Migration-head rule](#292-migration-head-rule)
  - [29.3 Backups](#293-backups)
  - [29.4 Feature flags](#294-feature-flags)
  - [29.5 Rollback triggers](#295-rollback-triggers)
  - [29.6 Rollback steps](#296-rollback-steps)
- [30. Test and Verification Plan](#30-test-and-verification-plan)
- [31. Real-Corpus Evaluation Plan](#31-real-corpus-evaluation-plan)
- [32. Evidence-Pack Plan](#32-evidence-pack-plan)
- [33. Script-Driven Workflow](#33-script-driven-workflow)
  - [33.1 `preflight_phase02r.sh`](#331-preflightphase02rsh)
  - [33.2 `apply_phase02r_patch.sh`](#332-applyphase02rpatchsh)
  - [33.3 `verify_phase02r.sh`](#333-verifyphase02rsh)
  - [33.4 `verify_phase02r_postgres.sh`](#334-verifyphase02rpostgressh)
  - [33.5 `collect_phase02r_evidence.sh`](#335-collectphase02revidencesh)
- [34. Phase Audit Plan](#34-phase-audit-plan)
- [35. Risks, Assumptions, and Stop Conditions](#35-risks-assumptions-and-stop-conditions)
  - [35.1 Absolute stop conditions](#351-absolute-stop-conditions)
- [36. Change Control](#36-change-control)
  - [36.1 Change log](#361-change-log)
- [37. Required Implementation Report](#37-required-implementation-report)
- [38. Phase Status Lifecycle](#38-phase-status-lifecycle)
- [39. Start-Gate Checklist](#39-start-gate-checklist)
- [40. Approval to Start](#40-approval-to-start)
- [41. Closure Acceptance Checklist](#41-closure-acceptance-checklist)
  - [Source and rights](#source-and-rights)
  - [Extraction, mapping, and corpus](#extraction-mapping-and-corpus)
  - [Generation, verification, and tutor](#generation-verification-and-tutor)
  - [Legacy, evaluation, security, and operations](#legacy-evaluation-security-and-operations)
  - [Engineering and governance](#engineering-and-governance)
- [42. Closure Approval Matrix](#42-closure-approval-matrix)
- [43. Planned Deliverables](#43-planned-deliverables)
  - [Governance and design](#governance-and-design)
  - [Implementation](#implementation)
  - [Verification and closure](#verification-and-closure)
- [44. Controlled Appendices and Maintainability](#44-controlled-appendices-and-maintainability)
- [45. Final Planning Position](#45-final-planning-position)

---

## 1. Mandate

EduBoost must replace a model-memory and hand-maintained-registry interpretation of CAPS alignment with a source-attributable, rights-aware, versioned, reviewed, and auditable curriculum corpus.

The governing product rule is:

> **Official and explicitly permitted curriculum source material is the curriculum authority. The LLM is a grounded pedagogical transformation and tutoring engine, not the curriculum authority.**

The required authority chain is:

```text
Authoritative or explicitly permitted source
→ per-use rights decision
→ immutable acquired source version
→ immutable original file/object and verified checksum
→ versioned extraction with page-level provenance
→ reviewed curriculum nodes and mappings
→ reviewed source chunks
→ frozen corpus manifest
→ atomic corpus activation
→ retrieval from one explicit active corpus version
→ grounded derivative generation or tutor response
→ claim/calculation/answer validation
→ generated-content review
→ publication
→ staleness and withdrawal monitoring
```

A curriculum-dependent operation must fail closed when any mandatory link is missing, stale, blocked, superseded, unauthorised, unreviewed, ambiguous, or insufficient.

---

## 2. Objective and Learner Risk Reduced

### 2.1 Objective

Implement a production-grade authoritative Grade 4 Mathematics CAPS corpus and make it the mandatory source of curriculum truth for EduBoost lesson generation, assessment generation, study-plan logic, curriculum-dependent tutor responses, and affected coverage reporting.

### 2.2 Learner and programme risks reduced

This phase reduces the risk that EduBoost:

- invents or misstates CAPS requirements from model memory;
- treats a manually assigned CAPS code as proof of alignment;
- retrieves synthetic, stale, blocked, or superseded content;
- uses source material without a defensible rights basis;
- silently changes the source version behind a published artifact;
- publishes mathematically incorrect answer keys because educators reached quorum;
- labels machine-translated text as official Afrikaans or Sepedi authority;
- serves legacy ungrounded content to learners;
- cannot prove which exact source passages grounded a lesson, item, study plan, or tutor answer.

---

## 3. Measurable Outcomes

Phase 2R succeeds only when all of the following are true and evidenced:

1. A signed source-scope and source-completeness register defines the complete first-closure inventory.
2. Every active source version has a reviewed authority tier and machine-enforceable per-use rights decisions, including translation/publication and structured conditions where applicable.
3. Every acquired original is stored immutably outside Git, malware-scanned, and SHA-256 verified.
4. Source versions, extraction runs, pages, sections, chunks, mappings, reviews, and corpus memberships are immutable and historically queryable.
5. Page provenance is preserved for every active chunk; OCR-derived text is identifiable and reviewed more strictly.
6. All five Grade 4 Mathematics CAPS strands and Terms 1–4 are represented by reviewed Tier 1 evidence.
7. The curriculum graph and mappings are human-reviewed and trace every active curriculum node to source sections.
8. A frozen corpus manifest identifies exact source versions, chunk versions, mapping versions, embedding model/version, and manifest hash.
9. Corpus activation and rollback are database-atomic per scope and language policy, with external side effects delivered through a transactional outbox and retrieval correctness independent of outbox timing.
10. The production retrieval projection contains only chunks eligible under the active corpus manifest.
11. Synthetic chunks remain test-only and cannot enter an active production corpus.
12. Production generation requires an explicit active corpus version and sufficient approved Tier 1 grounding for every requested learning objective.
13. Curriculum claims in generated output are linked to supporting chunks and unsupported claims block publication.
14. Mathematical calculations and assessment answers use an independent verification workflow separate from Phase 3 educator approval.
15. Curriculum-dependent tutor responses retrieve from the active corpus or use an explicit non-authoritative safe fallback.
16. Tutor and generation records persist the retrieval query, corpus version, chunk IDs, curriculum node IDs, grounding policy/version, validation result, and source snapshot hash.
17. English (`en`), Afrikaans (`af`), and Sepedi (`nso`) authority/translation status is explicit and cannot be silently conflated.
18. Every existing learner-serving curriculum artifact has a classified legacy disposition.
19. Retrieval evaluation uses real active-corpus chunk IDs and includes at least 18 positive cases plus at least 10 negative cases or one case for every mandatory exclusion class, whichever is greater, across all five strands and three languages.
20. Evaluation produces zero blocked-rights, withdrawn, superseded, wrong-version, or unauthorised authoritative hits.
21. Phase 1–7 regression gates remain green or an approved material plan amendment records and resolves the regression before closure.
22. Required APIs, jobs, metrics, alerts, and runbooks are operationally verified.
23. The implementation report reconciles every planned item and exception.
24. The evidence pack is complete, hashed, attributable to the canonical merge commit, and independently audited.
25. No Critical or High audit finding remains open.
26. Post-merge CI passes on the canonical merge commit before the phase status is updated to `Verified Complete`.
27. Phase 0 is verified or equivalent reproducibility controls pass under Gate 2R.0.
28. Existing programme tooling supports `02R`, `phase-02r`, and `phase_02r` without status, path, sorting, evidence, or CI defects.
29. Study plans use only active approved curriculum nodes and become stale after relevant source/corpus changes.
30. Phase 7 coverage is decomposed into authoritative source, reviewed mapping, approved chunk, published lesson, verified assessment, and language delivery coverage.
31. Phase 6 accounts applicable acquisition, OCR/AI extraction, embeddings, mapping, validation, verification, generation, tutor, and evaluation operations.
32. Rights, extraction, mapping, language, corpus, and source-change reviewers have a supported authenticated and accessible interface or approved CLI.
33. Evaluation and grounding thresholds are approved before dataset execution and cannot be relaxed post hoc without amendment and re-run.
34. Provenance is displayed appropriately for reviewers, educators, learners, guardians, operators, and auditors.

---

## 4. Bounded First-Closure Source Scope

### 4.1 Included curriculum scope

| Dimension | Phase 2R first-closure scope |
|---|---|
| Country | South Africa |
| Curriculum | CAPS |
| Phase / grade | Intermediate Phase, Grade 4 |
| Subject | Mathematics |
| Terms | 1–4 |
| Strands | Numbers, Operations and Relationships; Patterns, Functions and Algebra; Space and Shape; Measurement; Data Handling |
| Delivery languages | `en` English; `af` Afrikaans; `nso` Sepedi |
| Tier 1 | Official curriculum policy, amendments, errata, assessment/promotion requirements and applicable official circulars that define Grade 4 Mathematics requirements |
| Tier 2 | A selected, signed inventory of permitted official instructional support sources such as workbooks, teacher guides, exemplars, or official learning-support material |
| Tier 3 | Optional, explicitly permitted supplementary material; never allowed to override Tier 1 or define a CAPS requirement |

### 4.2 Meaning of “complete”

“All CAPS material” does **not** mean an unlimited crawl of every DBE or provincial document. For Phase 2R closure it means:

- the source-completeness register has a closed, approved inventory;
- every mandatory authority category has a located source or an explicit documented absence;
- all five strands, Terms 1–4, Grade 4 assessment expectations, and applicable amendments are covered;
- every inventory row has completed authority, rights, acquisition, extraction, mapping, review, and corpus decisions;
- changes after inventory freeze require a plan amendment or a controlled post-closure source-change workflow.

### 4.3 Required source-completeness register

Create and maintain:

```text
data/curriculum/registries/grade4_mathematics_caps_source_completeness.json
```

The canonical authority record remains in PostgreSQL; the Git record is a deterministic, non-sensitive reviewed manifest or generated projection used for review and drift checks.

Each required-source row must contain at least:

```text
inventory_item_id
source_category
required_for_closure
expected_authority_tier
subject
phase
grade
terms
strands
language_availability_expected
located
logical_source_id
source_version_id
official_url
authority_confirmed
rights_review_status
acquired
original_sha256_verified
extraction_status
mapping_status
approved_for_corpus
language_status
open_issue
reviewer
reviewed_at
```

### 4.4 Initial inventory categories

The discovery gate must locate and decide at least:

1. the current Grade 4–6 Mathematics CAPS policy statement applicable to Grade 4;
2. every amendment, erratum, or circular that changes that policy for the active period;
3. applicable official assessment and promotion requirements;
4. selected official Grade 4 Mathematics learner workbooks or instructional support sources for Terms 1–4, where use is permitted;
5. selected official teacher guides or exemplars, where use is permitted;
6. official Afrikaans or Sepedi versions where they exist;
7. an explicit “not available / not authoritative” record where an official translation is not available.

Exact titles, effective dates, versions, and URLs must be discovered and reviewed; this plan does not pre-approve any document.

### 4.5 Language authority rule

The system must distinguish:

```text
official_source
approved_human_translation
machine_translation_draft
generated_learner_explanation
```

A machine-translated or LLM-generated passage is never promoted to official curriculum authority. Where no official `af` or `nso` authority source exists, retrieval may use an approved cross-lingual policy that cites the authoritative source language and labels the learner-facing translation as derivative and reviewed.

---

## 5. Dependencies and Preconditions

| Dependency / precondition | Required state before substantive work | Planned evidence | Owner | Start-gate status |
|---|---|---|---|---|
| Canonical repository identity | Canonical branch and remote confirmed | E-02R-001 | Nkgolo Lebelo | Recorded |
| Phase 0 reproducibility foundation | Phase 0 is `Verified Complete`, or its clean-checkout, exact-toolchain, environment-validation, CI-baseline, and setup controls are formally absorbed into Gate 2R.0 with equivalent evidence | E-02R-014 | Nkgolo Lebelo | Blocked: clean-checkout evidence incomplete |
| Phase identifier compatibility | Status-register, path, evidence, template, sorting, and automation tooling supports `02R`, `phase-02r`, and `phase_02r` without integer conversion or ordering defects | E-02R-015 | Nkgolo Lebelo | Partially proven: validator installed and passing locally; broader CI/template proof pending |
| Clean worktree | No uncommitted implementation changes | E-02R-002 | Nkgolo Lebelo | Blocked: active worktree dirty |
| Plan approval | This plan approved and committed | E-02R-003 | Nkgolo Lebelo | Blocked: start gate failed |
| Baseline commit | Base SHA and plan commit SHA recorded | E-02R-004 | Nkgolo Lebelo | Base SHA recorded; plan commit pending |
| Migration head | Actual live Alembic head recorded; no unexpected branches | E-02R-005 | Nkgolo Lebelo | Recorded |
| Phase 1-7 state | Actual tests, evidence, status claims, and reconciliation gaps recorded without inheriting completion claims | E-02R-006 | Nkgolo Lebelo | Recorded with blocker |
| Audit-remediation boundary | Relevant release blockers tracked separately; Phase 2R scope not expanded silently | E-02R-007 | Nkgolo Lebelo | Accepted for planning |
| Object storage | Development/staging object storage and immutable-key policy available | E-02R-008 | Nkgolo Lebelo | Blocked: availability not proven |
| Rights review capability | Named reviewer and decision template accepted | E-02R-009 | Nkgolo Lebelo | Accepted with fail-closed limitation |
| Curriculum review capability | Named Grade 4 Mathematics reviewer and sampling scope accepted | E-02R-010 | Nkgolo Lebelo | Accepted with self-review limitation |
| Language review capability | Reviewers/controls for `en`, `af`, `nso` accepted | E-02R-011 | Nkgolo Lebelo | Accepted with self-review limitation |
| Auditor acceptance | Auditor accepts scope, independence statement, and sampling | E-02R-012 | Nkgolo Lebelo | Accepted as self-audit; independence conflict disclosed |
| Toolchain | `.venv/bin/python` or `PYTHON_BIN`, PostgreSQL/pgvector, Redis where required, object-storage adapter, frontend package manager | E-02R-013 | Nkgolo Lebelo | Partially recorded; object-storage adapter not proven |

### 5.1 Separate audit-remediation workstream

POPIA route/auth defects, general CI mechanics, unrelated frontend route drift, general auth refactoring, billing identity, and other June 2026 audit findings remain governed by the audit-remediation roadmap unless they directly block a Phase 2R verification gate.

Phase 2R may record such a blocker and stop. It may not silently absorb unrelated remediation or claim those matters resolved without their own evidence.

### 5.2 Phase 0 and reproducibility prerequisite

Phase 2R may not start on an unverified setup foundation.

Before approval, one of the following must be evidenced:

1. **Preferred:** Phase 0 is formally `Verified Complete`; or
2. **Compensating route:** Gate 2R.0 explicitly absorbs and independently verifies the equivalent controls:
   - clean-checkout setup;
   - exact Python, Node, package-manager, PostgreSQL, pgvector, Redis, container, and extraction-tool versions;
   - deterministic dependency installation;
   - environment validation;
   - secrets and configuration checks;
   - migration and schema baseline;
   - required CI baseline;
   - reproducible developer and verifier commands.

The compensating route does not retroactively mark Phase 0 complete. It only prevents Phase 2R from inheriting an unverified environment.

### 5.3 `02R` identifier compatibility prerequisite

Before any Phase 2R implementation file is installed, the preflight must prove that existing programme tooling supports all canonical forms:

```text
02R
phase-02r
phase_02r
```

The compatibility gate must cover:

- phase-status parsing;
- numeric sorting assumptions;
- Atlas path validation;
- evidence collection;
- template generation;
- report linking;
- shell-script phase loops;
- CI matrix generation;
- migration/evidence directory naming.

Any integer-conversion, ordering, omission, or path-normalisation defect blocks execution.


---

## 6. Pre-Execution Baseline

### 6.1 Provisional archive observations

The supplied archive indicates:

- a FastAPI/Next.js modular monolith with PostgreSQL, Alembic, Redis, pgvector retrieval, generated-content governance, IRT, tutor safety, durable AI accounting, and curriculum coverage components;
- an apparent single Alembic head of `20260615_1800_p7_curriculum`;
- existing `retrieval_source_documents` and `retrieval_source_chunks` tables;
- mutable retrieval document indexing keyed by `document_id`;
- source/chunk hashes and page-range metadata, but no complete immutable authority chain;
- current Content Factory registry files and a limited active Grade 4 Mathematics scope;
- a small technical retrieval dataset that is not closure evidence;
- existing production bypass candidates that assign approval/alignment/answer-verification state without the required independent controls;
- tutor context built principally from lesson content and knowledge gaps rather than direct active-corpus retrieval;
- no Phase 2R plan, migration, source catalogue, rights register, corpus-version implementation, or closure evidence.

### 6.2 Baseline limitations

The supplied ZIP has no usable Git history. Therefore branch identity, commit attribution, worktree cleanliness, merge state, and post-merge CI cannot be inferred from the archive.

All baseline facts must be re-run in the live canonical repository before approval to start.

### 6.3 Required baseline commands

The preflight must capture at least:

```bash
git remote -v
git branch --show-current
git rev-parse HEAD
git status --short
git log -1 --decorate --oneline
${PYTHON_BIN:-.venv/bin/python} -m compileall -q app scripts
${PYTHON_BIN:-.venv/bin/python} -m ruff check app tests scripts --select E9,F63,F7,F82,F821
${PYTHON_BIN:-.venv/bin/python} scripts/verify_migration_graph.py
${PYTHON_BIN:-.venv/bin/python} scripts/validate_schema_integrity.py
${PYTHON_BIN:-.venv/bin/python} -m alembic heads
${PYTHON_BIN:-.venv/bin/python} scripts/check_runtime_entrypoints.py
${PYTHON_BIN:-.venv/bin/python} scripts/generate_openapi.py --check
${PYTHON_BIN:-.venv/bin/python} scripts/validate_atlas_control_set.py
${PYTHON_BIN:-.venv/bin/python} scripts/validate_phase_identifier_compatibility.py 02R phase-02r phase_02r
${PYTHON_BIN:-.venv/bin/python} scripts/verify_phase0_or_equivalent_baseline.py
```

Where the exact executable form differs, the plan must be amended rather than recording a misleading command.

---

## 7. Scope

### 7.1 In scope

- authoritative-source catalogue and per-use rights register;
- immutable source, source-version, file/object, extraction, page, section, and chunk records;
- secure acquisition and refresh/change-detection workflows;
- native PDF extraction and controlled OCR fallback;
- structure-aware chunking with page and section provenance;
- curriculum graph and reviewed source-to-curriculum mappings;
- frozen corpus manifests, atomic activation, and rollback;
- retrieval projection rebuilt solely from active approved corpus membership;
- production synthetic-corpus guard;
- grounded lesson, assessment, worked-example, and curriculum-dependent study-plan generation;
- curriculum claim support and unsupported-claim rejection;
- deterministic-first answer/calculation verification;
- grounded learner tutor retrieval and provenance persistence;
- source-change impact analysis and stale-artifact workflow;
- measurable legacy artifact inventory, classification, withdrawal, regeneration, and re-review;
- real-corpus multilingual evaluation across five strands and three languages;
- protected admin APIs and durable jobs;
- metrics, alerts, and runbooks;
- Phase 1–7 affected regression verification;
- Atlas implementation report, evidence pack, audit, canonical merge, and closure controls.
- Phase 6 accounting for acquisition, OCR/extraction AI, embeddings, mapping proposals, validation, generation, verification, and tutor operations;
- grounded study-plan curriculum resolution, prerequisite use, provenance, and staleness invalidation;
- Phase 7 coverage decomposition into source, mapping, chunk, lesson, assessment, and language coverage;
- a supported, authenticated and accessible human-review interface or approved review CLI for rights, extraction, mapping, language, corpus, and source-change decisions;
- role-appropriate provenance display for reviewers, educators, learners, guardians, operators, and auditors;

### 7.2 Out of scope

- ingesting every South African curriculum, grade, or subject;
- unrestricted web crawling;
- model fine-tuning or training on official source text;
- automatic rights approval;
- automatic curriculum-mapping approval;
- automatic generated-content publication;
- redesigning Phases 8–13;
- general POPIA, billing, auth, frontend, or CI remediation not directly required by Phase 2R;
- storing original large documents in Git unless a rights and repository-size decision explicitly permits it;
- treating Tier 2 or Tier 3 material as superior to Tier 1;
- replacing the existing application or rebuilding working Phase 1–7 engines without a documented necessity.

---

## 8. Governing Architecture Decisions

Create the following Architecture Decision Records before schema implementation:

| ADR | Decision | Required conclusion |
|---|---|---|
| ADR-02R-001 | Authority write model versus retrieval projection | PostgreSQL authority records are immutable; retrieval tables/indexes are rebuildable projections, never the legal/curriculum source of truth |
| ADR-02R-002 | Original-file storage | Object storage with immutable/versioned keys; local filesystem adapter only for development; original SHA-256 stored and reverified |
| ADR-02R-003 | Corpus versioning, database-atomic activation, outbox, and cache consistency | Corpus manifests are immutable; the authoritative binding switches in PostgreSQL; external effects use a transactional outbox; versioned cache keys preserve correctness; rollback appends a new activation without rewriting history |
| ADR-02R-004 | Source and extraction version identity | Logical source, acquired version, original object, extraction run, page, section, and chunk version receive separate stable IDs |
| ADR-02R-005 | Rights policy | Per-use decisions, including translation/publication, are explicit, version-bound, fail-closed, conditionally machine-enforced, and independent from source authority |
| ADR-02R-006 | Multilingual authority and fallback | Official sources, reviewed translations, machine drafts, and generated explanations are distinguishable; fallback is explicit and auditable |
| ADR-02R-007 | Grounding contract | Every curriculum-dependent production operation resolves one explicit active corpus version and persists provenance |
| ADR-02R-008 | Answer verification | Deterministic/rule-based verification is preferred; separate model verification is supplementary; Phase 3 quorum never sets verification state |
| ADR-02R-009 | Legacy migration | Every learner-serving artifact receives an explicit disposition; synthetic fixtures are isolated from production |
| ADR-02R-010 | Source change and staleness | Source changes create impact records and controlled staleness/withdrawal decisions; no history is overwritten |
| ADR-02R-011 | Extracted-text storage | Decide PostgreSQL full-text, object-store extraction artifacts, or hybrid storage; DB always retains hashes, provenance, review state, and access-controlled references |
| ADR-02R-012 | Human review interface | Define the supported authenticated review UI/CLI, accessibility standard, immutable-decision interaction, and restrictions on bulk approval |
| ADR-02R-013 | Corpus activation resolution key | Define the exact global/tenant, curriculum, grade, subject, delivery-language, and language-policy dimensions used for activation, lookup, rollback, and caching |

ADR files must live under the canonical architecture namespace selected by existing repository convention and must be referenced from the implementation report.

---

## 9. Required Immutable Data Layers

The authoritative write model is immutable and distinct from the rebuildable retrieval projection.

It must preserve:

```text
source inventory version
→ logical source
→ acquired source version
→ original immutable object
→ extraction run
→ page/section/chunk version
→ reviewed translation version
→ curriculum node and mapping version
→ corpus version and membership
→ immutable activation event
→ transactional active binding
→ retrieval projection
→ generation/tutor provenance
→ verification/review/publication/staleness history
```

Mandatory design decisions include:

- authoritative PostgreSQL inventory-version tables;
- storage-mode-aware inline/object-store text fields;
- explicit reviewed translation lineage;
- complete activation-key dimensions on corpus versions, events, bindings, retrieval, caches, generation, tutor records, metrics, and evidence;
- immutable activation events plus a separate transactional current binding;
- no mutation of frozen corpus membership or source-bearing version fields;
- retrieval tables remain projections, never authority.

The complete schema is controlled in:

- `phase_02r_appendix_a_data_model.md`
- version `1.4`
- SHA-256 `57964963d41efdeee1dcc70c763f4e445684c73ecdc930af3884024ddbb545a7`

The appendix must be approved with this plan before schema implementation.

---
## 10. Rights Policy and Review Model

### 10.1 Fail-closed decision rule

A source version is ineligible for extraction, embedding, retrieval, prompting, derivative generation, translation, publication of a translation, excerpt display, redistribution, commercial use, or training unless that specific use has an explicit approved decision.

A missing, expired, superseded, withdrawn, disputed, or `unknown` decision is treated as denied.

### 10.2 Decision evidence

Each decision must retain:

- source version;
- reviewer identity and competence;
- basis type and evidence/reference;
- decision date;
- permitted and prohibited uses, including translation and publication of translations;
- structured, machine-enforceable conditions for permitted languages, channels, jurisdictions, excerpt limits, attribution, and other restrictions;
- attribution requirements and attribution-policy version;
- expiry, re-review date, or trigger;
- conflicts or limitations;
- immutable decision hash;
- supersession link.

### 10.3 Rights review states

```text
not_reviewed
in_review
approved_with_conditions
approved
rejected
expired
superseded
withdrawn
disputed
```

Only `approved` and `approved_with_conditions` decisions whose structured conditions are successfully evaluated may qualify a use. Free-text notes are never the sole enforcement mechanism for a conditional approval.


### 10.4 Immediate rights-expiry and withdrawal enforcement

Rights eligibility must be checked synchronously when resolving an active corpus membership for retrieval, prompt use, excerpt display, generation, or export.

An expiry, withdrawal, dispute, or superseding rights decision must:

1. make the affected use ineligible immediately;
2. append an eligibility/source-change event and safe-disable or replace the affected active binding without mutating the frozen corpus membership;
3. enqueue cache-invalidation, audit, metric, and alert work through the transactional outbox;
4. create a corpus-impact and artifact-staleness assessment;
5. trigger emergency rollback to a previously eligible corpus where one exists;
6. otherwise disable the affected curriculum-dependent operation;
7. alert rights, curriculum, security, operations, and release owners.

A scheduled rebuild may reconcile state, but it may not be the first enforcement point.


### 10.5 Rights-review authority and legal escalation

A designated rights reviewer may approve clear cases covered by an accepted policy, licence, written permission, or established organisational authority.

The following require authorised legal review or documented written permission from the rights holder before approval:

- ambiguous derivative or adaptation rights;
- commercial use not expressly granted;
- redistribution or learner-facing excerpt use not expressly granted;
- translation rights;
- model-training or fine-tuning use;
- conflicting licence terms;
- unclear copyright ownership;
- rights that depend on jurisdiction-specific interpretation.

Developers, curriculum reviewers, administrators, and LLM outputs are not legal authority by default.

The rights ledger must record whether the decision was:

```text
policy_determined
licence_determined
written_permission
authorised_legal_review
rejected_or_unresolved
```

Any ambiguous use remains denied until the required authority is documented.

### 10.6 Training prohibition by default

`may_use_for_model_training` defaults to `false` independently of retrieval or derivative permission. No source text enters Phase 7 training manifests unless the specific source version has explicit training approval.

---

## 11. Source Lifecycle

### 11.1 Lifecycle states

```text
discovered
rights_review_required
approved_for_acquisition
acquired
security_review_failed
extraction_pending
extracted
extraction_review
mapping_review
approved_for_corpus
superseded
withdrawn
blocked
archived
```

State changes require server-side policy checks and append-only audit events. `active_in_corpus` is not a global source lifecycle state: active use is derived from immutable corpus memberships plus the current active binding for a complete activation key. A source may be active in one language/tenant binding and inactive in another.

### 11.2 Supersession and effective dates

- A new source version never overwrites the previous version.
- Tier 1 effective-date resolution is server-side and deterministic.
- Superseded and withdrawn versions remain queryable for audit but are not retrieval-eligible.
- A source version change creates a `source_change_event` and impact analysis before activation.
- Where Tier 1 sources conflict, the applicable effective official source wins; unresolved conflicts block corpus activation.

### 11.3 Source-change triggers

At minimum, trigger review for:

- checksum or object change;
- publisher version-label change;
- publication/effective-date change;
- amendment or erratum discovery;
- authority-tier change;
- rights decision change;
- extraction text or layout change;
- mapping change;
- source withdrawal or URL substitution;
- embedding/chunking policy change affecting retrieved evidence.

Metadata-only changes may be classified as non-substantive only through a reviewed impact decision.

---

## 12. Secure Acquisition

### 12.1 Supported methods

- authorised administrator upload;
- approved HTTPS URL download;
- approved API/feed;
- checksum-confirmed refresh.

No arbitrary URL fetch is permitted.

### 12.2 Required controls

- scheme and host allowlist;
- SSRF controls that reject private, loopback, link-local, multicast, reserved, and cloud metadata-service addresses;
- DNS resolution and rebinding protection before connection and after every redirect;
- TLS certificate and hostname verification with no production bypass;
- redirect-chain validation and maximum redirect count;
- content-type allowlist;
- file-extension and magic-byte agreement;
- maximum file size and maximum page count;
- download timeout and rate limits;
- malware scanning before extraction;
- decompression-bomb and archive recursion limits;
- duplicate detection by original SHA-256;
- immutable object key/version;
- object-storage least privilege;
- path traversal prevention;
- HTML/script sanitisation where applicable;
- source-embedded prompt-injection scanning;
- parser and OCR execution in a network-disabled sandbox/container;
- CPU, memory, file-descriptor, page-count, output-size, and wall-clock limits;
- malformed-PDF/parser-crash containment and quarantine;
- operator and acquisition audit event;
- no learner PII in the curriculum corpus.

### 12.3 Acquisition record

Record exact URL, redirect chain, HTTP metadata, retrieval timestamp, operator, content type, size, object URI/version, checksum, scan outcome, rights state, and failure reason.

---

## 13. Extraction and Structure-Aware Chunking

### 13.1 Extraction preference

1. native PDF text and layout extraction;
2. table/formula-aware extraction adapters;
3. OCR only for pages without acceptable native extraction;
4. manual correction or exclusion where confidence remains insufficient.

### 13.2 Page provenance

Every active chunk must resolve to:

- source version;
- original object checksum;
- extraction run/configuration;
- page number(s);
- section path;
- table/figure/formula identity where applicable;
- extracted text hash;
- confidence and warnings;
- extraction review decision.

### 13.3 Chunking rules

- follow document section and reading-order boundaries;
- do not split a mathematical worked example from its result or qualifying text without linked context;
- preserve table headings and row/column meaning;
- preserve formula context;
- avoid combining unrelated curriculum requirements;
- store language explicitly;
- generate stable content-derived IDs only within a versioned namespace;
- record chunking policy and implementation version;
- create new chunk versions on policy change.

### 13.4 Extraction quality gates

A source version cannot be corpus-eligible until:

- all pages have extraction outcomes;
- low-confidence pages are reviewed or excluded;
- sampled page text matches the source;
- mathematical symbols, decimals, fractions, units, tables, and headings meet approved quality thresholds;
- every included chunk has a page range and reviewed source mapping.

---

## 14. Curriculum Knowledge Graph and Mapping Review

### 14.1 Mapping authority

The graph represents reviewed interpretations of authoritative source passages. It is not generated solely from the existing hand-maintained registry.

Existing CAPS codes and topic maps may be imported as mapping proposals, never as automatic approvals.

### 14.2 Required mapping outputs

For every included learning objective or assessment requirement:

- Grade 4, Mathematics, term, strand, topic/subtopic, skill, and objective are explicit;
- at least one approved Tier 1 chunk supports the requirement;
- prerequisite and sequencing edges are reviewed where used by diagnostics/study plans;
- multilingual labels are linked as translations, not separate authority claims;
- amendments/supersession are represented;
- mapping rationale and reviewer are stored.

### 14.3 Mapping review states

```text
proposed
in_review
approved
rejected
needs_revision
superseded
withdrawn
```

Only approved mapping versions may enter a corpus manifest.


### 14.4 Maker-checker and segregation-of-duty rules

The service, API, database constraints where practical, and tests must enforce:

- a mapping proposer may not be the sole approver of that mapping;
- a translation author may not be the sole language reviewer or curriculum-meaning reviewer;
- a corpus builder may not be the sole corpus activator;
- a rights requester may not approve an ambiguous or escalated rights decision;
- an acquisition operator may not self-approve a checksum discrepancy;
- an artifact generator may not independently verify its own answer solely through the same model, prompt, provider configuration, or operation identity;
- emergency overrides require a separate authorised actor, reason, expiry, and immutable audit event.

Where staffing makes strict separation impossible, the plan must record an approved compensating control before the affected decision is accepted.

---

## 15. Corpus Build, Freeze, Activation, and Rollback

### 15.1 Build eligibility

A chunk may enter a candidate corpus only when:

- source authority tier is approved;
- required rights uses are approved;
- the source version is active and not superseded/withdrawn/blocked;
- original checksum is verified;
- extraction review passes;
- mapping review passes;
- quality score meets policy;
- language status is explicit;
- no unresolved security warning remains.

### 15.2 Freeze

Freezing a corpus must:

- resolve the signed source-completeness register version;
- materialise exact source, chunk, and mapping version memberships;
- record chunking, embedding, retrieval, and grounding policy versions;
- generate a deterministic canonical manifest;
- calculate `manifest_sha256`;
- prevent membership edits;
- require curriculum and rights review before activation.


### 15.3 Corpus activation resolution key

ADR-02R-013 must define and freeze the activation key before corpus tables and caches are implemented.

The first-closure default is:

```text
curriculum_code
+ grade
+ subject_code
+ delivery_language
+ tenant_scope
```

Where:

- `curriculum_code` is initially `CAPS`;
- `grade` is initially `4`;
- `subject_code` is initially `MATH`;
- `delivery_language` is one of `en`, `af`, `nso`;
- `tenant_scope` is `global` unless a later approved tenancy policy requires tenant-specific corpora.

The implementation must explicitly decide whether language activation uses:

1. one corpus per delivery language; or
2. a multilingual corpus with language-specific membership and an approved cross-lingual policy.

**Recommended first closure:** one active corpus per delivery language, sharing the same reviewed Tier 1 authority versions where permitted, with derivative translation memberships clearly labelled.

Every activation, retrieval query, cache key, generation record, tutor record, rollback, metric, and audit event must carry the complete activation key.

A request may not combine memberships from multiple active corpora unless an approved cross-lingual retrieval policy records:

- primary authority language;
- derivative language status;
- source corpus versions;
- translation review status;
- fallback reason.

### 15.4 Database-atomic activation with transactional outbox

The authoritative switch must occur in one PostgreSQL transaction:

1. resolve and lock the `curriculum_corpus_active_bindings` row for the complete activation key;
2. verify the candidate remains eligible and its manifest hash matches;
3. append an immutable activation event;
4. atomically update the active binding, binding epoch/row version, active corpus ID, and activation-event reference;
5. append idempotent transactional-outbox records for cache invalidation, audit publication, metrics, alerts, and dependent staleness work;
6. commit.

After commit, an idempotent outbox consumer publishes the external side effects. It must support retries, deduplication, observability, and dead-letter handling. External cache invalidation, audit publication, and metric delivery are **not** claimed to be atomic with PostgreSQL.

Retrieval correctness must not depend on immediate outbox delivery. Retrieval and cache keys must include the complete activation key, active corpus version, and binding epoch/row version. A stale cache entry may remain physically present, but it must never be selected after the authoritative binding changes. Direct binding/version validation is required on cache miss, stale-key detection, and safety-critical operations.

Generation and tutor requests already in flight must persist the corpus version and binding epoch they resolved. New requests may resolve the new corpus only after the database commit.

### 15.5 Rollback

Rollback must reactivate an earlier eligible corpus through a new activation event. It must not delete the failed corpus or rewrite prior activation records.

Rollback is blocked if the prior corpus contains a now-withdrawn, blocked, or rights-ineligible source; an emergency safe-disable mode must then stop curriculum-dependent generation/tutoring.

### 15.6 Activation tests

Verify:

- concurrent activation produces one winner;
- retrieval never sees mixed memberships;
- rollback restores the previous manifest;
- in-flight requests remain attributable to the corpus they resolved;
- activation fails when any membership becomes ineligible;
- delayed, duplicated, or failed outbox delivery does not produce mixed-corpus reads;
- stale cache entries cannot be selected after a binding-epoch change;
- cache invalidation is deterministic and idempotent;
- dead-lettered outbox work raises an operational alert without corrupting the binding.

---

## 16. Mandatory Generation-Grounding Contract

### 16.1 Required inputs resolved server-side

Production generation must resolve:

```text
scope_id
requested curriculum node versions
active corpus version
retrieval query
retrieval policy version
grounding policy version
approved chunk versions
source versions
language/fallback policy
```

The client may request a grade/topic/skill but may not supply approval state, source eligibility, answer verification, or publication state.

### 16.2 Grounding sufficiency

Generation proceeds only when:

- one explicit active corpus version is resolved;
- at least one active approved Tier 1 chunk supports each requested learning objective;
- cumulative support meets the configured objective-coverage threshold;
- no source/chunk is blocked, withdrawn, superseded, stale, or rights-ineligible;
- mapping and extraction reviews are approved;
- requested language can be served through an approved authority/translation policy;
- the grounding snapshot and manifest hash are persisted before provider invocation.

A CAPS code alone is insufficient.

### 16.3 Persisted generation provenance

Persist at minimum:

```text
generation_operation_id
artifact_id/artifact_version_id
scope_id
curriculum_node_version_ids
corpus_version_id
activation_scope_key
binding_epoch
retrieval_query
retrieval_policy_version
grounding_policy_version
source_version_ids
chunk_version_ids
mapping_version_ids
retrieval_scores
source_snapshot_sha256
grounding_sufficiency_result
provider/model/prompt versions
claim_validation_result
answer_verification_status
created_at
```

### 16.4 Failure behaviour

Missing or insufficient grounding returns a typed domain error such as:

```text
NO_ACTIVE_CORPUS
INSUFFICIENT_TIER1_COVERAGE
RIGHTS_NOT_APPROVED
SOURCE_SUPERSEDED
MAPPING_NOT_APPROVED
LANGUAGE_FALLBACK_NOT_APPROVED
GROUNDING_VALIDATION_FAILED
```

The system must not silently ask the model to continue from memory.

---

## 17. Claim Validation and Copying Controls

### 17.1 Claim classes

Generated output must classify and validate at least:

1. **Curriculum requirement claims** — what CAPS requires, sequence, scope, terminology, or assessment expectation;
2. **Pedagogical explanations** — derivative explanations of supported concepts;
3. **Mathematical facts and calculations** — examples, steps, units, geometry, data interpretation;
4. **Assessment claims** — question validity, answer, distractor rationale, cognitive level;
5. **Enrichment claims** — useful context not defined as a CAPS requirement.

### 17.2 Support rules

- Every curriculum requirement claim must link to one or more Tier 1 chunk versions.
- Tier 2/3 content may enrich but may not create or override a requirement.
- Unresolved source disagreement blocks the claim and artifact.
- Enrichment must be labelled in metadata and must have its own rights eligibility.
- Generated uncertainty must be explicit; the model may not convert uncertainty into authority.

### 17.3 Unsupported-claim detection

Use a layered validator:

- structured claim extraction from the generated contract;
- required source-support IDs per claim;
- semantic entailment/contradiction screening;
- deterministic policy checks for grade, strand, term, and source tier;
- human review for flagged or ambiguous claims.

No single model score may approve the artifact. A failed mandatory claim blocks Phase 3 submission or moves the artifact to quarantine.

### 17.4 Mathematical validation

- parse and recalculate arithmetic where representable;
- validate units and conversions;
- validate geometry properties and measurements;
- recompute table/chart-derived answers;
- reject impossible or ambiguous questions;
- record checker version and inputs/outputs.

### 17.5 Textual overlap

A rights-approved copying policy must define:

- allowed quoted excerpt length;
- required attribution and citation;
- similarity/overlap thresholds for derivative content;
- handling of standard terminology that cannot be paraphrased meaningfully;
- restricted-source learner/educator excerpt display.

Initial thresholds must be approved by the rights reviewer and tested against the corpus before activation. Excessive overlap blocks publication.

---

## 18. Independent Assessment Answer Verification

### 18.1 Independence rule

Phase 3 educator quorum may approve pedagogical suitability but may never set `answer_key_verified=true` by implication.

Any code path that hardcodes or infers verification from generation, import, or review quorum must be removed from production or isolated as test-only.

### 18.2 Verification preference order

```text
1. deterministic arithmetic/measurement/data checker
2. structured rule-based geometry or curriculum-domain checker
3. symbolic/constraint solver where appropriate
4. separately configured model verification as supplementary evidence
5. educator review of the question and verification record
```

### 18.3 Verification record

Store:

```text
verification_id
artifact_version_id
question_sha256
answer_sha256
reasoning/input_sha256
checker_type
checker_version
checker_configuration_sha256
expected_answer
computed_answer
comparison_result
ambiguity_result
verified_by/reviewer
verified_at
status
invalidated_at
invalidation_reason
```

Any edit to the question, options, answer, data table, diagram, or relevant wording invalidates the previous verification.

---

## 19. Grounded Learner Tutor

### 19.1 Grounding hierarchy

```text
1. active authoritative curriculum chunks
2. published EduBoost lessons grounded in those chunks
3. approved worked examples grounded in those chunks
4. safe generic pedagogical fallback that makes no curriculum-authority claim
```

### 19.2 Tutor request requirements

For curriculum-dependent learner questions, the tutor must:

- enforce existing ownership, consent, PII, safety, rate, and budget controls;
- resolve the learner’s active lesson and curriculum intent;
- resolve one active corpus version;
- retrieve approved chunks;
- persist the retrieval query and results;
- generate only from approved grounding plus safe learner context;
- validate output claims and calculations;
- provide a typed fallback when grounding is unavailable or insufficient.

### 19.3 Tutor provenance

Persist:

```text
tutor_message_id
retrieval_query
activation_scope_key
binding_epoch
corpus_version_id
source_version_ids
source_chunk_version_ids
curriculum_node_version_ids
published_artifact_ids
grounding_policy_version
grounding_status
source_snapshot_sha256
fallback_reason
provider/model/prompt versions
claim_validation_status
```

### 19.4 Safe fallback

The fallback may provide general learning support—such as asking the learner to share the problem or advising them to consult the assigned lesson—but must not state or imply a CAPS requirement.

---

## 20. Multilingual Delivery and Review

### 20.1 Language codes

```text
en  English
af  Afrikaans
nso Sepedi
```

### 20.2 Required metadata

Every source, page, section, chunk, mapping label, generated artifact, evaluation query, and tutor response must record language.

### 20.3 Translation workflow

```text
authoritative source passage
→ explicit `may_translate` rights decision and structured conditions
→ translation proposal
→ language review
→ curriculum meaning review
→ explicit `may_publish_translation` decision where publication is intended
→ approved derivative translation version bound to the relevant rights decisions
→ corpus or generation eligibility decision
```

Machine translation remains draft until both language and curriculum meaning reviews pass. Review approval does not override missing, expired, or conditionally unsatisfied translation/publication rights.


### 20.4 Multilingual closure matrix

| Language/source state | Authority status | Production retrieval | Derivative generation | Closure treatment |
|---|---|---:|---:|---|
| Official source | Authoritative | Yes, subject to rights and active corpus | Yes | Full authority coverage |
| Approved human translation | Reviewed derivative | Yes under approved policy | Yes | Derivative-language coverage |
| Machine translation draft | Non-authoritative draft | No | No publication | Incomplete |
| Generated learner explanation | Learner-facing derivative | Never source authority | Yes only after grounding and review | Delivery coverage only |
| No official/reviewed version | Missing | Same-language authority unavailable; explicit cross-lingual policy only | Safe fallback or reviewed derivative | Recorded gap, not full authority coverage |

Phase 2R must report separately:

```text
authority coverage by language
reviewed derivative translation coverage
learner delivery coverage
missing-language authority gaps
```

Three-language delivery must never be represented as three-language official authority unless that is factually true and evidenced.

### 20.5 Retrieval behaviour

- Prefer same-language approved chunks.
- Cross-lingual retrieval is allowed only by an approved policy.
- The response must retain the authority language and translation status.
- Wrong-language authoritative hits are measured separately.
- English authority may ground an approved Afrikaans/Sepedi derivative explanation, but the system may not label the derivative as official source text.

---

## 21. Legacy Artifact Migration

### 21.1 Inventory

Create a deterministic inventory of all generated lessons, assessments, worked examples, study plans, published artifacts, and tutor-linked lesson content.

At minimum report:

```text
total artifacts
grounded_verified
grounded_unverified
synthetic_fixture
legacy_ungrounded
published_requires_review
quarantined
regenerated
withdrawn
retained_non_curriculum
```

### 21.2 Classification rules

- `grounded_verified`: active source provenance, claim checks, and required answer verification pass;
- `grounded_unverified`: provenance exists but validation/verification is incomplete;
- `synthetic_fixture`: explicitly test-only and inaccessible to production retrieval/serving;
- `legacy_ungrounded`: no acceptable authoritative provenance;
- `published_requires_review`: learner-serving and not yet Phase 2R compliant;
- `quarantined`: blocked from serving pending action.

### 21.3 Migration policy

- preserve IDs, versions, timestamps, and review history;
- add explicit grounding and legacy status;
- remove `legacy_ungrounded` and `synthetic_fixture` artifacts from learner serving;
- regenerate/re-review where product value justifies it;
- withdraw rather than fabricate provenance;
- prevent legacy import paths from assigning `caps_alignment_score=1.0`, `review_status=approved`, `answer_key_verified=true`, or synthetic source evidence in production;
- reconcile every learner-serving artifact before closure.

## 22. Human Review and Provenance Interfaces

Phase 2R requires a supported authenticated and accessible reviewer UI or approved review CLI. Raw SQL and ad hoc HTTP calls are not an acceptable operational review process.

The interface must support source/page preview, rights evidence, extraction warnings, mapping and translation decisions, corpus membership, source-change review, immutable history, maker-checker controls, keyboard access, labels, error summaries, and non-colour-only status.

Audience-specific provenance must be defined for rights reviewers, curriculum/extraction reviewers, generated-content educators, learners, guardians, operators, and auditors, subject to rights and access controls.

Detailed interface, decision, and provenance requirements are controlled in:

- `phase_02r_appendix_e_api_review_and_provenance.md`
- version `1.4`
- SHA-256 `4556fe48a959a99acda1321b1a9a3a8d0d5b255a2b240e4f0b0d591bab910e36`

---
## 23. Cross-Phase Integration Requirements

Phase 2R must explicitly integrate with:

- **Study plans:** active approved curriculum nodes and prerequisite versions, persisted corpus/source provenance, and source/corpus-change staleness.
- **Phase 6:** reservations and finalisation for applicable OCR/AI extraction, embeddings, mapping proposals, claim validation, answer verification, generation, tutor, and evaluation operations.
- **Phase 7:** separate authoritative-source, reviewed-mapping, approved-chunk, published-lesson, verified-assessment, and language-delivery coverage measures.

A combined “CAPS coverage” percentage is prohibited.

Detailed cross-phase contracts are controlled in Appendix E:

- SHA-256 `4556fe48a959a99acda1321b1a9a3a8d0d5b255a2b240e4f0b0d591bab910e36`

---
## 24. APIs and Authorisation

Protected APIs must enforce strict schemas, least privilege, authenticated server-side actor identity, idempotency, immutable decisions, maker-checker restrictions, bounded exports, redacted restricted-source responses, OpenAPI drift checks, and full route/role contract tests.

No client may supply approval, activation, rights, verification, or publication state.

The complete route inventory and review-interface contract are controlled in Appendix E:

- SHA-256 `4556fe48a959a99acda1321b1a9a3a8d0d5b255a2b240e4f0b0d591bab910e36`

---
## 25. Durable Jobs

Phase 2R jobs must be idempotent, resumable, observable, hash their inputs/outputs, use Phase 6 accounting where applicable, enforce source/tenant boundaries, and never auto-approve rights, extraction, mapping, translation, answer verification, corpus activation, content, or publication.

The complete planned job inventory and invariants are controlled in Appendix E:

- SHA-256 `4556fe48a959a99acda1321b1a9a3a8d0d5b255a2b240e4f0b0d591bab910e36`

---
## 26. Security, Privacy, Safety, and Data Controls

### 26.1 Threats

- malicious or substituted source files;
- source poisoning and prompt injection;
- decompression bombs and oversized PDFs;
- path traversal and unsafe filenames;
- checksum mismatch;
- URL/redirect substitution;
- rights-review bypass;
- blocked or withdrawn source retrieval;
- restricted excerpt leakage;
- tenant leakage;
- malicious HTML/scripts;
- poisoned embeddings;
- learner PII entering corpus, embeddings, prompts, logs, or evidence;
- over-privileged object-storage access;
- evidence containing restricted source text.

### 26.2 Mandatory controls

- file and source allowlists;
- content sniffing and size/page limits;
- malware scan and quarantine;
- immutable checksums and object versions;
- prompt-injection detection and source text delimiting;
- server-side authority/rights resolution;
- least-privilege service accounts;
- no learner data in the curriculum corpus;
- sensitive-text redaction in logs/evidence;
- access-controlled excerpts;
- encryption in transit and at rest;
- retention and deletion rules compatible with source rights;
- audit logs for all decisions and activation changes;
- dependency and container scanning under the separate release controls.

---

## 27. Observability and Operations

### 27.1 Metrics

```text
curriculum_sources_discovered_total
curriculum_sources_rights_pending_total
curriculum_sources_acquired_total
curriculum_source_version_changes_total
curriculum_source_scan_failures_total
curriculum_extraction_failures_total
curriculum_extraction_low_confidence_pages_total
curriculum_chunks_approved_total
curriculum_mapping_backlog_total
curriculum_corpus_builds_total
curriculum_corpus_activation_failures_total
curriculum_activation_outbox_pending_total
curriculum_activation_outbox_retry_total
curriculum_activation_outbox_dead_letter_total
curriculum_active_binding_epoch
curriculum_corpus_active_version
curriculum_coverage_by_strand
curriculum_retrieval_fallback_rate
grounding_failures_total
unsupported_claims_total
answer_verification_failures_total
wrong_version_attempts_total
blocked_source_retrieval_attempts_total
rights_condition_evaluation_failures_total
stale_cache_rejection_total
stale_artifacts_total
stale_published_artifacts_total
tutor_grounding_fallback_total
```

### 27.2 Alerts

Alert on:

- checksum or object-version change;
- source withdrawal or rights expiry;
- malware/scan failure;
- extraction-quality threshold breach;
- blocked/superseded source retrieval attempt;
- missing generation/tutor provenance;
- corpus activation or rollback failure;
- activation outbox dead-letter, retry backlog, or binding/cache inconsistency;
- tutor fallback spike;
- unsupported-claim spike;
- stale learner-facing artifact beyond SLA;
- synthetic chunk detected in production corpus;
- repeated structured-rights condition evaluation failure.

### 27.3 Required runbooks

```text
docs/runbooks/atlas/curriculum_source_ingestion.md
docs/runbooks/atlas/curriculum_rights_review.md
docs/runbooks/atlas/corpus_version_change.md
docs/runbooks/atlas/corpus_activation_and_rollback.md
docs/runbooks/atlas/corpus_activation_outbox_failure.md
docs/runbooks/atlas/withdrawn_source_response.md
docs/runbooks/atlas/grounding_failure.md
docs/runbooks/atlas/stale_artifact_response.md
docs/runbooks/atlas/source_security_incident.md
```

---

## 28. Internal Delivery Gates and Execution Order

No later gate may start until the preceding gate’s exit criteria are recorded. Gate 2R.0 is the only pre-start gate and is limited to read-only discovery, planning, ADR drafting/approval, sample-based non-production spikes, estimate refinement, and start-gate approval while `PHASE_02R_START_APPROVED=false`. It may not add migrations, production schema, application/service changes, governed-source ingestion, corpus activation, or learner-serving behaviour. The approved Gate 2R.0 exit commit changes the flag to `true` and authorises Gate 2R.1 onward.

### 28.1 Gate summary

| Gate | Name | Engineering estimate | Human review estimate | Exit decision |
|---|---|---:|---:|---|
| 2R.0 | Read-only discovery, baseline, ADRs, source-scope freeze, and start approval | 5–7 days | 2–4 days | Approved plan/start commit authorises Gate 2R.1 |
| 2R.1 | Source catalogue, rights model, completeness register | 6–9 days | 4–8 days | Inventory and rights framework approved |
| 2R.2 | Secure acquisition and immutable source versioning | 7–10 days | 1–3 days | Original objects and checksums verified |
| 2R.3 | Extraction, pages, sections, chunking, review | 10–15 days | 5–10 days | Extraction quality accepted |
| 2R.4 | Curriculum graph and mapping review | 10–16 days | 8–15 days | All five strands/terms mapped and approved |
| 2R.5 | Corpus build, staging activation, retrieval projection | 9–13 days | 2–4 days | Frozen corpus and controlled staging activation/rollback proven |
| 2R.6 | Grounded generation, claim and answer validation | 10–15 days | 4–8 days | Production generation fails closed and validates |
| 2R.7 | Grounded tutor, study plans, coverage, and operations | 7–10 days | 2–4 days | Tutor, study-plan, coverage, accounting, and observability controls proven |
| 2R.8 | Legacy migration, multilingual evaluation, release, evidence, audit, closure | 8–13 days | 8–15 days | Full closure control set complete |

Estimates are planning ranges, not calendar promises. Rights, curriculum, and language review may dominate elapsed time.

A mandatory re-estimation occurs at the end of Gate 2R.0 after the live repository baseline, source-inventory proposal, rights risks, non-production extraction sample, review-interface decision, legacy volume, and ADRs are known. The updated estimate and the approved plan/start commit must be recorded before Gate 2R.1 begins.

The Gate 2R.0–2R.8 engineering ranges total **72–108 person-days**, matching the document-level planning estimate. Human review ranges are tracked separately and must not be converted into engineering completion claims.

### 28.2 Detailed work breakdown

| ID | Work item | Acceptance criteria | Owner role | Depends on | Status |
|---|---|---|---|---|---|
| P02R-0001 | Confirm canonical repository, branch, base SHA, worktree, toolchain | E-02R-001 through E-02R-013 complete | Release manager | None | Completed at Gate 2R.0 |
| P02R-0002 | Reconcile Phase 1–7 actual state | Tests/evidence/status gaps recorded; no inherited completion claims | Evidence custodian | P02R-0001 | Completed at Gate 2R.0 |
| P02R-0003 | Approve ADR-02R-001 through ADR-02R-013 | All ADRs reviewed and committed | Engineering approver | P02R-0001 | Completed at Gate 2R.0 |
| P02R-0004 | Freeze first-closure source inventory scope | Signed completeness-register scope and amendment rule | Curriculum + rights owners | P02R-0003 | Completed at Gate 2R.0; item resolution remains Gate 2R.1 |
| P02R-0005 | Verify Phase 0 or equivalent reproducibility controls | Clean-checkout/toolchain/environment/CI baseline evidenced | Programme + engineering owners | P02R-0001 | Completed at Gate 2R.0 |
| P02R-0006 | Verify `02R` identifier compatibility | Status, Atlas, evidence, sorting, CI, and templates support `02R` forms | Evidence custodian + engineering | P02R-0001 | Completed at Gate 2R.0 |
| P02R-0101 | Add authoritative source catalogue schema | Migration/model constraints pass | Database owner | P02R-0003 | Implemented; disposable PostgreSQL migration, schema, and append-only proof passed. Candidate evidence collected and committed; independent approval pending |
| P02R-0102 | Add per-use rights decision schema and policy engine | Missing/expired/denied use fails closed; translation/publication permissions and structured conditions are machine-enforced | Rights + engineering owners | P02R-0101 | Implemented; first-slice real rights decision loader passed in disposable PostgreSQL. Independent rights approval pending |
| P02R-0103 | Implement completeness register and validator | All mandatory inventory rows deterministically validated | Curriculum owner | P02R-0004 | Implemented; source-completeness register frozen. Candidate evidence collected and committed; independent approval pending |
| P02R-0104 | Implement independent review-domain ledgers | Rights/extraction/mapping/content/answer decisions cannot imply one another | Engineering owner | P02R-0101 | Implemented; independent approvals pending |
| P02R-0201 | Implement object-storage abstraction | Immutable keys/versions and local dev adapter pass | Operations + engineering | P02R-0101 | Not started |
| P02R-0202 | Implement secure acquisition | Allowlist, redirects, limits, checksums, audit logs pass | Security + engineering | P02R-0201 | Not started |
| P02R-0203 | Integrate malware scanning/quarantine | Unsafe file never reaches extraction | Security owner | P02R-0202 | Not started |
| P02R-0204 | Implement source change detection | Checksum/metadata/version changes create reviewed events | Engineering owner | P02R-0202 | Not started |
| P02R-0205 | Verify database and object-store backup restoration | Restored database, object manifest, hashes, access controls, and active-corpus reconstruction pass | Operations + database owners | P02R-0201–0204 | Not started |
| P02R-0301 | Implement versioned extraction runs and page records | Reproducible extraction manifests and page hashes | Engineering owner | P02R-0203 | Not started |
| P02R-0302 | Implement native PDF extraction | Text/layout/pages preserved | Engineering owner | P02R-0301 | Not started |
| P02R-0303 | Implement controlled OCR fallback | OCR is identifiable and low confidence queues review | Engineering owner | P02R-0302 | Not started |
| P02R-0304 | Implement structure-aware sections/chunks | Tables/formulas/examples preserve meaning and page links | Engineering owner | P02R-0302 | Not started |
| P02R-0305 | Implement extraction review workflow | Reviewer decisions append-only; rejected chunks ineligible | Curriculum reviewer | P02R-0304 | Not started |
| P02R-0401 | Add curriculum node/version/edge schema | Constraints and effective-version resolution pass | Database owner | P02R-0101 | Not started |
| P02R-0402 | Import existing registries as proposals only | No imported mapping auto-approved | Engineering owner | P02R-0401 | Not started |
| P02R-0403 | Implement mapping proposal and review workflow | Every active mapping has reviewer/rationale | Curriculum owner | P02R-0305, P02R-0401 | Not started |
| P02R-0404 | Complete Grade 4 Mathematics mapping | Terms 1–4 and five strands have approved Tier 1 support | Curriculum owner | P02R-0403 | Not started |
| P02R-0405 | Implement multilingual labels/translation links | Authority and derivative language states explicit | Language + curriculum owners | P02R-0403 | Not started |
| P02R-0406 | Implement supported human-review interface/CLI | Inventory/absence, rights lifecycle, extraction retry/quarantine, mapping, translation, corpus review, source-change, stale-artifact disposition, and assignment decisions are operable, attributable, maker-checker-safe, and accessible | Frontend/CLI + governance owners | P02R-0104, P02R-0305, P02R-0403 | Not started |
| P02R-0501 | Add corpus version, membership, freeze, activation ledgers | Manifests immutable and hashed | Database owner | P02R-0404 | Not started |
| P02R-0502 | Implement deterministic corpus builder | Same inputs produce same manifest hash | Engineering owner | P02R-0501 | Not started |
| P02R-0503 | Implement database-atomic activation, transactional outbox, versioned-cache safety, and rollback | Concurrency, delayed/duplicate/failed outbox, stale-cache, mixed-version, and rollback tests pass | Engineering owner | P02R-0502 | Not started |
| P02R-0504 | Refactor retrieval as active-corpus projection | Every hit carries corpus/source/chunk/mapping versions | Retrieval owner | P02R-0503 | Not started |
| P02R-0505 | Add synthetic-corpus production guard | Build/activation/serving fails on synthetic membership | Retrieval owner | P02R-0504 | Not started |
| P02R-0506 | Freeze and activate first real corpus in controlled evaluation/staging only | Curriculum, rights, security reviews complete; production activation remains blocked | Release manager | P02R-0501–0505 | Not started |
| P02R-0507 | Integrate Phase 6 accounting | Embedding, OCR/AI extraction, mapping, validation, verification, generation, tutor, and evaluation costs are reserved/finalised | AI operations owner | P02R-0202, P02R-0502 | Not started |
| P02R-0601 | Define grounding policy and typed failures | Policy versioned and contract tested | Generation owner | P02R-0504 | Not started |
| P02R-0602 | Refactor Phase 1 generation | Every production path resolves active corpus and persists provenance | Generation owner | P02R-0601 | Not started |
| P02R-0603 | Remove/isolate generation/import bypasses | No production hardcoded approval/alignment/verification | Generation owner | P02R-0602 | Not started |
| P02R-0604 | Implement claim extraction/support records | Curriculum claims map to Tier 1 support | Generation owner | P02R-0602 | Not started |
| P02R-0605 | Implement unsupported-claim and overlap controls | Unsupported/excessive-copy artifacts block | Generation + rights owners | P02R-0604 | Not started |
| P02R-0606 | Implement deterministic-first answer verification | Verification independent and edit-invalidated | Assessment owner | P02R-0602 | Not started |
| P02R-0607 | Correct Phase 3 interaction | Quorum cannot set answer verification; publication checks both domains | Governance owner | P02R-0606 | Not started |
| P02R-0701 | Extend tutor grounding schema | Required provenance fields persisted | Tutor owner | P02R-0504 | Not started |
| P02R-0702 | Refactor tutor context retrieval | Active corpus hierarchy and policy enforced | Tutor owner | P02R-0701 | Not started |
| P02R-0703 | Implement non-authoritative fallback | No unsupported CAPS claim during fallback | Tutor + safety owners | P02R-0702 | Not started |
| P02R-0704 | Add metrics, alerts, and runbooks | Operational acceptance tests pass | Operations owner | P02R-0702 | Not started |
| P02R-0705 | Refactor study-plan curriculum resolution | Plans use active approved nodes/prerequisites, persist provenance, and become stale after relevant changes | Study-plan owner | P02R-0404, P02R-0503 | Not started |
| P02R-0706 | Refactor Phase 7 coverage reporting | Source, mapping, chunk, lesson, assessment, and language coverage are separate | Curriculum coverage owner | P02R-0506, P02R-0705 | Not started |
| P02R-0707 | Implement audience-specific provenance display | Reviewer, educator, learner, guardian, operator, and auditor views enforce rights and access rules | Frontend/API + governance owners | P02R-0406, P02R-0604, P02R-0702 | Not started |
| P02R-0801 | Inventory and classify legacy artifacts | Counts reconcile to all relevant records/files | Migration owner | P02R-0607, P02R-0703 | Not started |
| P02R-0802 | Quarantine/withdraw/regenerate legacy content | Every learner-serving artifact has disposition | Migration + content owners | P02R-0801 | Not started |
| P02R-0803 | Build real-corpus evaluation dataset | 18+ positive; at least 10 negative or one per mandatory exclusion class, whichever is greater; five strands, three languages, real chunk IDs, subgroup labels | Evaluation + language owners | P02R-0506 | Not started |
| P02R-0804 | Run retrieval/generation/tutor evaluation | Thresholds pass; zero prohibited hits | Evaluation owner | P02R-0803 | Not started |
| P02R-0805 | Run Phase 1–7 regression and PostgreSQL gates | Zero failures/unexpected skips | Engineering owner | P02R-0802–0804 | Not started |
| P02R-0806 | Complete implementation report and freeze candidate evidence | All plan items reconciled; candidate evidence hashed and labelled provisional | Evidence custodian | P02R-0805 | Not started |
| P02R-0807 | Pre-merge independent audit and remediation | Candidate audit report/verdict is recorded as E-02R-135; no unresolved High/Critical before merge approval | Auditor | P02R-0806 | Not started |
| P02R-0808 | Obtain merge approval after remediation | Candidate source and audit-remediation state accepted for canonical merge | Engineering approver + release manager | P02R-0807 | Not started |
| P02R-0809 | Canonical merge and post-merge verification | Merge SHA and required CI/verification evidence recorded | Release manager | P02R-0808 | Not started |
| P02R-0810 | Regenerate and finalise merge-commit evidence | Final evidence references clean canonical merge state and valid hashes | Evidence custodian | P02R-0809 | Not started |
| P02R-0811 | Auditor merge-state addendum and final verdict | E-02R-136 verifies merge-state evidence; E-02R-123 binds the candidate audit and addendum into the final Pass/Pass-with-observations/Fail control | Auditor | P02R-0810 | Not started |
| P02R-0812 | Closure approval and status update | All signatories approve; status register updated last | Final phase approver | P02R-0811 | Not started |

---

## 29. Migration, Compatibility, Deployment, Rollback, and Recovery

### 29.1 Migration approach

Use expand–migrate–contract:

1. add authoritative tables, constraints, and indexes without changing serving behaviour;
2. deploy read/write support behind disabled feature flags;
3. ingest and review sources;
4. build candidate corpus and retrieval projection;
5. dual-read in controlled non-learner environments for comparison;
6. activate authoritative-corpus enforcement in staging;
7. migrate/classify legacy artifacts;
8. activate in production only after acceptance and approvals;
9. remove or isolate obsolete production bypasses only after replacement verification.

### 29.2 Migration-head rule

The migration must be based on the **actual** canonical Alembic head at execution time. The archive-reported head is contextual only.

No hardcoded revision ID may be accepted before preflight.

### 29.3 Backups

- schema/data backups must be stored outside the repository;
- object-storage manifests and checksums must be exported before activation;
- backup identifiers, encryption, retention, and restore tests must be evidenced;
- no secret or restricted source text may be committed to Git evidence.

### 29.4 Feature flags

Planned flags:

```text
AUTHORITATIVE_CORPUS_ENABLED
AUTHORITATIVE_CORPUS_REQUIRED_FOR_GENERATION
AUTHORITATIVE_CORPUS_REQUIRED_FOR_TUTOR
LEGACY_UNGROUNDED_SERVING_DISABLED
CROSS_LINGUAL_GROUNDING_ENABLED
```

Production defaults after cutover must fail closed. Flags may not allow blocked or superseded content.

### 29.5 Rollback triggers

- wrong-version, blocked-source, or rights-ineligible retrieval;
- corpus activation inconsistency;
- unacceptable extraction/mapping defect;
- grounding bypass;
- material Phase 1–7 regression;
- stale/withdrawn content still serving;
- security incident or object checksum mismatch.

### 29.6 Rollback steps

1. disable affected generation/tutor path or activate safe fallback;
2. atomically reactivate the previous eligible corpus where permitted;
3. quarantine affected artifacts/messages;
4. preserve failed version and logs for audit;
5. notify rights/curriculum/security owners as applicable;
6. run recovery verification;
7. document cause and corrective action before reactivation.

Schema downgrade is not the primary production rollback. Prefer forward-compatible disablement and corpus reactivation; destructive downgrades require explicit approval and tested backups.

---

## 30. Test and Verification Plan

The complete test and verification matrix is controlled in Appendix B.

Mandatory principles remain authoritative in this main plan:

- scenario and invariant coverage outrank raw test counts;
- no unexpected database-gated skips;
- clean upgrade and actual-baseline upgrade;
- constraints, append-only decisions, activation concurrency, rollback, rights expiry, retrieval projection, grounding, answer verification, tutor, study plan, coverage, accounting, backup restoration, security, OpenAPI, architecture, Atlas, and Phase 1–7 regressions;
- every gate must be committed, verified, evidenced, and exited before the next gate is applied;
- final verification is repeated on the canonical merge commit.

Controlled appendix:

- `phase_02r_appendix_b_test_and_evaluation_matrix.md`
- version `1.4`
- SHA-256 `6b0c825f1be3a123fc3e47c04744c3e877eb452966284898816a4361ccfa4367`

---
## 31. Real-Corpus Evaluation Plan

Closure evaluation uses real active-corpus chunk version IDs, curriculum-reviewed graded relevance judgments, and a frozen dataset hash.

Minimum content:

- one positive case for each of the 15 strand-language combinations;
- at least 18 positive cases overall;
- at least 10 negative cases or one per mandatory exclusion class, whichever is greater;
- graded pooled relevance judgments for Precision@5 and nDCG@5;
- separate Hit Rate@5/Recall@5 where only one canonical target exists;
- a separate 500+ query reproducible latency workload;
- zero observed prohibited publications/hits in the approved evaluation set, with sample size and confidence limitations reported;
- zero-tolerance operational policy for blocked, expired, withdrawn, superseded, wrong-version, unreviewed, synthetic, wrong-key, and restricted-excerpt outcomes.

Thresholds and full methodology are controlled in Appendix B:

- SHA-256 `6b0c825f1be3a123fc3e47c04744c3e877eb452966284898816a4361ccfa4367`

---
## 32. Evidence-Pack Plan

Evidence is lifecycle-specific:

```text
start-gate design/dependency evidence
→ gate implementation evidence
→ candidate feature-branch evidence
→ pre-merge audit evidence
→ canonical merge/post-merge evidence
→ final auditor addendum and closure evidence
```

Feature-branch evidence is provisional. Final evidence must reference the clean canonical merge commit and validate every raw-file hash.

The complete inventory, evidence schema, sensitivity rules, and revalidation triggers are controlled in:

- `phase_02r_appendix_c_evidence_inventory.md`
- version `1.4`
- SHA-256 `295ba3bb8cdadaae6c6dc6925b07afa2b9e67be91bb1028b736105d15231f39d`

---
## 33. Script-Driven Workflow

The implementation phase must produce gate-aware scripts:

```text
preflight_phase02r.sh
apply_phase02r_patch.sh
verify_phase02r.sh
verify_phase02r_postgres.sh
collect_phase02r_evidence.sh
```

Every script must accept an explicit gate, for example:

```bash
bash scripts/preflight_phase02r.sh --gate 2R.0 --mode discovery
bash scripts/preflight_phase02r.sh --gate 2R.3 --mode implementation
bash scripts/apply_phase02r_patch.sh --gate 2R.3
bash scripts/verify_phase02r.sh --gate 2R.3
bash scripts/verify_phase02r_postgres.sh --gate 2R.3
bash scripts/collect_phase02r_evidence.sh --gate 2R.3
```

Gate 2R.0 preflight/verification may run with `PHASE_02R_START_APPROVED=false` only in read-only discovery mode. `apply_phase02r_patch.sh --gate 2R.0` is prohibited. Gates 2R.1–2R.8 may be applied only after the approved Gate 2R.0 exit commit sets the flag to `true`, and after the prior implementation gate has a committed state, passing verification, attributable evidence, and recorded exit decision. `--all` is prohibited for production implementation; it may exist only for read-only final verification after all gates are complete.

### 33.1 `preflight_phase02r.sh`

Must verify:

- canonical branch/remote/base SHA;
- clean worktree;
- for Gate 2R.0 discovery mode: draft plan identity, permitted read-only scope, and `PHASE_02R_START_APPROVED=false`;
- for Gates 2R.1–2R.8: approved and committed plan plus the immutable Gate 2R.0 approval commit;
- `PHASE_02R_START_APPROVED=true` only for Gates 2R.1–2R.8 after approval;
- actual Alembic head;
- Atlas paths and no duplicate non-Atlas control set;
- `.venv/bin/python` or `PYTHON_BIN`;
- current Phase 1–7/reconciliation state;
- object-storage configuration;
- named reviewers/auditor;
- no unsupported completion claims;
- backups target outside repository.
- requested gate is valid, prior-gate commit/evidence/exit decision exists, and later-gate files are not being applied early.

### 33.2 `apply_phase02r_patch.sh`

Must:

- fail if preflight fails;
- refuse Gate 2R.0 and any invocation while `PHASE_02R_START_APPROVED=false`;
- create backups outside repository;
- be idempotent;
- validate expected source boundaries;
- apply code, migrations, tests, docs, and fixtures;
- never ingest unreviewed external sources automatically;
- update phase status to `In Progress` only;
- apply only the explicitly requested gate and refuse `--all` implementation mode;
- create a gate-specific change manifest and expected source-boundary hash;
- never approve the corpus, audit, or phase completion.

### 33.3 `verify_phase02r.sh`

Must run or orchestrate:

- compilation and critical Ruff;
- focused Phase 2R suites;
- Phase 1–7 regressions;
- migration graph and schema integrity;
- OpenAPI drift and import boundaries;
- Atlas control-set validation;
- source catalogue/completeness/rights validators;
- corpus manifest and synthetic guard;
- generation/tutor grounding checks;
- legacy reconciliation;
- multilingual evaluation;
- operations/runbook checks.
- gate-specific acceptance criteria and prior-gate immutability checks;

### 33.4 `verify_phase02r_postgres.sh`

Must run against isolated PostgreSQL/pgvector:

- clean upgrade;
- upgrade from actual baseline head;
- constraints and append-only review tests;
- source version/supersession/effective-date tests;
- rights fail-closed tests;
- corpus build/activation/concurrency/rollback;
- retrieval projection and wrong-version exclusion;
- generation/tutor persistence;
- legacy migration;
- safe downgrade/re-upgrade where approved;
- zero unexpected skips.
- gate-specific database scope and prior-gate migration compatibility;

### 33.5 `collect_phase02r_evidence.sh`

Must:

- run only after implementation commit;
- record source state and environment;
- invoke verifiers and retain failures;
- write raw outputs and machine-readable summaries;
- hash every raw file;
- distinguish feature-branch from merge-commit evidence;
- identify missing artifacts, stale hashes, unresolved approvals, and findings;
- preserve nonzero exit status;
- generate a gate report and gate evidence index before final phase-wide evidence;
- never self-approve or mark completion.

---

## 34. Phase Audit Plan

Phase 2R requires independent technical audit plus competent curriculum and rights review. Any unresolved Critical or High finding requires `Fail`.

The final audit sequence is:

```text
candidate evidence
→ pre-merge independent audit (E-02R-135)
→ remediation and merge approval
→ canonical merge
→ post-merge verification and final evidence
→ auditor merge-state addendum/final verdict (E-02R-136)
→ combined final audit control (E-02R-123)
→ closure approval
```

The complete sampling floors and mandatory reproduction procedures are controlled in:

- `phase_02r_appendix_d_audit_sampling.md`
- version `1.4`
- SHA-256 `37b2fdf06a932697357e0a236178f190d0f3cef360a091bead1eb01ed77b860c`

---
## 35. Risks, Assumptions, and Stop Conditions

| ID | Risk/assumption | Probability | Impact | Mitigation | Stop condition | Owner |
|---|---|---:|---:|---|---|---|
| R-02R-001 | Official source inventory is incomplete or ambiguous | Medium | Critical | Signed completeness register and curriculum review | Tier 1 authority cannot be established | Curriculum owner |
| R-02R-002 | Rights for storage/embedding/prompt/derivative use are unclear | High | Critical | Per-use review; deny by default | Any mandatory active-source use unresolved | Rights reviewer |
| R-02R-003 | Official `af`/`nso` source versions do not exist | Medium | High | Explicit translation status and reviewed cross-lingual policy | System would need to mislabel derivative text as authority | Language owner |
| R-02R-004 | PDF extraction corrupts formulas/tables | Medium | High | Layout-aware extraction, OCR controls, human sampling | Quality below approved threshold | Extraction owner |
| R-02R-005 | Current retrieval schema encourages overwriting | High | High | Separate immutable authority model and projection | Authoritative history would be mutated | Database owner |
| R-02R-006 | Existing generation/import bypasses remain reachable | High | Critical | Inventory all paths; production guard and tests | Any learner-facing path bypasses grounding | Generation owner |
| R-02R-007 | LLM validator approves its own unsupported claims | Medium | High | Structured support records, deterministic policy checks, human review | Mandatory claim lacks Tier 1 support | Generation owner |
| R-02R-008 | Answer verification relies on second LLM only | Medium | High | Deterministic-first checkers and edit invalidation | Quorum/model-only verification is required for publication | Assessment owner |
| R-02R-009 | Source change leaves stale artifacts serving | Medium | Critical | Impact graph, stale status, alerts, emergency disable | Withdrawn/changed source still serves without decision | Operations owner |
| R-02R-010 | Legacy dataset is too large for complete review | High | High | Deterministic inventory; quarantine by default; prioritised regeneration | Unclassified learner-serving artifact remains | Migration owner |
| R-02R-011 | Reviewer capacity delays phase | High | Medium | Freeze scope; schedule reviews; no automatic approval | Required reviews unavailable | Phase owner |
| R-02R-012 | Phase scope absorbs unrelated audit remediation | Medium | Medium | Separate roadmap and change control | Work expands without approved amendment | Programme owner |
| R-02R-013 | Evidence collected from wrong source state | Medium | Critical | Clean worktree, commit attribution, post-merge rerun | Final evidence is feature-branch-only or dirty | Evidence custodian |
| R-02R-014 | Production corpus contains restricted excerpts | Low/Med | Critical | Rights-aware excerpt policy and access controls | Restricted text exposed beyond permission | Security + rights owners |
| R-02R-015 | Object storage unavailable or not immutable | Medium | High | Preflight and local adapter only for dev | Original integrity cannot be proven | Operations owner |
| R-02R-016 | Existing tooling assumes numeric-only phase identifiers | Medium | High | Compatibility validator and preflight gate | `02R` omitted, mis-sorted, or collector fails | Evidence custodian |
| R-02R-017 | Review workflows exist only as raw API/SQL operations | Medium | High | Supported authenticated accessible UI/CLI | Required human reviews cannot be operated reliably | Governance + frontend owners |
| R-02R-018 | Evaluation thresholds are adjusted after results | Medium | High | Freeze thresholds in approved plan; amendment and full rerun | Threshold is weakened post hoc | Evaluation owner |
| R-02R-019 | Phase 2R provider/embedding/OCR costs bypass Phase 6 authority | Medium | High | Mandatory reservation/finalisation integration | Unaccounted AI operation reaches production | AI operations owner |
| R-02R-020 | Study plans or coverage reports continue using synthetic/inactive nodes | Medium | Critical | Explicit Phase 2R integrations and regression tests | Unsupported plan or false CAPS coverage is produced | Study-plan + coverage owners |
| R-02R-021 | Activation commits but outbox/cache side effects lag or fail | Medium | Critical | Binding epoch, versioned cache keys, idempotent outbox retries, dead-letter alerts | Retrieval can select a corpus inconsistent with the authoritative binding | Retrieval + operations owners |
| R-02R-022 | Conditional rights are stored only as prose and cannot be enforced | Medium | Critical | Structured conditions, policy tests, denial on evaluation failure | An active use depends on an unevaluated or ambiguous condition | Rights + engineering owners |

### 35.1 Absolute stop conditions

Stop implementation, activation, audit, or closure if:

- the plan is not approved and committed;
- owner, reviewer, custodian, release manager, or auditor roles remain unassigned at start;
- canonical branch/base SHA/migration head are unknown;
- source authority cannot be established;
- any mandatory rights use remains unresolved or a structured condition cannot be evaluated deterministically;
- source object hashes are unstable or unverifiable;
- malware/security review fails;
- extraction quality is unacceptable;
- mappings are unreviewed;
- production retrieval includes synthetic, blocked, superseded, withdrawn, wrong-version, or rights-ineligible chunks;
- the authoritative active binding, binding epoch, cache key, or retrieval corpus cannot be reconciled;
- activation outbox dead-letter/backlog exceeds the approved safety threshold without safe-disable or incident response;
- generation succeeds without sufficient Tier 1 grounding;
- tutor claims curriculum authority without grounding;
- educator quorum implies answer verification;
- a learner-serving legacy artifact remains unclassified;
- evidence hashes fail;
- final evidence is not attributable to the canonical merge commit;
- audit is pending or has unresolved Critical/High findings;
- post-merge CI is not green.

---

## 36. Change Control

Material changes require a versioned plan amendment approved before affected work is accepted.

Material changes include:

- changing the bounded source inventory or authority tiers;
- changing a rights rule or allowing an unreviewed use;
- changing immutable source/version semantics;
- changing chunking, mapping, corpus membership, or activation policy;
- allowing generation without Tier 1 support;
- changing multilingual fallback or authority labelling;
- changing claim/overlap/answer verification rules;
- grandfathering learner-serving legacy artifacts;
- reducing evaluation coverage or thresholds;
- changing object storage or evidence requirements;
- reducing audit sampling;
- weakening publication or staleness rules.

No implementation convenience or failed target may silently redefine success.

### 36.1 Change log

| Version | Date | Change | Reason | Evidence/audit impact | Approved by |
|---|---|---|---|---|---|
| 1.0 | 2026-06-16 | Initial formal execution plan compiled from handover, repository discovery, and review feedback | Establish controlled Phase 2R start gate | Full plan establishes evidence/audit scope | Pending |
| 1.1 | 2026-06-16 | Added Phase 0 prerequisite, activation key, cross-phase integrations, review tooling, fixed thresholds, legal escalation, storage policy, multilingual matrix, `02R` compatibility, provenance display, and controlled appendices | Close initial execution-readiness gaps | Expanded preflight, work, evidence, audit, and closure scope | Pending |
| 1.2 | 2026-06-16 | Corrected section numbering, evidence-label ambiguity, and navigation | Structural correctness | No control weakening | Pending |
| 1.3 | 2026-06-16 | Reconciled estimates and commands; refined activation, inventory, storage, translation, gate scripts, audit order, evaluation methodology, evidence lifecycle, separation of duties, acquisition security, rights expiry, staging activation, negative coverage, restoration proof, and actual appendix split | Resolve final execution-readiness findings | Material plan expansion; renewed approval required | Pending |
| 1.4 | 2026-06-16 | Added transactional-outbox activation, explicit pre-start Gate 2R.0, translation permissions/structured rights conditions, immutable-authority versus projection rules, stronger negative minimum, separate audit identities, complete control surfaces, subgroup reporting, source-activation semantics, database constraints, package manifest, and validation report | Resolve third-review control inconsistencies and implementation ambiguities | Material control refinement; renewed approval required | Pending |

---

## 37. Required Implementation Report

The phase must produce:

```text
docs/roadmap/execution/atlas/phase_02r_implementation_report.md
```

It must reconcile:

- every `P02R-*` work item;
- planned versus actual architecture and schema;
- source inventory and rights decisions;
- files changed and migrations added;
- source/object/extraction/mapping/corpus counts;
- corpus version and activation history;
- generation/tutor integration;
- claim and answer validation;
- legacy classification/disposition counts;
- test totals, failures, warnings, skips, xfails, retries;
- evaluation results;
- security/privacy/safeguarding impacts;
- plan amendments;
- defects and residual risks;
- evidence IDs;
- audit readiness;
- canonical merge and post-merge CI.

The report may not claim closure while evidence, audit, merge, CI, or approvals are pending.

---

## 38. Phase Status Lifecycle

Phase 2R may move only through:

```text
Not Started
→ Planning
→ Ready to Start
→ In Progress
→ Verification Pending
→ Evidence Complete
→ Audit Review
→ Closure Review
→ Verified Complete
```

No state may be skipped.

The following are not completion states:

```text
Code Complete
Locally Verified
Ready for Review
PR Open
Feature Branch Green
Evidence Collected
Audit Pending
Merge Pending
Documentation Complete
```

---

## 39. Historical Gate 2R.0 Start-Gate Checklist

- [x] Canonical plan path is correct.
- [ ] This plan is reviewed and committed.
- [x] `PHASE_02R_START_APPROVED=false` has not been changed prematurely.
- [ ] Canonical branch, remote, base SHA, and clean worktree are recorded. Branch/remote/base are recorded; clean worktree is blocked by existing dirty reconciliation/source/evidence changes.
- [x] Actual Alembic head and migration graph are recorded.
- [ ] Phase 1–7 actual state and relevant audit blockers are reconciled. Actual state is recorded in the Gate 2R.0 initial report and rerun closure report; the combined verifier is now fail-closed for closure mode but still must pass from a clean source state.
- [ ] Phase 0 is `Verified Complete` or equivalent reproducibility controls are formally absorbed into Gate 2R.0 and evidenced. Phase 0 is planning only and equivalent clean-checkout evidence is not yet complete.
- [ ] `02R` identifier compatibility passes across status, Atlas, evidence, templates, CI, sorting, and collectors. The planned compatibility validator does not exist yet.
- [x] Source scope and completeness-register categories are proposed for approval.
- [x] All owner and reviewer names are assigned.
- [x] Rights-review framework is accepted as fail-closed for planning.
- [x] Curriculum and language review scope is accepted for planning.
- [ ] Auditor independence and sampling are accepted. Sampling is accepted; independence conflict is disclosed and requires compensating controls.
- [ ] Gate 2R.0 read-only discovery is complete and all required ADRs are approved before any Gate 2R.1 schema work. Discovery is complete; blockers remain.
- [x] Corpus activation resolution key and multilingual activation model are recorded.
- [x] Extracted-text storage model is recorded.
- [x] Supported human-review interface/CLI approach is recorded.
- [x] Numeric evaluation and grounding thresholds are frozen in the plan.
- [x] Study-plan, Phase 6 accounting, Phase 7 coverage, and provenance-display integrations are accepted for planning.
- [ ] Object storage and backup targets are available. Required, but availability is not proven.
- [x] Work estimates, dependencies, WIP order, stop conditions, and rollback are accepted for planning.
- [x] Evidence inventory and sensitivity rules are accepted for planning.
- [x] Audit-remediation workstream boundary is accepted.
- [x] No Gate 2R.1–2R.8 production implementation has begun before approval; Gate 2R.0 activity is demonstrably read-only.

This checklist records the pre-approval review state. The later immutable Gate 2R.0 approval transition is recorded in the start-gate control. It changed:

```text
PHASE_02R_START_APPROVED=true
```

---

## 40. Gate Transition Record

| Transition | Decision | Immutable reference | Current effect |
|---|---|---|---|
| Gate 2R.0 evidence review | Accepted with disclosed single-developer compensating controls | `851f3e16b83d8d1cd9b531ed29dbfe2f5b278e73` | Eligible for start approval |
| Gate 2R.0 approval | Approved | `d2b243ca4a3f75e4b50a0afaed046bacabf7c7b9` | Authorises Gate 2R.1 only |
| Gate 2R.1 premature closure claim | Superseded / invalid | `docs/release-evidence/atlas/phase-02r/gate-2r1/superseded/2026-06-16-premature-transition/` | No authority |
| Gate 2R.1 current state | In Progress | This v1.5 amendment and implementation patch | Gate 2R.2 remains blocked |

**Current decision:** Gate 2R.4 is Verified Complete. Gate 2R.5 is Authorised. `PHASE_02R_START_APPROVED` remains `true` because Phase 2R execution has started, and the current gate control authorises Gate 2R.5 only.

---

## 41. Closure Acceptance Checklist

Phase 2R may enter `Verified Complete` only when:

### Source and rights

- [ ] Bounded Grade 4 Mathematics source-completeness register is signed.
- [ ] All five strands and Terms 1–4 have approved Tier 1 evidence.
- [ ] Every active source version has authority and per-use rights decisions, including explicit translation/publication permissions and satisfied structured conditions where applicable.
- [ ] Every active original object is immutable and hash-verified.
- [ ] No source with unresolved, expired, rejected, withdrawn, or disputed rights is active.
- [ ] Any ambiguous derivative, commercial, redistribution, translation, or model-training use has authorised legal review or written rights-holder permission.

### Extraction, mapping, and corpus

- [ ] Page-level provenance is preserved.
- [ ] Extraction samples and low-confidence pages pass review.
- [ ] Curriculum nodes and mappings are human-approved.
- [ ] Language and translation states are explicit.
- [ ] A deterministic frozen corpus manifest exists.
- [ ] Database-atomic activation, transactional-outbox delivery safety, stale-cache rejection, and rollback pass.
- [ ] Production retrieval uses only active manifest memberships.
- [ ] Synthetic fixtures are excluded from production.
- [ ] Activation-key resolution is consistent across database, cache, retrieval, generation, tutor, rollback, metrics, and evidence.
- [ ] Extracted-text storage and access controls match ADR-02R-011.
- [ ] Supported human-review UI/CLI passes authorisation, audit, and accessibility gates.

### Generation, verification, and tutor

- [ ] All production generation paths require sufficient Tier 1 grounding.
- [ ] Generated artifacts persist complete source/corpus provenance.
- [ ] Unsupported claims and excessive copying are blocked.
- [ ] Independent answer verification is separate from educator review.
- [ ] Edits invalidate prior answer verification.
- [ ] Tutor retrieves from active corpus or uses explicit non-authoritative fallback.
- [ ] Tutor provenance is persisted.
- [ ] Study plans use only approved active nodes/prerequisites, persist provenance, and pass staleness tests.
- [ ] Phase 7 reports source, mapping, chunk, lesson, assessment, and language coverage separately.
- [ ] Phase 6 accounts every applicable Phase 2R AI, OCR, embedding, validation, verification, generation, tutor, and evaluation operation.
- [ ] Provenance displays are correct and access-controlled for each audience.

### Legacy, evaluation, security, and operations

- [ ] Every learner-serving legacy artifact is classified and dispositioned.
- [ ] Real-corpus evaluation has at least 18 positive cases and at least 10 negative cases or one case for every mandatory exclusion class, whichever is greater.
- [ ] All five strands and three languages are represented.
- [ ] Metrics are reported by language, strand, term, authority/translation state, and same-language versus cross-lingual mode; no subgroup contains a prohibited hit.
- [ ] Zero blocked, withdrawn, superseded, wrong-version, unreviewed, or synthetic production hits occur.
- [ ] Security negative scenarios pass.
- [ ] Metrics, alerts, and runbooks pass operational acceptance.

### Engineering and governance

- [ ] Phase 1–7 required regressions pass.
- [ ] Phase 0/equivalent reproducibility and `02R` identifier compatibility gates pass.
- [ ] Migration, schema, OpenAPI, and architecture checks pass.
- [ ] Implementation report is complete.
- [ ] Evidence pack is complete and hashed.
- [ ] Independent audit passes.
- [ ] No Critical or High finding remains.
- [ ] Canonical merge is complete.
- [ ] Post-merge CI passes on the merge commit.
- [ ] Closure approval matrix is complete.
- [ ] Phase-status register is updated last.

---

## 42. Closure Approval Matrix

| Role | Required decision | Name | Date | Immutable reference |
|---|---|---|---|---|
| Phase owner | Recommend close | Nkgolo Lebelo | Not yet due | Pending closure |
| Engineering approver | Approve implementation | Nkgolo Lebelo | Not yet due | Pending closure |
| Curriculum reviewer | Approve mappings and corpus | Nkgolo Lebelo | Not yet due | Pending closure |
| Rights reviewer | Approve active-source rights register | Nkgolo Lebelo | Not yet due | Pending closure |
| Language reviewer(s) | Approve multilingual evaluation and derivative language quality | Nkgolo Lebelo | Not yet due | Pending closure |
| Security/privacy/safeguarding reviewer | Approve | Nkgolo Lebelo | Not yet due | Pending closure |
| Evidence custodian | Evidence complete and hashes valid | Nkgolo Lebelo | Not yet due | Pending closure |
| Independent auditor | Pass or Pass with non-blocking observations | Nkgolo Lebelo | Not yet due | Pending closure |
| Release manager | Canonical merge and post-merge CI verified | Nkgolo Lebelo | Not yet due | Pending closure |
| Final phase approver | `Verified Complete` / Reject | Nkgolo Lebelo | Not yet due | Pending closure |

No one person should approve every role. In a single-developer context, independent curriculum review, rights review, command reproduction, raw evidence, post-merge CI, and explicit conflict declarations are mandatory compensating controls.

---

## 43. Planned Deliverables

### Governance and design

1. canonical Phase 2R execution plan;
2. baseline/reconciliation report;
3. source-completeness register;
4. rights policy and decision template;
5. ADR-02R-001 through ADR-02R-013;
6. threat model and data-flow update;
7. evidence and audit plans;
8. Phase 0/equivalent reproducibility baseline decision;
9. `02R` identifier compatibility validator;
10. corpus activation-key and multilingual activation specification;
11. extracted-text storage ADR;
12. human-review interface/CLI specification;
13. frozen evaluation-threshold record.

### Implementation

1. migrations and ORM/domain models;
2. source catalogue and rights register;
3. object-storage adapter and acquisition pipeline;
4. malware/security scan integration;
5. extraction/page/section/chunk pipeline;
6. extraction and mapping review workflows;
7. curriculum graph;
8. corpus build/freeze/activation/rollback;
9. retrieval projection refactor;
10. synthetic-corpus closure guard;
11. mandatory grounded generation;
12. claim/copying validation;
13. independent answer verification;
14. Phase 3 publication integration correction;
15. grounded tutor integration;
16. source-change and stale-artifact processing;
17. legacy migration;
18. multilingual real-corpus evaluation;
19. metrics, alerts, dashboards, and runbooks;
20. protected APIs and durable jobs;
21. supported accessible human-review UI or approved review CLI;
22. Phase 6 accounting integration;
23. grounded study-plan integration;
24. decomposed Phase 7 coverage integration;
25. audience-specific provenance displays.

### Verification and closure

1. `preflight_phase02r.sh`;
2. `apply_phase02r_patch.sh`;
3. `verify_phase02r.sh`;
4. `verify_phase02r_postgres.sh`;
5. `collect_phase02r_evidence.sh`;
6. implementation report;
7. evidence index and raw hashed evidence;
8. audit report;
9. canonical merge and post-merge CI evidence;
10. closure approvals.

---


## 44. Controlled Appendices and Maintainability

The detailed specifications are now split into controlled appendices.

| Appendix | Canonical file | Version | SHA-256 | Status |
|---|---|---:|---|---|
| A | `phase_02r_appendix_a_data_model.md` | 1.4 | `57964963d41efdeee1dcc70c763f4e445684c73ecdc930af3884024ddbb545a7` | Pending approval with main plan |
| B | `phase_02r_appendix_b_test_and_evaluation_matrix.md` | 1.4 | `6b0c825f1be3a123fc3e47c04744c3e877eb452966284898816a4361ccfa4367` | Pending approval with main plan |
| C | `phase_02r_appendix_c_evidence_inventory.md` | 1.4 | `295ba3bb8cdadaae6c6dc6925b07afa2b9e67be91bb1028b736105d15231f39d` | Pending approval with main plan |
| D | `phase_02r_appendix_d_audit_sampling.md` | 1.4 | `37b2fdf06a932697357e0a236178f190d0f3cef360a091bead1eb01ed77b860c` | Pending approval with main plan |
| E | `phase_02r_appendix_e_api_review_and_provenance.md` | 1.4 | `4556fe48a959a99acda1321b1a9a3a8d0d5b255a2b240e4f0b0d591bab910e36` | Pending approval with main plan |

Rules:

- this execution plan remains the programme authority;
- all five appendices must be reviewed and approved with the main plan;
- the canonical repository copy must reproduce the recorded hashes or update the plan through a controlled amendment;
- an appendix may clarify detail but may not weaken the main plan;
- any change to scope, architecture, rights, activation, thresholds, evidence, audit, tests, APIs, or reviewer controls is material;
- appendix hashes must be re-recorded after any approved amendment;
- implementation scripts must verify the main-plan and appendix hashes at preflight.


---

## 45. Final Planning Position

This plan authorises no code by itself.

The immediate next action is a start-gate review that names owners, confirms the live canonical repository and migration head, freezes the first-closure source inventory, accepts the rights/curriculum/language/audit scope, and commits the approved plan.

Execution remains two-step:

1. **Gate 2R.0 — read-only discovery and approval:** baseline, source-inventory proposal, rights risks, ADRs, non-production samples, storage/review-interface decisions, thresholds, estimate refresh, and the immutable approved-plan/start commit while the flag remains `false` until the final commit transition.
2. **Gates 2R.1–2R.8 — controlled implementation:** migrations, production schema/services, governed-source ingestion, corpus activation, and learner-serving changes only after the approved Gate 2R.0 exit commit sets the start flag to `true`.

Only then should Phase 2R implementation begin.

Until the full plan/report/evidence/audit/merge/CI/approval chain is complete, EduBoost must not claim that its model “knows CAPS” or that Phase 2R is complete.
