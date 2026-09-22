# LEV-09.04 — Implementation Task Card

**Workstream:** LEV-WS09 — Establish validity across relevant learner contexts  
**Phase:** LEV-1  
**Priority:** P0  
**Status:** `not_started`  
**Implementation type:** `human_governance_or_research`  
**Estimated effort:** L/XL; elapsed time may be term- or cohort-bound  
**Human dependency:** Yes  
**Cannot be completed by code alone:** Yes

## Required outcome

Design recruitment to include varied school contexts, baseline attainment, language, device and connectivity conditions.

## Definition-of-done link

Results remain valid across relevant learner contexts.

## Dependencies

- `LEV-09.03`

## Existing repository files to inspect or modify

- `docs/diagnostics/assessment_quality_fairness_contract.md`
- `app/modules/diagnostics/bias_review_router.py`
- `app/modules/diagnostics/quality_scorer.py`
- `app/services/runtime_kg/feature_flags.py`
- `docs/compliance`

## Planned or new files

- `app/services/educational_validation/fairness.py`
- `scripts/educational_validation/run_fairness_analysis.py`
- `docs/research/longitudinal_validation/evidence/09.04_sampling_and_recruitment_plan.md`

## Implementation procedure

1. Read the LEV-WS09 workstream specification and confirm prerequisites for task 09.04.
2. Open or update the task evidence record before changing code, data, instruments or governance documents.
3. Implement the required work exactly as scoped: Design recruitment to include varied school contexts, baseline attainment, language, device and connectivity conditions.
4. Confirm lawful authority, consent/assent, independence and conflict-of-interest controls before participant or reviewer activity.
5. Record attendance, decisions, dissent, requested corrections and signed approval or rejection.
6. Attach or link the required evidence: Sampling and recruitment plan.
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

- [ ] Sampling and recruitment plan.
- [ ] All declared dependencies are closed or formally waived.
- [ ] No critical privacy, fairness, educational-safety or traceability finding remains unresolved.
- [ ] The LEV verifier returns valid=true after status and evidence updates.

## Required evidence

Sampling and recruitment plan.

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
