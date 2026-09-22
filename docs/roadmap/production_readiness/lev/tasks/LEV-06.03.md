# LEV-06.03 — Implementation Task Card

**Workstream:** LEV-WS06 — Demonstrate delayed-retention validity  
**Phase:** LEV-1  
**Priority:** P0  
**Status:** `not_started`  
**Implementation type:** `governance_and_documentation`  
**Estimated effort:** S/M  
**Human dependency:** No  
**Cannot be completed by code alone:** No

## Required outcome

Define when a mastery declaration becomes eligible for a retention probe and how re-practice affects interpretation.

## Definition-of-done link

Estimates predict delayed retention.

## Dependencies

- `LEV-06.02`

## Existing repository files to inspect or modify

- `app/modules/progress/mastery_model.py`
- `app/services/runtime_kg/service.py`
- `app/modules/study_plans/runtime_kg_planner.py`
- `app/services/study_plan_service_v2.py`
- `docs/learning_science/mastery_model.md`

## Planned or new files

- `app/services/educational_validation/retention.py`
- `scripts/educational_validation/run_retention_analysis.py`
- `docs/research/longitudinal_validation/evidence/06.03_eligibility_and_censoring_rules.md`

## Implementation procedure

1. Read the LEV-WS06 workstream specification and confirm prerequisites for task 06.03.
2. Open or update the task evidence record before changing code, data, instruments or governance documents.
3. Implement the required work exactly as scoped: Define when a mastery declaration becomes eligible for a retention probe and how re-practice affects interpretation.
4. Circulate the draft to accountable and consulted roles.
5. Resolve comments and obtain the required versioned approval.
6. Attach or link the required evidence: Eligibility and censoring rules.
7. Mark complete only after the acceptance criterion is independently verifiable.

## Verification commands

```bash
python scripts/educational_validation/verify_lev_task_register.py --repo-root . --json
```
```bash
python scripts/educational_validation/lev_task_cli.py show <TASK_ID>
```
```bash
pytest -q tests/unit/test_study_plan_service_v2.py tests/unit/runtime_kg
```

## Acceptance criteria

- [ ] Eligibility and censoring rules.
- [ ] All declared dependencies are closed or formally waived.
- [ ] No critical privacy, fairness, educational-safety or traceability finding remains unresolved.
- [ ] The LEV verifier returns valid=true after status and evidence updates.

## Required evidence

Eligibility and censoring rules.

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
