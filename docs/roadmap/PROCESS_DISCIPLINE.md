# Process Discipline — Phase Execution Standards

**Version:** 1.0  
**Date:** 2026-06-10  
**Status:** Active  
**Applies to:** All RoadMap phases (0–16)

## Purpose

This document defines the mandatory process discipline for every RoadMap phase. No phase may be started, executed, or closed without satisfying the gates defined below. These rules are non-negotiable and apply to both human and automated/agent execution.

---

## Phase Lifecycle

Every phase follows a strict five-stage lifecycle:

```
    ┌──────────┐
    │   PLAN   │  ← Gate: Execution plan committed before any code is touched
    └────┬─────┘
         ▼
    ┌──────────┐
    │  EXECUTE │  ← Work happens on a named branch
    └────┬─────┘
         ▼
    ┌──────────┐
    │  REPORT  │  ← Gate: Implementation report committed before merge
    └────┬─────┘
         ▼
    ┌──────────┐
    │  AUDIT   │  ← Independent verification (may be self-audit for non-P0 phases)
    └────┬─────┘
         ▼
    ┌──────────┐
    │  CLOSE   │  ← All gates green, branch merged, evidence committed
    └──────────┘
```

---

## Stage 1 — PLAN

### Mandatory Deliverable: Execution Plan

**Location:** `docs/roadmap/execution/phase_N_execution_plan.md`  
**Must exist BEFORE any implementation work begins.**

The execution plan must contain:

1. **Phase identification** — number, name, priority, source reference (roadmap.md line)
2. **Pre-execution baseline** — captured metrics/outputs showing the "before" state
3. **Problem statements** — each sub-phase listed with the specific gap being addressed
4. **Acceptance criteria** — concrete, verifiable, with pass/fail conditions
5. **Implementation tasks** — ordered checklist with `[ ]` markers
6. **Evidence output** — exact file paths where before/after evidence will be stored
7. **Success criteria** — when is this phase considered done (not just "code merged")
8. **Next phase** — what phase follows and any dependencies

### Execution Plan Template

```markdown
# Phase N Execution Plan — [Phase Name]

**Date**: YYYY-MM-DD
**Status**: IN PROGRESS
**Branch**: `phase-N/branch-name`
**Scope**: [One-line summary]

---

## Pre-Execution Baseline

Capture the current state BEFORE any changes:

```
# Example: before-state commands
<command to capture before state>
```

**Current known baseline:**
- Item 1: current value/state
- Item 2: current value/state

---

## Phase N.1 — [Sub-phase Name]

### Problem Statement

[What specific gap is being fixed? Include error output if applicable.]

### Acceptance Criteria

- [ ] Concrete, verifiable criterion 1
- [ ] Concrete, verifiable criterion 2

### Implementation Tasks

- [ ] Task 1
- [ ] Task 2
- [ ] Task 3

---

[Repeat for each sub-phase: N.2, N.3, …]

---

## Evidence Output

After completion, the following evidence files must exist:

- [ ] `docs/release/phase_N_evidence.md` — before/after outputs
- [ ] CI run URL (once available)
- [ ] Any additional artifacts

---

## Success Criteria

**Phase N is complete when:**
- [ ] All sub-phases have acceptance criteria met
- [ ] Evidence files committed
- [ ] CI gates pass (where applicable)
- [ ] Tracking documents updated

---

## Next Phase

[Phase N+1 name and brief scope]
```

---

## Stage 2 — EXECUTE

### Rules

1. **Work on a named branch** matching the pattern `phase-N/descriptive-name`.
2. **Commit incrementally** with messages that reference the sub-phase (e.g., `Phase 3.1: reconcile frontend dependencies`).
3. **Keep the execution plan updated** — check off tasks as they are completed.
4. **Do not mark the phase complete** until all acceptance criteria are verified.
5. **If a blocker is discovered**, update the execution plan with the blocker and proposed resolution before continuing.

---

## Stage 3 — REPORT

### Mandatory Deliverable: Implementation Report

**Location:** `docs/roadmap/execution/phase_N_implementation_report.md`  
**Must be committed BEFORE the phase branch is merged.**

The implementation report must contain:

1. **Summary** — what was done, what was left undone
2. **Evidence links** — exact paths to evidence files, CI URLs, captured outputs
3. **Acceptance criteria checklist** — every criterion from the execution plan, marked pass/fail with evidence
4. **Technical debt created** — any shortcuts, workarounds, or deferred items with explicit ownership
5. **Phase 4/11 debt registration** — if debt was created, register it in the appropriate burn-down tracker
6. **Verification method** — how was each claim verified (live command, CI output, manual review)
7. **Deviations from plan** — anything that was skipped, deferred, or done differently with rationale

### Implementation Report Template

```markdown
# Phase N Implementation Report — [Phase Name]

**Date**: YYYY-MM-DD
**Branch**: `phase-N/branch-name`
**Status**: COMPLETE / COMPLETE WITH DEBT / INCOMPLETE (choose one)

---

## Summary

[2-3 sentences describing what was accomplished.]

## Before/After Comparison

| Metric | Before | After |
|--------|--------|-------|
| [Metric 1] | [value] | [value] |
| [Metric 2] | [value] | [value] |

## Sub-Phase Results

### Phase N.1 — [Sub-phase Name]

| Acceptance Criterion | Status | Evidence |
|---------------------|:------:|----------|
| Criterion 1 | ✅/❌ | [link to evidence] |
| Criterion 2 | ✅/❌ | [link to evidence] |

### Phase N.2 — [Sub-phase Name]

| Acceptance Criterion | Status | Evidence |
|---------------------|:------:|----------|
| ... | ... | ... |

## Technical Debt Created

| Item | Severity | Owner | Resolution Plan |
|------|----------|-------|-----------------|
| [Description] | Low/Med/High | [Phase N+?] | [How to fix] |

## Deviations from Plan

| Planned | Actual | Rationale |
|---------|--------|-----------|
| [What was planned] | [What was done] | [Why] |

## Verification

All claims verified by: [live command / CI output / manual review]

```
# Verification commands run:
<actual commands with output excerpts>
```

## Evidence Files

- [ ] `docs/release/phase_N_evidence.md`
- [ ] `docs/roadmap/execution/phase_N_execution_plan.md` (updated with checkmarks)
- [ ] CI run: [URL]
- [ ] Other: [list]

## Sign-off

- [ ] All acceptance criteria met
- [ ] Evidence files committed
- [ ] Tracking documents updated
- [ ] Ready for merge to master
```

---

## Stage 4 — AUDIT

### Rules

1. **Every P0 phase must be independently audited** (can be self-audit with documented verification for non-critical phases).
2. **The audit must verify every acceptance criterion claim** — not just trust the report.
3. **The audit document lives at** `docs/release/phase_N_implementation_audit.md`.
4. **Discrepancies found in audit must be fixed** before the phase is marked complete. This means:
   - Stale evidence claims must be corrected in the evidence file.
   - Failed acceptance criteria must be re-executed.
   - Tracking documents must reflect the audited state.

---

## Stage 5 — CLOSE

### Gates (all must pass before merge)

- [ ] Execution plan exists at `docs/roadmap/execution/phase_N_execution_plan.md`
- [ ] Implementation report exists at `docs/roadmap/execution/phase_N_implementation_report.md`
- [ ] Audit report exists at `docs/release/phase_N_implementation_audit.md` (for P0 phases)
- [ ] All audit discrepancies resolved
- [ ] Evidence files committed and accurate
- [ ] `roadmap.md` phase status updated to "Complete (YYYY-MM-DD)"
- [ ] `context/build-plan.md` phase status updated
- [ ] `context/progress-tracker.md` updated
- [ ] CI gates pass on the phase branch (where applicable)
- [ ] Branch merged to `master` via PR
- [ ] Remote branch deleted after merge
- [ ] `../todos/todo.md` North Star tasks updated

---

## Phase Artifact Directory Map

Every phase produces files in these locations:

```
docs/
├── roadmap/
│   ├── roadmap.md                              # Canonical roadmap (moved from root)
│   ├── PROCESS_DISCIPLINE.md                   # This file
│   └── execution/
│       ├── phase_N_execution_plan.md           # PLAN stage output
│       └── phase_N_implementation_report.md    # REPORT stage output
├── release/
│   ├── phase_N_evidence.md                     # Before/after evidence
│   └── phase_N_implementation_audit.md         # AUDIT stage output
└── [domain-specific subdirectories]            # Content, curriculum, ops, etc.
```

---

## Enforcement

### Pre-Phase Checklist (Blocking)

Before ANY work begins on a new phase, this checklist must be complete:

- [ ] Execution plan written and committed to `docs/roadmap/execution/phase_N_execution_plan.md`
- [ ] Pre-execution baseline captured in the plan
- [ ] Branch created with correct naming pattern
- [ ] Success criteria defined and measurable

### Pre-Merge Checklist (Blocking)

Before a phase branch is merged to master:

- [ ] Implementation report written and committed
- [ ] All acceptance criteria verified (not just claimed)
- [ ] Audit completed (for P0 phases)
- [ ] All evidence files accurate
- [ ] Tracking documents updated
- [ ] CI green

### Rule for Marking Items Complete

Do not mark a task `[x]` or a phase "Complete" unless its evidence artifact exists and can be linked.

**Acceptable evidence includes:**
- committed file path
- passing CI run URL
- captured CLI output in an evidence file
- signed document
- dashboard screenshot
- staging/production log

**Unacceptable:**
- "should work"
- "was tested manually"
- undocumented claims
- documentation-only confidence
- intent to verify later

---

## Summary

| Gate | When | Deliverable |
|------|------|-------------|
| PLAN | Before any code is touched | `execution/phase_N_execution_plan.md` |
| REPORT | Before merge to master | `execution/phase_N_implementation_report.md` |
| AUDIT | After report, before close | `release/phase_N_implementation_audit.md` |
| CLOSE | After all gates pass | Merge PR, update tracking docs |
