# LEV-04.08 — Implementation Task Card

**Workstream:** LEV-WS04 — Calibrate mastery estimates against independent outcomes  
**Phase:** LEV-2  
**Priority:** P1  
**Status:** `not_started`  
**Implementation type:** `analysis_and_validation`  
**Estimated effort:** M/L after data readiness  
**Human dependency:** No  
**Cannot be completed by code alone:** Yes

## Required outcome

Evaluate discrimination and ranking metrics without treating them as substitutes for calibration.

## Definition-of-done link

Mastery estimates are calibrated against independent outcomes.

## Dependencies

- `LEV-04.07`

## Existing repository files to inspect or modify

- `app/modules/diagnostics/irt_engine.py`
- `app/modules/diagnostics/calibration_service.py`
- `app/repositories/irt_repository.py`
- `app/services/diagnostic_scoring_snapshot.py`
- `docs/research/mastery_model/rr013_evaluation_protocol.md`

## Planned or new files

- `app/services/educational_validation/calibration.py`
- `scripts/educational_validation/run_calibration_analysis.py`
- `docs/research/longitudinal_validation/evidence/04.08_auc_pr_results_reported_alongside_calibration.md`

## Implementation procedure

1. Read the LEV-WS04 workstream specification and confirm prerequisites for task 04.08.
2. Open or update the task evidence record before changing code, data, instruments or governance documents.
3. Implement the required work exactly as scoped: Evaluate discrimination and ranking metrics without treating them as substitutes for calibration.
4. Freeze the analysis input manifest before examining outcome results.
5. Execute the pre-specified analysis with reproducible code and retain diagnostics, uncertainty and sensitivity outputs.
6. Attach or link the required evidence: AUC/PR results reported alongside calibration.
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

- [ ] AUC/PR results reported alongside calibration.
- [ ] All declared dependencies are closed or formally waived.
- [ ] No critical privacy, fairness, educational-safety or traceability finding remains unresolved.
- [ ] The LEV verifier returns valid=true after status and evidence updates.

## Required evidence

AUC/PR results reported alongside calibration.

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
