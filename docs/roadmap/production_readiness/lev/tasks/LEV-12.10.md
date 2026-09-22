# LEV-12.10 — Implementation Task Card

**Workstream:** LEV-WS12 — Replicate findings in another cohort or academic year  
**Phase:** LEV-5  
**Priority:** P2  
**Status:** `not_started`  
**Implementation type:** `human_governance_or_research`  
**Estimated effort:** L/XL; elapsed time may be term- or cohort-bound  
**Human dependency:** Yes  
**Cannot be completed by code alone:** Yes

## Required outcome

Investigate non-replication through population, curriculum, item, teacher-use, platform and model-change analyses.

## Definition-of-done link

Findings replicate in another cohort or academic year.

## Dependencies

- `LEV-12.09`

## Existing repository files to inspect or modify

- `docs/research/mastery_model`
- `scripts/mastery_research`
- `docs/release-evidence/roadmap-reconciliation/rr-013-advanced-mastery-model-research`

## Planned or new files

- `docs/research/longitudinal_validation/replication_protocol.md`
- `scripts/educational_validation/run_replication_analysis.py`
- `docs/research/longitudinal_validation/evidence/12.10_non_replication_root_cause_report.md`

## Implementation procedure

1. Read the LEV-WS12 workstream specification and confirm prerequisites for task 12.10.
2. Open or update the task evidence record before changing code, data, instruments or governance documents.
3. Implement the required work exactly as scoped: Investigate non-replication through population, curriculum, item, teacher-use, platform and model-change analyses.
4. Confirm lawful authority, consent/assent, independence and conflict-of-interest controls before participant or reviewer activity.
5. Record attendance, decisions, dissent, requested corrections and signed approval or rejection.
6. Attach or link the required evidence: Non-replication root-cause report.
7. Mark complete only after the acceptance criterion is independently verifiable.

## Verification commands

```bash
python scripts/educational_validation/verify_lev_task_register.py --repo-root . --json
```
```bash
python scripts/educational_validation/lev_task_cli.py show <TASK_ID>
```
```bash
python scripts/roadmap_reconciliation/verify_rr013_advanced_mastery_model_research.py --json
```

## Acceptance criteria

- [ ] Non-replication root-cause report.
- [ ] All declared dependencies are closed or formally waived.
- [ ] No critical privacy, fairness, educational-safety or traceability finding remains unresolved.
- [ ] The LEV verifier returns valid=true after status and evidence updates.

## Required evidence

Non-replication root-cause report.

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
