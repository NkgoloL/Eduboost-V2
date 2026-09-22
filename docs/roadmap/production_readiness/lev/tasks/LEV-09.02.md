# LEV-09.02 — Implementation Task Card

**Workstream:** LEV-WS09 — Establish validity across relevant learner contexts  
**Phase:** LEV-0  
**Priority:** P0  
**Status:** `not_started`  
**Implementation type:** `governance_and_documentation`  
**Estimated effort:** S/M  
**Human dependency:** No  
**Cannot be completed by code alone:** No

## Required outcome

Determine which context variables may lawfully and ethically be collected, for what purpose and for how long.

## Definition-of-done link

Results remain valid across relevant learner contexts.

## Dependencies

- `LEV-09.01`

## Existing repository files to inspect or modify

- `docs/diagnostics/assessment_quality_fairness_contract.md`
- `app/modules/diagnostics/bias_review_router.py`
- `app/modules/diagnostics/quality_scorer.py`
- `app/services/runtime_kg/feature_flags.py`
- `docs/compliance`

## Planned or new files

- `app/services/educational_validation/fairness.py`
- `scripts/educational_validation/run_fairness_analysis.py`
- `docs/research/longitudinal_validation/evidence/09.02_approved_data_minimisation_and_lawful_basis_record.md`

## Implementation procedure

1. Read the LEV-WS09 workstream specification and confirm prerequisites for task 09.02.
2. Open or update the task evidence record before changing code, data, instruments or governance documents.
3. Implement the required work exactly as scoped: Determine which context variables may lawfully and ethically be collected, for what purpose and for how long.
4. Circulate the draft to accountable and consulted roles.
5. Resolve comments and obtain the required versioned approval.
6. Attach or link the required evidence: Approved data-minimisation and lawful-basis record.
7. Mark complete only after the acceptance criterion is independently verifiable.

## Verification commands

```bash
python scripts/educational_validation/verify_lev_task_register.py --repo-root . --json
```
```bash
python scripts/educational_validation/lev_task_cli.py show <TASK_ID>
```
```bash
pytest -q tests/unit/test_diagnostics_assessment_production_readiness.py
```

## Acceptance criteria

- [ ] Approved data-minimisation and lawful-basis record.
- [ ] All declared dependencies are closed or formally waived.
- [ ] No critical privacy, fairness, educational-safety or traceability finding remains unresolved.
- [ ] The LEV verifier returns valid=true after status and evidence updates.

## Required evidence

Approved data-minimisation and lawful-basis record.

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
