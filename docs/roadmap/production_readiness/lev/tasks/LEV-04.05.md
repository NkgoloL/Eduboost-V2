# LEV-04.05 — Implementation Task Card

**Workstream:** LEV-WS04 — Calibrate mastery estimates against independent outcomes  
**Phase:** LEV-2  
**Priority:** P1  
**Status:** `not_started`  
**Implementation type:** `governance_and_documentation`  
**Estimated effort:** S/M  
**Human dependency:** No  
**Cannot be completed by code alone:** No

## Required outcome

Assess data completeness, representativeness, missingness and outcome quality before modelling.

## Definition-of-done link

Mastery estimates are calibrated against independent outcomes.

## Dependencies

- `LEV-04.04`

## Existing repository files to inspect or modify

- `app/modules/diagnostics/irt_engine.py`
- `app/modules/diagnostics/calibration_service.py`
- `app/repositories/irt_repository.py`
- `app/services/diagnostic_scoring_snapshot.py`
- `docs/research/mastery_model/rr013_evaluation_protocol.md`

## Planned or new files

- `app/services/educational_validation/calibration.py`
- `scripts/educational_validation/run_calibration_analysis.py`
- `docs/research/longitudinal_validation/evidence/04.05_data_quality_gate_passed.md`

## Implementation procedure

1. Read the LEV-WS04 workstream specification and confirm prerequisites for task 04.05.
2. Open or update the task evidence record before changing code, data, instruments or governance documents.
3. Implement the required work exactly as scoped: Assess data completeness, representativeness, missingness and outcome quality before modelling.
4. Circulate the draft to accountable and consulted roles.
5. Resolve comments and obtain the required versioned approval.
6. Attach or link the required evidence: Data-quality gate passed.
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

- [ ] Data-quality gate passed.
- [ ] All declared dependencies are closed or formally waived.
- [ ] No critical privacy, fairness, educational-safety or traceability finding remains unresolved.
- [ ] The LEV verifier returns valid=true after status and evidence updates.

## Required evidence

Data-quality gate passed.

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
