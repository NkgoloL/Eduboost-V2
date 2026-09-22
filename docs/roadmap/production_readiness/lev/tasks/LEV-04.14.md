# LEV-04.14 — Implementation Task Card

**Workstream:** LEV-WS04 — Calibrate mastery estimates against independent outcomes  
**Phase:** LEV-3  
**Priority:** P1  
**Status:** `not_started`  
**Implementation type:** `human_governance_or_research`  
**Estimated effort:** L/XL; elapsed time may be term- or cohort-bound  
**Human dependency:** Yes  
**Cannot be completed by code alone:** Yes

## Required outcome

Obtain independent psychometric review of the calibration evidence and limitations.

## Definition-of-done link

Mastery estimates are calibrated against independent outcomes.

## Dependencies

- `LEV-04.13`

## Existing repository files to inspect or modify

- `app/modules/diagnostics/irt_engine.py`
- `app/modules/diagnostics/calibration_service.py`
- `app/repositories/irt_repository.py`
- `app/services/diagnostic_scoring_snapshot.py`
- `docs/research/mastery_model/rr013_evaluation_protocol.md`

## Planned or new files

- `app/services/educational_validation/calibration.py`
- `scripts/educational_validation/run_calibration_analysis.py`
- `docs/research/longitudinal_validation/evidence/04.14_signed_review_decision.md`

## Implementation procedure

1. Read the LEV-WS04 workstream specification and confirm prerequisites for task 04.14.
2. Open or update the task evidence record before changing code, data, instruments or governance documents.
3. Implement the required work exactly as scoped: Obtain independent psychometric review of the calibration evidence and limitations.
4. Confirm lawful authority, consent/assent, independence and conflict-of-interest controls before participant or reviewer activity.
5. Record attendance, decisions, dissent, requested corrections and signed approval or rejection.
6. Attach or link the required evidence: Signed review decision.
7. Mark complete only after the acceptance criterion is independently verifiable.

## Verification commands

```bash
python scripts/educational_validation/verify_lev_task_register.py --repo-root . --json
```
```bash
python scripts/educational_validation/lev_task_cli.py show <TASK_ID>
```
```bash
pytest -q tests/legacy/unit/test_irt_engine.py tests/unit/test_irt_properties.py
```

## Acceptance criteria

- [ ] Signed review decision.
- [ ] All declared dependencies are closed or formally waived.
- [ ] No critical privacy, fairness, educational-safety or traceability finding remains unresolved.
- [ ] The LEV verifier returns valid=true after status and evidence updates.

## Required evidence

Signed review decision.

## Execution record

- **Owner:** Unassigned
- **Reviewer:** Unassigned
- **Started:** —
- **Candidate complete:** —
- **Closed:** —
- **Commit(s):** —
- **PR(s):** —
- **Study/data manifest:** —
- **Decision:** —
- **Blockers:** —
- **Notes:** —
