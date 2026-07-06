---
title: Phase 2R Gate 2R.0 Initial Start-Gate Report
status: historical-record
owner: roadmap-governance
reviewers: [roadmap-governance, release-management, documentation-governance]
audience: roadmap-reviewer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-06
review_interval_days: 30
evidence_command: make docs-housekeeping-stage7-check
code_anchors: [docs/roadmap, docs/documentation/stage_7_release_archive_backlog_codemaps_governance.md]
---

# Phase 2R Gate 2R.0 Initial Start-Gate Report

> Historical initial discovery report. This report records the first failed Gate
> 2R.0 capture and must not be treated as closure evidence. Current remediation
> and closure evidence belongs in
> `docs/roadmap/execution/atlas/phase_02r_gate_2r0_closure_report.md` and
> `docs/release-evidence/atlas/phase-02r/gate-2r0/`.

**Generated:** 2026-06-16
**Gate:** 2R.0 read-only discovery and approval review
**Decision:** Do not authorise Gate 2R.1 yet
**Owner:** Nkgolo Lebelo
**Reviewer / auditor assignment:** Nkgolo Lebelo, with a disclosed independence conflict because this is a single-developer project

## 1. Canonical repository state

| Item | Actual value |
|---|---|
| Canonical remote | `origin https://github.com/NkgoloL/Eduboost-V2.git` |
| Canonical branch | `feature/atlas-phase-02r-authoritative-caps-corpus` |
| baseline_capture_sha | `81735c51a7cf71c8b9fa110d1d152fb8d7103278` |
| initial_gate_report_commit_sha | `8d972b5f` |
| eventual_gate_approval_commit_sha | Not issued; Gate 2R.1 remains blocked |
| Base branch merge-base with `origin/master` | `4b3805b700869aaeacce4141bb565e1963777163` |
| Worktree baseline | Dirty; existing reconciliation/source/evidence changes are present and must be reconciled before an immutable approval claim |
| Actual Alembic head | `20260615_2100_p17_reconcile` |
| Migration graph | Passed; 42 revisions, single head `20260615_2100_p17_reconcile` |
| Schema integrity | Passed |

## 2. Clean-checkout and toolchain baseline

Toolchain observed in the active WSL checkout:

| Tool | Version / result |
|---|---|
| Python | `3.12.3` |
| Git | `2.43.0` |
| Docker | `29.5.3` |
| Docker Compose | `v5.1.4` |
| Node | `v22.22.3` |
| pnpm | `9.14.4` |
| pytest | `8.2.1` |
| Ruff | `0.4.8` |

The active checkout is not clean. Phase 2R may use the Phase 0 compensating route only after a clean checkout or clean worktree evidence is produced and committed.

## 3. Phase 1-7 reconciliation state

| Area | Actual state |
|---|---|
| Phase 0 | Planning only; not `Verified Complete` |
| Phase 1 | Revalidation required |
| Phase 2 | Closure review; two-case retrieval smoke dataset is correctly rejected for closure |
| Phase 3 | Governance revalidation required |
| Phase 4 | Evidence repair / closure review |
| Phase 5 | Audit review |
| Phase 6 | Verification pending |
| Phase 7 | Verification pending; isolated-port evidence exists but final audit/merge closure is still pending |
| Combined Phase 1-7 gate | Not proven complete |

`scripts/verify_phases_01_07_reconciliation.sh` compiled reconciliation modules, passed focused tests, Ruff, migration graph, schema integrity, control-set validation, static checks, and the Phase 2 smoke claim guard at the original Gate 2R.0 capture. A remediation patch now makes the Phase 2 smoke claim guard explicit and allows later advertised steps to run. Full Phase 1-7 reconciliation still must be regenerated from a clean remediation candidate before it can be claimed as passing.

## 4. `02R` programme-tool compatibility findings

| Surface | Finding |
|---|---|
| Plan paths | `phase_02r_*` paths exist under `docs/roadmap/execution/atlas` |
| Evidence paths | Planned `docs/release-evidence/atlas/phase-02r/` path is specified, but the collector does not exist yet |
| Validator | `scripts/validate_phase_identifier_compatibility.py` is referenced in the plan but does not exist |
| Preflight / apply / verify / evidence scripts | `preflight_phase02r.sh`, `apply_phase02r_patch.sh`, `verify_phase02r.sh`, `verify_phase02r_postgres.sh`, and `collect_phase02r_evidence.sh` are planned deliverables and do not exist yet |
| Status / sorting / CI | Not proven by an executable validator |

No planned validator is recorded as passing. The validator and script suite remain Gate 2R.0 or Gate 2R.1 deliverables before implementation can claim automation compatibility.

## 5. Phase 0 / reproducibility decision

Decision: use the compensating route only after it is evidenced.

Phase 0 is not verified complete. Gate 2R.0 may absorb equivalent controls, but the active worktree is dirty and no clean-checkout evidence pack exists yet. Start approval remains blocked until a clean-checkout/toolchain baseline is produced or Phase 0 is separately completed.

## 6. Bounded source-inventory proposal

First closure remains bounded to Grade 4 Mathematics, all five strands, Terms 1-4, and the languages `en`, `af`, and `nso`.

Minimum source-completeness categories:

| Category | Required treatment |
|---|---|
| Tier 1 official CAPS source | Mandatory where official source exists |
| Official translation | Separate language authority and rights decision |
| Reviewed translation | Allowed only when translation rights and review pass |
| Derived teaching aid | Not authority unless explicitly classified and reviewed |
| Synthetic or generated material | Never authority source for production grounding |
| Missing / ambiguous source | Blocks active corpus membership |

Observed source-inventory sample:

| Check | Result |
|---|---|
| `scripts/curriculum/source_inventory.py --json` | Validation failed |
| Missing rows | 1 |
| Gap reason | `missing_source_document` |
| Affected scope | `grade4_mathematics_en` |
| Generation-ready scopes | none |

## 7. Rights-risk inventory

| Risk | Gate 2R.0 disposition |
|---|---|
| Storage rights for original source files | Not approved; object files are missing locally |
| Extraction/text storage rights | Not approved; must be explicit per source/version/use |
| Embedding and prompt-use rights | Not approved; fail closed until structured decision exists |
| Translation rights | Not approved; translation and translation-publication permissions must be separate |
| Model-training rights | Explicitly prohibited by default |
| Redistribution/excerpt exposure | Not approved; must be access-controlled and rights-aware |
| Conditional-use rights | Must be machine-evaluable; prose-only conditions are insufficient |

## 8. Named owners, reviewers, and auditor

| Role | Name | Gate 2R.0 decision |
|---|---|---|
| Phase owner | Nkgolo Lebelo | Assigned |
| Engineering approver | Nkgolo Lebelo | Assigned |
| Curriculum owner/reviewer | Nkgolo Lebelo | Assigned with self-review conflict disclosed |
| Rights reviewer | Nkgolo Lebelo | Assigned with legal-competence limitation disclosed |
| Language-quality owner | Nkgolo Lebelo | Assigned with human-language review limitation disclosed |
| Security/privacy/safeguarding reviewer | Nkgolo Lebelo | Assigned |
| Evidence custodian | Nkgolo Lebelo | Assigned |
| Independent technical auditor | Nkgolo Lebelo | Assigned as self-auditor; independence conflict disclosed |
| Release manager | Nkgolo Lebelo | Assigned |
| Final phase approver | Nkgolo Lebelo | Assigned |

Compensating controls required before closure: command reproduction from clean checkout, raw evidence hashes, post-merge CI, and explicit conflict disclosure in every audit report.

## 9. ADR-02R decisions

| ADR | Decision |
|---|---|
| ADR-02R-001 | Immutable PostgreSQL authority records are the source of truth; retrieval tables and vector indexes are rebuildable projections |
| ADR-02R-002 | Original files require immutable object storage; local filesystem adapter is development-only |
| ADR-02R-003 | Corpus activation is a PostgreSQL binding update plus transactional outbox, with versioned cache keys and append-only activation history |
| ADR-02R-004 | Logical source, acquired object, extraction run, page, section, and chunk versions receive separate stable identities |
| ADR-02R-005 | Rights decisions are explicit per version and per use, including translation and publication; all unresolved uses fail closed |
| ADR-02R-006 | Official source, reviewed translation, machine draft, and generated explanation are separate authority classes |
| ADR-02R-007 | Production curriculum operations resolve one active corpus version and persist provenance |
| ADR-02R-008 | Answer verification is deterministic-first and independent from educator quorum or generation approval |
| ADR-02R-009 | Existing learner-serving artifacts require explicit disposition before being served under Phase 2R |
| ADR-02R-010 | Source changes create impact/staleness records and do not overwrite history |
| ADR-02R-011 | Extracted text uses hybrid storage: PostgreSQL metadata, hashes, provenance, review state, and access references; object storage holds large extraction artifacts |
| ADR-02R-012 | Reviewer workflow will use an authenticated admin web interface plus approved CLI/export fallback; bulk approval without per-item trace is prohibited |
| ADR-02R-013 | Activation key dimensions are tenant/global scope, curriculum, grade, subject, delivery language, language policy, active corpus version, and binding epoch |

## 10. Object-storage, extracted-text, activation-key, and reviewer-interface decisions

| Decision | Outcome |
|---|---|
| Object storage | Required for staging/production; immutable/versioned keys mandatory; local adapter allowed only for development |
| Extracted text | Hybrid storage approved as ADR-02R-011 |
| Activation key | Full key approved as ADR-02R-013 |
| Reviewer interface | Admin web interface plus CLI/export fallback approved as ADR-02R-012 |

## 11. Non-production extraction sample results

| Check | Result |
|---|---|
| `scripts/curriculum/extract_caps_source_text.py --json` | Did not extract source documents |
| Documents extracted | 0 |
| Validation | Failed |
| Primary validation error | `scope grade4_mathematics_en does not reference a source document` |
| Missing files | Manifest references multiple missing local PDFs under `data/caps/source_documents/raw/` |

This sample is not authority-source proof. It is a start-gate discovery result showing that source acquisition and local object availability are blockers.

## 12. Refreshed estimate

The plan estimate remains 72-108 engineering person-days, but Gate 2R.0 findings require reserve before Gate 2R.1:

| Work item | Estimate impact |
|---|---|
| Build missing Phase 02R validators and collectors | +2-4 engineering days |
| Produce clean-checkout/toolchain evidence | +1 day |
| Complete source acquisition / object availability | +3-6 engineering days, plus rights review time |
| Repair combined Phase 1-7 verifier terminal flow | +1-2 engineering days |
| Rights and language review compensating controls | Human review schedule risk remains high |

Recommended planning range after Gate 2R.0: 79-121 engineering person-days, plus curriculum, rights, language, security, legal, accessibility, operational, and audit time.

## 13. Start-gate recommendation

Recommendation: do not set `PHASE_02R_START_APPROVED=true` yet.

Gate 2R.0 produced the required discovery outputs, but the start gate is not closed because:

- Phase 0 is not verified complete and equivalent clean-checkout evidence is not yet proven;
- the active worktree is dirty;
- Phase 1-7 reconciliation is not fully proven by the existing script;
- the `02R` compatibility validator and Phase 02R preflight/verify/evidence scripts do not exist;
- the source inventory and extraction sample fail;
- object-storage availability is not proven;
- rights and language review remain self-reviewed with disclosed conflicts.

The immutable approval transition must wait until these blockers are resolved and committed.

## 14. Source-state clarification

Future Gate 2R.0 closure evidence must be generated from a clean checkout of the remediation candidate. It must not be retrospectively attributed to `81735c51a7cf71c8b9fa110d1d152fb8d7103278`.

Definitions:

| Field | Meaning |
|---|---|
| `baseline_capture_sha` | Source state used for the first failed Gate 2R.0 discovery capture |
| `initial_gate_report_commit_sha` | Commit that recorded the failed initial Gate 2R.0 report |
| `remediation_code_commit_sha` | Future commit that records start-gate remediation code and docs |
| `evidence_run_source_sha` | Future clean source state used to generate closure evidence |
| `evidence_commit_sha` | Future commit that freezes the generated closure evidence |
| `eventual_gate_approval_commit_sha` | Future dedicated approval commit that may set `PHASE_02R_START_APPROVED=true` only after all start-gate blockers close |
