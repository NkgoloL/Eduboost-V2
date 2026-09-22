# LEV-08.15 — Implementation Task Card

**Workstream:** LEV-WS08 — Validate educational plausibility of state transitions  
**Phase:** LEV-6  
**Priority:** P2  
**Status:** `not_started`  
**Implementation type:** `governance_and_documentation`  
**Estimated effort:** S/M  
**Human dependency:** No  
**Cannot be completed by code alone:** No

## Required outcome

Maintain a public-facing limitations explanation and internal known-anomaly register.

## Definition-of-done link

State transitions are educationally plausible.

## Dependencies

- `LEV-08.14`

## Existing repository files to inspect or modify

- `app/modules/progress/mastery_model.py`
- `app/services/runtime_kg/integration.py`
- `app/services/runtime_kg/service.py`
- `app/services/runtime_kg/route_integration.py`
- `tests/unit/runtime_kg`

## Planned or new files

- `app/services/educational_validation/state_reasonableness.py`
- `tests/unit/educational_validation/test_state_reasonableness.py`
- `docs/research/longitudinal_validation/evidence/08.15_current_limitations_and_anomaly_records.md`

## Implementation procedure

1. Read the LEV-WS08 workstream specification and confirm prerequisites for task 08.15.
2. Open or update the task evidence record before changing code, data, instruments or governance documents.
3. Implement the required work exactly as scoped: Maintain a public-facing limitations explanation and internal known-anomaly register.
4. Circulate the draft to accountable and consulted roles.
5. Resolve comments and obtain the required versioned approval.
6. Attach or link the required evidence: Current limitations and anomaly records.
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

- [ ] Current limitations and anomaly records.
- [ ] All declared dependencies are closed or formally waived.
- [ ] No critical privacy, fairness, educational-safety or traceability finding remains unresolved.
- [ ] The LEV verifier returns valid=true after status and evidence updates.

## Required evidence

Current limitations and anomaly records.

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
