# Production Diagnostics and Assessment Readiness Contract

## Purpose

This contract records repository-side implementation evidence for production-readiness backlog item 07: diagnostics, assessment, item bank, and mastery model.

## Required Runtime Domains

- diagnostic item schema with item ID, subject, grade, topic, skill, difficulty, discrimination, correct answer, distractors, explanation, and CAPS reference
- IRT parameter validation for theta bounds, difficulty bounds, discrimination bounds, probability output, overflow safety, and invalid input handling
- probability of correctness, Fisher information, ability update, EAP estimate, edge response, empty response, all-correct, and all-incorrect test evidence
- grade-equivalent mapping evidence
- item selection by Fisher information evidence
- gap identification evidence
- diagnostic session start, question serving, answer submission, ability update, result retrieval, consent gate, and object authorization evidence
- pause/resume, session recovery, maximum item cap, minimum evidence threshold, and confidence interval evidence

## Required Repository Evidence

- `app/domain/item_schema.py`
- `app/modules/diagnostics/production_readiness_contracts.py`
- `app/modules/diagnostics/irt_engine.py`
- `app/modules/diagnostics/diagnostic_session_service.py`
- `app/modules/diagnostics/session_recovery_service.py`
- `app/modules/diagnostics/termination_service.py`
- `app/modules/diagnostics/item_bank_service.py`
- `app/modules/diagnostics/item_selection_service.py`
- `tests/unit/modules/diagnostics/test_irt_engine_hardening.py`
- `tests/unit/modules/diagnostics/test_session_lifecycle.py`

## Non-Goals

This contract does not replace educator psychometric review, live calibration data, live production analytics, or post-launch item-performance monitoring.

## Command

```bash
make diagnostics-assessment-production-readiness-check
```
