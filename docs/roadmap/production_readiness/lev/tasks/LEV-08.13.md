# LEV-08.13 — Implementation Task Card

**Workstream:** LEV-WS08 — Validate educational plausibility of state transitions  
**Phase:** LEV-3  
**Priority:** P1  
**Status:** `not_started`  
**Implementation type:** `operations`  
**Estimated effort:** M  
**Human dependency:** No  
**Cannot be completed by code alone:** Yes

## Required outcome

Set quantitative alert thresholds for unexplained jumps, reversals and cross-concept spill-over.

## Definition-of-done link

State transitions are educationally plausible.

## Dependencies

- `LEV-08.12`

## Existing repository files to inspect or modify

- `app/modules/progress/mastery_model.py`
- `app/services/runtime_kg/integration.py`
- `app/services/runtime_kg/service.py`
- `app/services/runtime_kg/route_integration.py`
- `tests/unit/runtime_kg`

## Planned or new files

- `app/services/educational_validation/state_reasonableness.py`
- `tests/unit/educational_validation/test_state_reasonableness.py`
- `docs/research/longitudinal_validation/evidence/08.13_monitoring_policy.md`

## Implementation procedure

1. Read the LEV-WS08 workstream specification and confirm prerequisites for task 08.13.
2. Open or update the task evidence record before changing code, data, instruments or governance documents.
3. Implement the required work exactly as scoped: Set quantitative alert thresholds for unexplained jumps, reversals and cross-concept spill-over.
4. Define thresholds, escalation ownership, fallback behaviour and evidence retention.
5. Exercise the control in a rehearsal or controlled environment before production authority.
6. Attach or link the required evidence: Monitoring policy.
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

- [ ] Monitoring policy.
- [ ] All declared dependencies are closed or formally waived.
- [ ] No critical privacy, fairness, educational-safety or traceability finding remains unresolved.
- [ ] The LEV verifier returns valid=true after status and evidence updates.

## Required evidence

Monitoring policy.

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
