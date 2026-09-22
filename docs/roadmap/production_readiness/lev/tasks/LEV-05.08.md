# LEV-05.08 — Implementation Task Card

**Workstream:** LEV-WS05 — Quantify false-mastery and false-non-mastery risk  
**Phase:** LEV-2  
**Priority:** P1  
**Status:** `not_started`  
**Implementation type:** `governance_and_documentation`  
**Estimated effort:** S/M  
**Human dependency:** No  
**Cannot be completed by code alone:** No

## Required outcome

Investigate language load, poor item fit, missing opportunity to learn and interface problems as causes of false non-mastery.

## Definition-of-done link

False-mastery and false-non-mastery rates are understood.

## Dependencies

- `LEV-05.07`

## Existing repository files to inspect or modify

- `app/modules/progress/mastery_model.py`
- `app/modules/diagnostics/irt_engine.py`
- `app/services/runtime_kg/schemas.py`
- `docs/diagnostics/mastery_model_assessment_contract.md`

## Planned or new files

- `app/services/educational_validation/classification.py`
- `scripts/educational_validation/run_classification_analysis.py`
- `docs/research/longitudinal_validation/evidence/05.08_measurement_confound_report.md`

## Implementation procedure

1. Read the LEV-WS05 workstream specification and confirm prerequisites for task 05.08.
2. Open or update the task evidence record before changing code, data, instruments or governance documents.
3. Implement the required work exactly as scoped: Investigate language load, poor item fit, missing opportunity to learn and interface problems as causes of false non-mastery.
4. Circulate the draft to accountable and consulted roles.
5. Resolve comments and obtain the required versioned approval.
6. Attach or link the required evidence: Measurement-confound report.
7. Mark complete only after the acceptance criterion is independently verifiable.

## Verification commands

```bash
python scripts/educational_validation/verify_lev_task_register.py --repo-root . --json
```
```bash
python scripts/educational_validation/lev_task_cli.py show <TASK_ID>
```
```bash
pytest -q tests/unit/modules/progress/test_mastery_model.py
```

## Acceptance criteria

- [ ] Measurement-confound report.
- [ ] All declared dependencies are closed or formally waived.
- [ ] No critical privacy, fairness, educational-safety or traceability finding remains unresolved.
- [ ] The LEV verifier returns valid=true after status and evidence updates.

## Required evidence

Measurement-confound report.

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
