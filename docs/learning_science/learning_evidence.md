# Learning Evidence

This document is the review index for diagnostics, item-bank, practice, and
mastery evidence. It does not claim full CAPS coverage or public-beta learning
readiness; it records what is implemented and what still needs approval.

## Item Schema

- Contract: `docs/diagnostics/item_contract.md`
- Domain schema: `app/domain/item_schema.py`
- ORM model: `app/models/diagnostic_item.py`
- Model tests: `tests/unit/modules/diagnostics/test_item_bank_models.py`

## IRT Validation

- Engine: `app/modules/diagnostics/irt_engine.py`
- Parameter helpers: `app/modules/diagnostics/irt_params.py`
- Hardening tests: `tests/unit/modules/diagnostics/test_irt_engine_hardening.py`
- Property tests: `tests/unit/test_irt_properties.py`
- Focused command: `make diagnostics-assessment-check`

## Item Bank Approval Scope

- Coverage matrix: `docs/caps/grade4_maths_coverage_matrix.md`
- Production plan: `docs/caps/grade4_maths_120_item_production_plan.md`
- Validator: `scripts/validate_item_bank.py`
- Current approved scope: 120 approved Grade 4 Mathematics launch diagnostic items across `4.M.1.1`, `4.M.1.2`, and `4.M.1.3`.
- Current limitation: the Grade 4 Mathematics launch slice is green, but this must not be described as full Grade 4 Mathematics or Grades R-7 CAPS coverage.

## Diagnostic Session Lifecycle

- Runtime service: `app/modules/diagnostics/diagnostic_session_service.py`
- Recovery service: `app/modules/diagnostics/session_recovery_service.py`
- Repository: `app/repositories/diagnostic_session_repository.py`
- Tests: `tests/unit/modules/diagnostics/test_session_lifecycle.py`
- Authorization evidence:
  `docs/security/diagnostic_items_authorization_wiring.md` and
  `docs/security/diagnostic_submit_authorization_wiring.md`

## Mastery Evidence

- Mastery model: `app/modules/progress/mastery_model.py`
- Timeline service: `app/modules/progress/progress_timeline_service.py`
- Learning velocity: `app/modules/progress/learning_velocity_service.py`
- Practice generator: `app/modules/practice/practice_generator.py`
- Spaced repetition scheduler:
  `app/modules/practice/spaced_repetition_scheduler.py`
- Tests: `tests/unit/modules/progress/test_mastery_model.py` and
  `tests/unit/modules/practice/test_practice_and_calibration.py`

## Aggregate Check

Run the aggregate learning evidence check with:

```bash
make learning-evidence-check
```

Run the focused diagnostics assessment check with:

```bash
make diagnostics-assessment-check
```

## Verification Gaps

- The minimum viable Grade 4 Mathematics launch item bank is approved and seeded at the target count.
- Expansion beyond the launch slice still requires generated content, validation, and promotion.
- Bias review needs end-to-end reviewer evidence.
- Diagnostic/session behavior still needs staging-path evidence before release.
- Mastery and recommendation claims must remain limited to tested model behavior
  until connected to approved item-bank evidence.
