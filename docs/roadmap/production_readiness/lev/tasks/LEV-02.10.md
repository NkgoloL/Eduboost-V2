# LEV-02.10 — Implementation Task Card

**Workstream:** LEV-WS02 — Independently review CAPS concepts and assessment items  
**Phase:** LEV-1  
**Priority:** P0  
**Status:** `not_started`  
**Implementation type:** `governance_and_documentation`  
**Estimated effort:** S/M  
**Human dependency:** No  
**Cannot be completed by code alone:** No

## Required outcome

Run cognitive interviews or structured response-process sessions with a diverse pilot subsample.

## Definition-of-done link

CAPS concepts and items are independently reviewed.

## Dependencies

- `LEV-02.09`

## Existing repository files to inspect or modify

- `app/modules/diagnostics/item_bank_pipeline.py`
- `app/modules/diagnostics/item_bank_service.py`
- `app/repositories/item_bank_repository.py`
- `app/services/curriculum/claim_validation.py`
- `docs/architecture/diagnostic_item_bank_canonicality.yml`
- `docs/diagnostics/assessment_quality_fairness_contract.md`
- `scripts/curriculum/build_launch_item_bank.py`
- `scripts/validate_item_bank.py`

## Planned or new files

- `docs/research/longitudinal_validation/caps_validation_blueprint.csv`
- `docs/research/longitudinal_validation/validation_item_bank_manifest.json`
- `docs/research/longitudinal_validation/evidence/02.10_response_process_report_confirms_intended_reasoning_is_elicited.md`

## Implementation procedure

1. Read the LEV-WS02 workstream specification and confirm prerequisites for task 02.10.
2. Open or update the task evidence record before changing code, data, instruments or governance documents.
3. Implement the required work exactly as scoped: Run cognitive interviews or structured response-process sessions with a diverse pilot subsample.
4. Circulate the draft to accountable and consulted roles.
5. Resolve comments and obtain the required versioned approval.
6. Attach or link the required evidence: Response-process report confirms intended reasoning is elicited.
7. Mark complete only after the acceptance criterion is independently verifiable.

## Verification commands

```bash
python scripts/educational_validation/verify_lev_task_register.py --repo-root . --json
```
```bash
python scripts/educational_validation/lev_task_cli.py show <TASK_ID>
```
```bash
pytest -q tests/unit/modules/diagnostics tests/unit/test_diagnostic_item_bank_canonicality.py
```
```bash
python scripts/validate_item_bank.py
```

## Acceptance criteria

- [ ] Response-process report confirms intended reasoning is elicited.
- [ ] All declared dependencies are closed or formally waived.
- [ ] No critical privacy, fairness, educational-safety or traceability finding remains unresolved.
- [ ] The LEV verifier returns valid=true after status and evidence updates.

## Required evidence

Response-process report confirms intended reasoning is elicited.

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
