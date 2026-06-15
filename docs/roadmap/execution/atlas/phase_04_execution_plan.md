# Phase 4 Execution Plan — IRT Quality and Self-Healing Controls

**Document version:** 1.0  
**Status:** Draft — approval required before execution  
**Machine approval marker:** `PHASE_04_START_APPROVED=true`  
**Branch:** `feature/atlas-phase-04-irt-quality-and-self-healing`  
**Base branch:** `master`  
**Base commit:** TBD at start gate  
**Evidence path:** `docs/release-evidence/phase-04/`

> No Phase 4 production-code change may begin until this plan is reviewed, the approval marker is changed to `true`, and the plan is committed. Phase 4 cannot close without an implementation report, evidence pack, independent audit, canonical merge, and post-merge verification.

## Objective

Monitor diagnostic-item performance and safely retain, monitor, review, quarantine, retire, or request a governed rewrite without automatic learner-facing content mutation.

## Approved policy to confirm before execution

- Model: conservative two-parameter logistic fit using a session-rest-score ability proxy.
- Minimum data: 100 usable responses, 50 unique learners, 20 sessions, 95% answered ratio.
- Healthy discrimination: `a >= 0.70` and fit RMSE `<= 0.35`.
- Monitor: `0.50 <= a < 0.70`.
- Review required: weak fit or `0.35 < a < 0.50`.
- Quarantine: `a <= 0.35`, RMSE `>= 0.45`, or extreme accuracy outside 5–95%.
- Retire/rewrite: third consecutive catastrophic strike.
- Correct-answer position warning: maximum position share above 45% over at least 20 items.
- No automatic option shuffle, wording change, answer-key change, or publication.
- Rewrites enter Phase 3 `pending_review` with publication eligibility false.

Thresholds are provisional until approved by a qualified statistical or assessment reviewer.

## Scope

### In scope

- Versioned calibration and intervention policy.
- Data-quality gates and deterministic 2PL fitting.
- Calibration runs, item events, idempotency, retries, state and metrics.
- Learner-serving exclusion for review-required, quarantined, retired, and rewrite-review states.
- Nightly durable ARQ execution and protected admin dry-run/manual-override API.
- Append-only calibration history.
- Governed rewrite requests into Phase 3 review.
- Unit, migration, PostgreSQL, route, selection, regression, recovery, and evidence tests.

### Out of scope

- National norming or claims of population-valid IRT.
- Automatic content rewriting or publication.
- Phase 5 tutor changes.
- Broad redesign of the diagnostics frontend.

## Preconditions

- [x] Phase 1 is verified/revalidated on the current master commit.
- [x] Phase 2 is Verified Complete.
- [x] Phase 3 is Verified Complete and the single-review route is absent.
- [x] Clean master checkout and single Alembic head at `20260614_1500_p3_consensus`.
- [x] This plan is approved and committed.
- [x] Statistical/assessment reviewer is assigned.
- [x] Content owner accepts the rewrite-to-Phase-3 policy.
- [x] Disposable pgvector/PostgreSQL environment is available.

## Work items

| ID | Work | Acceptance criterion |
|---|---|---|
| P4-001 | Add policy/domain contracts | Threshold order and data gates are validated and versioned |
| P4-002 | Add migration/models | Item state, runs, append-only events, indexes and constraints migrate from Phase 3 |
| P4-003 | Implement deterministic calibrator | Same observations produce the same bounded result |
| P4-004 | Implement state machine | Healthy, monitor, review, quarantine and retirement transitions are explicit |
| P4-005 | Enforce learner-serving exclusion | Ineligible states cannot be selected |
| P4-006 | Create governed rewrites | Rewrite artifacts are pending Phase 3 review and cannot auto-publish |
| P4-007 | Add durable job and admin API | Nightly job, dry run, status and attributable manual override work |
| P4-008 | Add metrics/runbook | Runs, interventions, bias and rewrites are observable |
| P4-009 | Add fast/PostgreSQL tests | Zero failures and zero unexpected database skips |
| P4-010 | Freeze evidence and audit | Complete four-artifact set against merge commit |

## Mandatory tests

- Data below minimum sample causes no state mutation.
- Healthy items remain learner eligible and content is unchanged.
- Weak items require review.
- Catastrophic items quarantine immediately and retire after the approved strike threshold.
- Quarantined/retired/review-required items cannot be selected.
- Answer-position bias is measured without shuffling options.
- Rewrites are Phase 3 pending-review artifacts.
- Duplicate run keys are idempotent.
- Calibration events reject update/delete in PostgreSQL.
- Manual override is authenticated, reasoned, and suppresses automation without making a quarantined item eligible.
- Phase 1–3 verification remains green.
- Upgrade from the Phase 3 head and downgrade/upgrade recovery pass.

## Stop conditions

Stop and keep the phase open if any of these occur:

- learner-facing content is automatically changed;
- a rewrite bypasses Phase 3 review;
- quarantine does not remove learner eligibility;
- model fitting uses fewer than the approved minimum observations;
- concurrent or repeated runs create contradictory events;
- Phase 1–3 regress;
- the independent reviewer rejects the statistical policy.

## Evidence set

- `docs/roadmap/execution/phase_04_implementation_report.md`
- `docs/release-evidence/phase-04/phase_04_evidence_index.md`
- `docs/release-evidence/phase-04/phase_04_audit_report.md`
- raw fast/PostgreSQL/migration/schema/environment logs and SHA-256 manifest.

## Start approval

| Role | Name | Decision | Date/reference |
|---|---|---|---|
| Phase owner | | Pending | |
| Engineering approver | | Pending | |
| Statistical/assessment reviewer | | Pending | |
| Content owner | | Pending | |
| Evidence custodian | | Pending | |
| Planned auditor | | Pending | |

## Definition of Done

Phase 4 is complete only after all policy, state, serving, rewrite, scheduler, recovery and regression gates pass; the evidence is frozen against the canonical merge commit; a qualified independent audit passes with no open Critical/High finding; and the phase status register is updated last.
