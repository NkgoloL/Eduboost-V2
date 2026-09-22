# LEV-08.02 — Implementation Task Card

**Workstream:** LEV-WS08 — Validate educational plausibility of state transitions  
**Phase:** LEV-1  
**Priority:** P0  
**Status:** `not_started`  
**Implementation type:** `human_governance_or_research`  
**Estimated effort:** L/XL; elapsed time may be term- or cohort-bound  
**Human dependency:** Yes  
**Cannot be completed by code alone:** Yes

## Required outcome

Create synthetic and curated learner histories representing expected learning, guessing, assistance, contradiction, forgetting and recovery.

## Definition-of-done link

State transitions are educationally plausible.

## Dependencies

- `LEV-08.01`

## Existing repository files to inspect or modify

- `app/modules/progress/mastery_model.py`
- `app/services/runtime_kg/integration.py`
- `app/services/runtime_kg/service.py`
- `app/services/runtime_kg/route_integration.py`
- `tests/unit/runtime_kg`

## Planned or new files

- `app/services/educational_validation/state_reasonableness.py`
- `tests/unit/educational_validation/test_state_reasonableness.py`
- `docs/research/longitudinal_validation/evidence/08.02_golden_transition_fixtures.md`

## Implementation procedure

1. Read the LEV-WS08 workstream specification and confirm prerequisites for task 08.02.
2. Open or update the task evidence record before changing code, data, instruments or governance documents.
3. Implement the required work exactly as scoped: Create synthetic and curated learner histories representing expected learning, guessing, assistance, contradiction, forgetting and recovery.
4. Confirm lawful authority, consent/assent, independence and conflict-of-interest controls before participant or reviewer activity.
5. Record attendance, decisions, dissent, requested corrections and signed approval or rejection.
6. Attach or link the required evidence: Golden transition fixtures.
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

- [ ] Golden transition fixtures.
- [ ] All declared dependencies are closed or formally waived.
- [ ] No critical privacy, fairness, educational-safety or traceability finding remains unresolved.
- [ ] The LEV verifier returns valid=true after status and evidence updates.

## Required evidence

Golden transition fixtures.

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
