# LEV-03.07 — Implementation Task Card

**Workstream:** LEV-WS03 — Make learner evidence and state changes fully traceable  
**Phase:** LEV-1  
**Priority:** P0  
**Status:** `not_started`  
**Implementation type:** `engineering`  
**Estimated effort:** M/L  
**Human dependency:** No  
**Cannot be completed by code alone:** No

## Required outcome

Implement trace-reconstruction APIs and internal tools for authorised reviewers.

## Definition-of-done link

Learner evidence and state changes are fully traceable.

## Dependencies

- `LEV-03.06`

## Existing repository files to inspect or modify

- `app/models/runtime_kg.py`
- `app/services/runtime_kg/repository.py`
- `app/services/runtime_kg/service.py`
- `app/services/runtime_kg/integration.py`
- `app/repositories/audit_repository.py`
- `app/services/audit_service.py`
- `app/core/audit.py`
- `alembic/versions`

## Planned or new files

- `app/models/educational_validation.py`
- `app/repositories/educational_validation_repository.py`
- `app/services/educational_validation/traceability.py`
- `alembic/versions/<new>_educational_validation_traceability.py`
- `docs/research/longitudinal_validation/evidence/03.07_a_sampled_learner_concept_history_can_be_reconstructed_deterministically.md`

## Implementation procedure

1. Read the LEV-WS03 workstream specification and confirm prerequisites for task 03.07.
2. Open or update the task evidence record before changing code, data, instruments or governance documents.
3. Implement the required work exactly as scoped: Implement trace-reconstruction APIs and internal tools for authorised reviewers.
4. Add or update unit, integration and contract tests for the changed behaviour.
5. Run focused checks, then the LEV register verifier and applicable repository quality gates.
6. Attach or link the required evidence: A sampled learner-concept history can be reconstructed deterministically.
7. Mark complete only after the acceptance criterion is independently verifiable.

## Verification commands

```bash
python scripts/educational_validation/verify_lev_task_register.py --repo-root . --json
```
```bash
python scripts/educational_validation/lev_task_cli.py show <TASK_ID>
```
```bash
pytest -q tests/unit/runtime_kg tests/integration/test_audit_immutability.py
```

## Acceptance criteria

- [ ] A sampled learner-concept history can be reconstructed deterministically.
- [ ] All declared dependencies are closed or formally waived.
- [ ] No critical privacy, fairness, educational-safety or traceability finding remains unresolved.
- [ ] The LEV verifier returns valid=true after status and evidence updates.

## Required evidence

A sampled learner-concept history can be reconstructed deterministically.

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
