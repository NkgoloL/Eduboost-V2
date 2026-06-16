# Phase 1 Execution Plan - Release-Blocking Correctness Fixes

**Date:** 2026-06-09  
**Traceability update:** 2026-06-13  
**Status:** Retrospective plan artifact  
**Branch:** `phase-1/release-blocking-correctness`

## Pre-Execution Baseline

Phase 1 covered release-blocking correctness gates:

- Python source and scripts must compile.
- Ruff release-blocking rules must pass: `E9,F63,F7,F82,F821`.
- Remaining non-blocking style debt must be quantified instead of treated as release blocking.
- CI must expose equivalent checks.

This execution plan was reconstructed after the implementation to complete the phase artifact set required by `docs/roadmap/PROCESS_DISCIPLINE.md`. It is not proof that the plan existed before implementation.

## Phase 1.1 - Python Compile Gate

### Problem Statement

Syntax errors and invalid f-strings must be caught before release.

### Acceptance Criteria

- [x] `python -m compileall -q app scripts` passes.
- [x] CI includes a backend compile gate.

### Evidence Output

- `docs/release/phase_1_evidence.md`
- `docs/release/phase_1_implementation_audit.md`

## Phase 1.2 - Undefined Name Gate

### Problem Statement

Undefined names and syntax-class Ruff failures must be treated as release blockers.

### Acceptance Criteria

- [x] `ruff check app tests scripts --select E9,F63,F7,F82,F821` passes.
- [x] Remaining Ruff debt is tracked separately from release blockers.
- [x] CI exposes the same release-blocking Ruff rule set.

### Evidence Output

- `docs/release/phase_1_evidence.md`
- `docs/backlog/ruff_debt.md`
- `docs/release/phase_1_implementation_audit.md`

## Success Criteria

- [x] Release-blocking correctness checks pass locally.
- [x] CI configuration contains equivalent checks.
- [x] Non-blocking Ruff debt is not falsely treated as complete.
- [x] Missing phase artifacts are backfilled with this retrospective plan and the matching report/audit.

## Next Phase

Phase 2: Practice session durability and/or content pipeline work, with scope discrepancy recorded in the Phase 2 audit.
