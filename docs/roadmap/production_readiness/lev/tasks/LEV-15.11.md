# LEV-15.11 — Implementation Task Card

**Workstream:** LEV-WS15 — Document unsupported uses and residual limitations  
**Phase:** LEV-4  
**Priority:** P2  
**Status:** `not_started`  
**Implementation type:** `governance_and_documentation`  
**Estimated effort:** S/M  
**Human dependency:** No  
**Cannot be completed by code alone:** Yes

## Required outcome

Update limitations based on impact-study findings, subgroup results and adverse-consequence evidence.

## Definition-of-done link

EduBoost clearly documents which uses remain unsupported.

## Dependencies

- `LEV-15.10`

## Existing repository files to inspect or modify

- `app/services/runtime_kg/feature_flags.py`
- `app/services/runtime_kg/schemas.py`
- `docs/learning_science/mastery_model.md`
- `docs/diagnostics/mastery_model_assessment_contract.md`
- `docs/roadmap/production_readiness/production_readiness_register.json`

## Planned or new files

- `docs/research/longitudinal_validation/unsupported_use_register.json`
- `app/services/educational_validation/use_authorization.py`
- `docs/research/longitudinal_validation/evidence/15.11_post_study_limitations_revision.md`

## Implementation procedure

1. Read the LEV-WS15 workstream specification and confirm prerequisites for task 15.11.
2. Open or update the task evidence record before changing code, data, instruments or governance documents.
3. Implement the required work exactly as scoped: Update limitations based on impact-study findings, subgroup results and adverse-consequence evidence.
4. Circulate the draft to accountable and consulted roles.
5. Resolve comments and obtain the required versioned approval.
6. Attach or link the required evidence: Post-study limitations revision.
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

- [ ] Post-study limitations revision.
- [ ] All declared dependencies are closed or formally waived.
- [ ] No critical privacy, fairness, educational-safety or traceability finding remains unresolved.
- [ ] The LEV verifier returns valid=true after status and evidence updates.

## Required evidence

Post-study limitations revision.

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
