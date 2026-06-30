# Phase 4 Execution Plan - Runtime and Environment Alignment

**Date:** 2026-06-10  
**Traceability update:** 2026-06-13  
**Gate repair:** 2026-06-14
**Status:** Complete
**Branch:** `phase-4/python-version-alignment`

## Pre-Execution Baseline

The repository previously had mixed Python runtime references:

- Dockerfiles used older Python base images.
- CI and local configuration were expected to standardize on Python 3.12.3.
- Documentation referenced older generic Python 3.11+ guidance.
- Frontend Phase 3 evidence identified runtime/tooling drift as follow-up debt.

This plan was reconstructed on 2026-06-13 because no Phase 4 execution plan existed under `docs/roadmap/execution`.

## Phase 4.1 - Choose Authoritative Python Runtime

### Problem Statement

Local, Docker, and CI Python versions must not drift for production-like verification.

### Acceptance Criteria

- [x] `.python-version` records the chosen runtime.
- [x] ADR records the runtime decision.
- [x] Dockerfiles use the chosen runtime family.

## Phase 4.2 - Align CI and Documentation

### Problem Statement

CI and documentation must not point developers toward incompatible Python versions.

### Acceptance Criteria

- [x] CI primarily uses Python 3.12.3.
- [x] No workflow labels or selectors imply Python 3.11 or loose versions without rationale.
- [x] Documentation records the decision.

## Phase 4.3 - Verification

### Problem Statement

The repository needs a repeatable way to prove runtime alignment.

### Acceptance Criteria

- [x] `docs/adr/ADR-026-python-version-alignment.md` exists.
- [x] Dockerfiles use `python:3.12.3-slim`.
- [x] All CI workflow references are strictly aligned to `3.12.3`.

## Evidence Output

- `docs/adr/ADR-026-python-version-alignment.md`
- `docs/release/phase_4_evidence.md`
- `docs/release/phase_4_implementation_audit.md`

## Success Criteria

Phase 4 is complete when local, Docker, CI, and documentation Python version references are aligned or documented with intentional exceptions.

## Next Phase

Phase 5: migrations and schema management.
