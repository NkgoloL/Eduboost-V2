# LEV-03.04 — Implementation Task Card

**Workstream:** LEV-WS03 — Make learner evidence and state changes fully traceable  
**Phase:** LEV-1  
**Priority:** P0  
**Status:** `not_started`  
**Implementation type:** `analysis_and_validation`  
**Estimated effort:** M/L after data readiness  
**Human dependency:** No  
**Cannot be completed by code alone:** Yes

## Required outcome

Create a model registry storing code commit, training data manifest, features, parameters, authorised population, limitations, expiry and rollback model.

## Definition-of-done link

Learner evidence and state changes are fully traceable.

## Dependencies

- `LEV-03.03`

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
- `docs/research/longitudinal_validation/evidence/03.04_registry_supports_immutable_model_snapshots.md`

## Implementation procedure

1. Read the LEV-WS03 workstream specification and confirm prerequisites for task 03.04.
2. Open or update the task evidence record before changing code, data, instruments or governance documents.
3. Implement the required work exactly as scoped: Create a model registry storing code commit, training data manifest, features, parameters, authorised population, limitations, expiry and rollback model.
4. Freeze the analysis input manifest before examining outcome results.
5. Execute the pre-specified analysis with reproducible code and retain diagnostics, uncertainty and sensitivity outputs.
6. Attach or link the required evidence: Registry supports immutable model snapshots.
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

- [ ] Registry supports immutable model snapshots.
- [ ] All declared dependencies are closed or formally waived.
- [ ] No critical privacy, fairness, educational-safety or traceability finding remains unresolved.
- [ ] The LEV verifier returns valid=true after status and evidence updates.

## Required evidence

Registry supports immutable model snapshots.

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
