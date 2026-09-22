# LEV-07.14 — Implementation Task Card

**Workstream:** LEV-WS07 — Demonstrate transfer validity  
**Phase:** LEV-5  
**Priority:** P2  
**Status:** `not_started`  
**Implementation type:** `governance_and_documentation`  
**Estimated effort:** S/M  
**Human dependency:** No  
**Cannot be completed by code alone:** Yes

## Required outcome

Replicate transfer findings using new items and a later cohort.

## Definition-of-done link

Estimates predict transfer to unfamiliar tasks.

## Dependencies

- `LEV-07.13`

## Existing repository files to inspect or modify

- `app/services/runtime_kg/service.py`
- `app/services/runtime_kg/schemas.py`
- `app/modules/lessons/adaptive_remediation.py`
- `app/modules/study_plans/runtime_kg_planner.py`
- `app/services/content_blueprint_validation.py`

## Planned or new files

- `app/services/educational_validation/transfer.py`
- `scripts/educational_validation/run_transfer_analysis.py`
- `docs/research/longitudinal_validation/evidence/07.14_replication_report.md`

## Implementation procedure

1. Read the LEV-WS07 workstream specification and confirm prerequisites for task 07.14.
2. Open or update the task evidence record before changing code, data, instruments or governance documents.
3. Implement the required work exactly as scoped: Replicate transfer findings using new items and a later cohort.
4. Circulate the draft to accountable and consulted roles.
5. Resolve comments and obtain the required versioned approval.
6. Attach or link the required evidence: Replication report.
7. Mark complete only after the acceptance criterion is independently verifiable.

## Verification commands

```bash
python scripts/educational_validation/verify_lev_task_register.py --repo-root . --json
```
```bash
python scripts/educational_validation/lev_task_cli.py show <TASK_ID>
```
```bash
pytest -q tests/unit/runtime_kg tests/unit/test_lesson_service_v2.py
```

## Acceptance criteria

- [ ] Replication report.
- [ ] All declared dependencies are closed or formally waived.
- [ ] No critical privacy, fairness, educational-safety or traceability finding remains unresolved.
- [ ] The LEV verifier returns valid=true after status and evidence updates.

## Required evidence

Replication report.

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
