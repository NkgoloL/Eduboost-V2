# LEV-08.14 — Implementation Task Card

**Workstream:** LEV-WS08 — Validate educational plausibility of state transitions  
**Phase:** LEV-6  
**Priority:** P2  
**Status:** `not_started`  
**Implementation type:** `analysis_and_validation`  
**Estimated effort:** M/L after data readiness  
**Human dependency:** No  
**Cannot be completed by code alone:** Yes

## Required outcome

Run continuous transition-reasonableness surveillance after model, KG or content changes.

## Definition-of-done link

State transitions are educationally plausible.

## Dependencies

- `LEV-08.13`

## Existing repository files to inspect or modify

- `app/modules/progress/mastery_model.py`
- `app/services/runtime_kg/integration.py`
- `app/services/runtime_kg/service.py`
- `app/services/runtime_kg/route_integration.py`
- `tests/unit/runtime_kg`

## Planned or new files

- `app/services/educational_validation/state_reasonableness.py`
- `tests/unit/educational_validation/test_state_reasonableness.py`
- `docs/research/longitudinal_validation/evidence/08.14_production_dashboard_and_regression_gate.md`

## Implementation procedure

1. Read the LEV-WS08 workstream specification and confirm prerequisites for task 08.14.
2. Open or update the task evidence record before changing code, data, instruments or governance documents.
3. Implement the required work exactly as scoped: Run continuous transition-reasonableness surveillance after model, KG or content changes.
4. Freeze the analysis input manifest before examining outcome results.
5. Execute the pre-specified analysis with reproducible code and retain diagnostics, uncertainty and sensitivity outputs.
6. Attach or link the required evidence: Production dashboard and regression gate.
7. Mark complete only after the acceptance criterion is independently verifiable.

## Verification commands

```bash
python scripts/educational_validation/verify_lev_task_register.py --repo-root . --json
```
```bash
python scripts/educational_validation/lev_task_cli.py show <TASK_ID>
```
```bash
pytest -q tests/unit/runtime_kg tests/unit/modules/progress/test_mastery_model.py
```

## Acceptance criteria

- [ ] Production dashboard and regression gate.
- [ ] All declared dependencies are closed or formally waived.
- [ ] No critical privacy, fairness, educational-safety or traceability finding remains unresolved.
- [ ] The LEV verifier returns valid=true after status and evidence updates.

## Required evidence

Production dashboard and regression gate.

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
