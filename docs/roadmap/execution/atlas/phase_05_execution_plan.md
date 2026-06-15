# Phase 5 Execution Plan — Safe Learner AI Tutor

**Document version:** 1.0  
**Date:** 2026-06-15  
**Status:** Draft — approval required before execution  
**Machine approval marker:** `PHASE_05_START_APPROVED=true`  
**Branch:** `feature/atlas-phase-05-safe-learner-ai-tutor`  
**Base branch:** `master`  
**Base commit:** TBD at start gate  
**Python:** use the repository `.venv/bin/python`; minimum supported version is Python 3.11  
**Evidence path:** `docs/release-evidence/atlas/phase-05/`

> No Phase 5 production-code change may begin until this plan is reviewed, the approval marker is changed to `true`, and the plan is committed. Phase 5 cannot close without an implementation report, evidence pack, independent audit, canonical merge, and post-merge verification.

## Objective

Deliver a lesson-scoped, context-aware, privacy-preserving and age-appropriate learner tutor that fails safely, respects learner ownership and consent, supports cancellation and connectivity loss, enforces rate and token budgets, and escalates unsafe or low-quality interactions for educator review.

## Approved policy to confirm before execution

- The tutor is not a general-purpose chatbot.
- Every session is bound to one authenticated learner and one learner-owned lesson.
- Provider context is limited to a bounded lesson excerpt, grade, subject, topic, language and non-identifying knowledge-gap topics.
- Recognised PII is redacted before persistence and before a provider call; only a SHA-256 digest represents the original learner text.
- Prompt-injection and high-risk requests fail closed before a provider call.
- Provider output is fully validated before any text reaches the learner. Controlled SSE chunks may be emitted only after validation.
- Provider, network, budget and policy failures use a local non-deceptive fallback.
- High-risk or unsafe interactions create an educator/safeguarding escalation.
- The tutor never automatically changes curriculum content, learner records or Phase 3 publication status.
- Tutor conversations are not training data without a separate approved governance decision.

## Preconditions

- [ ] Phases 1–4 are recorded `Verified Complete` on the current canonical source state.
- [ ] Phase 4 plan/report/evidence/audit artifacts exist under the `atlas` hierarchy.
- [ ] Clean `master` checkout and one Alembic head at `20260615_0900_p4_irt_quality`.
- [ ] This plan is approved and committed under `docs/roadmap/execution/atlas/`.
- [ ] Safeguarding owner, content owner, evidence custodian and independent auditor are assigned.
- [ ] Disposable PostgreSQL/pgvector environment is available.
- [ ] Frontend uses the repository-supported pnpm toolchain.

## Scope

### In scope

- Tutor session, message and escalation persistence.
- Learner and lesson ownership plus active-consent enforcement.
- Lesson-context and non-identifying learner-context construction.
- Strict question/session API schemas.
- PII redaction, prompt-injection prevention and high-risk input blocking.
- Age-appropriate system policy and provider-output validation.
- Endpoint rate limits and daily/monthly token budget enforcement.
- Safe fallback for provider, connectivity, policy and budget failures.
- SSE interaction with cancellation and disconnect handling.
- Accessible learner chat component and privacy notice.
- Metrics, runbook, unit, PostgreSQL, route, frontend and regression tests.
- Full plan/report/evidence/audit set under `atlas`.

### Out of scope

- Voice input/output.
- Unbounded general chat.
- Tutor-generated curriculum publication.
- Automated safeguarding decisions beyond safe containment and escalation.
- Training on tutor conversations.
- Phase 6 production observability platform redesign.

## Work items

| ID | Work | Acceptance criterion |
|---|---|---|
| P5-001 | Approve tutor safety ADR and context policy | Roles, data boundary, refusal, fallback and escalation policy accepted |
| P5-002 | Add tutor models and migration | Sessions/messages/escalations migrate from Phase 4 and enforce constraints |
| P5-003 | Implement input/output safety | PII, injection, high-risk and unsafe output tests pass |
| P5-004 | Implement tutor orchestration | Context-bound provider call, budget guard and persistence work |
| P5-005 | Implement protected tutor API | Ownership, consent, rate limit, idempotency and cancellation pass |
| P5-006 | Implement validated SSE | No unvalidated partial output; disconnect/cancel safe |
| P5-007 | Implement learner UI | Accessible chat, stop control, privacy notice and fallback UX pass |
| P5-008 | Add escalation and metrics | Unsafe/low-quality interactions are attributable and observable |
| P5-009 | Add fast/PostgreSQL/frontend tests | Zero failures and zero unexpected skips |
| P5-010 | Freeze evidence and audit | Four-artifact set references canonical merge commit |

## Mandatory tests

- Cross-learner and unrelated-lesson access returns 403/404 without data leakage.
- Missing consent blocks session creation and messaging.
- Actor identity cannot be supplied in the payload.
- PII is redacted before storage and provider use.
- Prompt injection and high-risk content never reach the provider.
- Unsafe, empty, oversized or low-quality output fails safely.
- Provider and network failure return a non-deceptive fallback.
- Rate and budget exhaustion do not call the provider.
- Duplicate `client_message_id` is idempotent.
- Lesson changes invalidate the bound context and require a new session.
- Cancellation and client disconnect do not claim successful completion.
- Tutor messages are immutable after insert in PostgreSQL.
- Frontend input, live region, stop control and privacy notice are accessible.
- Phases 1–4 remain green.
- Upgrade from the Phase 4 head and downgrade/re-upgrade recovery pass.

## Stop conditions

Stop and keep Phase 5 open if:

- unredacted learner PII reaches logs, persistence or a provider;
- provider text reaches the learner before safety validation;
- a learner can access another learner's session or lesson context;
- an unsafe or malformed response is shown as a tutor answer;
- fallback text is deceptive about provider success;
- budget/rate controls can be bypassed;
- Phase 1–4 regress;
- the independent safeguarding/content reviewer rejects the policy.

## Required control set

- `docs/roadmap/execution/atlas/phase_05_execution_plan.md`
- `docs/roadmap/execution/atlas/phase_05_implementation_report.md`
- `docs/release-evidence/atlas/phase-05/phase_05_evidence_index.md`
- `docs/release-evidence/atlas/phase-05/phase_05_audit_report.md`
- `docs/release-evidence/atlas/phase-05/raw/`

## Start approval

| Role | Name | Decision | Date/reference |
|---|---|---|---|
| Phase owner | | Pending | |
| Engineering approver | | Pending | |
| Safeguarding/privacy reviewer | | Pending | |
| Content owner | | Pending | |
| Evidence custodian | | Pending | |
| Planned auditor | | Pending | |

## Definition of Done

Phase 5 is complete only when all ownership, consent, privacy, safety, context, fallback, rate, budget, cancellation, accessibility, browser, provider-failure and regression gates pass; PostgreSQL verification has zero unexpected skips; the implementation report and evidence pack are frozen against the canonical merge commit; an independent audit passes with no open Critical or High finding; and the status register is updated last.
