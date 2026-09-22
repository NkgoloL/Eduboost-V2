# LEV-15.13 — Implementation Task Card

**Workstream:** LEV-WS15 — Document unsupported uses and residual limitations  
**Phase:** LEV-6  
**Priority:** P2  
**Status:** `not_started`  
**Implementation type:** `analysis_and_validation`  
**Estimated effort:** M/L after data readiness  
**Human dependency:** No  
**Cannot be completed by code alone:** Yes

## Required outcome

Add CI or release-gate checks requiring current limitation records for every promoted model.

## Definition-of-done link

EduBoost clearly documents which uses remain unsupported.

## Dependencies

- `LEV-15.12`
- `LEV-13.12`

## Existing repository files to inspect or modify

- `app/services/runtime_kg/feature_flags.py`
- `app/services/runtime_kg/schemas.py`
- `docs/learning_science/mastery_model.md`
- `docs/diagnostics/mastery_model_assessment_contract.md`
- `docs/roadmap/production_readiness/production_readiness_register.json`

## Planned or new files

- `docs/research/longitudinal_validation/unsupported_use_register.json`
- `app/services/educational_validation/use_authorization.py`
- `docs/research/longitudinal_validation/evidence/15.13_release_control_operational.md`

## Implementation procedure

1. Read the LEV-WS15 workstream specification and confirm prerequisites for task 15.13.
2. Open or update the task evidence record before changing code, data, instruments or governance documents.
3. Implement the required work exactly as scoped: Add CI or release-gate checks requiring current limitation records for every promoted model.
4. Freeze the analysis input manifest before examining outcome results.
5. Execute the pre-specified analysis with reproducible code and retain diagnostics, uncertainty and sensitivity outputs.
6. Attach or link the required evidence: Release control operational.
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

- [ ] Release control operational.
- [ ] All declared dependencies are closed or formally waived.
- [ ] No critical privacy, fairness, educational-safety or traceability finding remains unresolved.
- [ ] The LEV verifier returns valid=true after status and evidence updates.

## Required evidence

Release control operational.

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
