# LEV-12.01 — Implementation Task Card

**Workstream:** LEV-WS12 — Replicate findings in another cohort or academic year  
**Phase:** LEV-3  
**Priority:** P1  
**Status:** `not_started`  
**Implementation type:** `governance_and_documentation`  
**Estimated effort:** S/M  
**Human dependency:** No  
**Cannot be completed by code alone:** Yes

## Required outcome

Identify the primary claims requiring replication and rank them by decision importance.

## Definition-of-done link

Findings replicate in another cohort or academic year.

## Dependencies

- `LEV-10.15`
- `LEV-11.13`

## Existing repository files to inspect or modify

- `docs/research/mastery_model`
- `scripts/mastery_research`
- `docs/release-evidence/roadmap-reconciliation/rr-013-advanced-mastery-model-research`

## Planned or new files

- `docs/research/longitudinal_validation/replication_protocol.md`
- `scripts/educational_validation/run_replication_analysis.py`
- `docs/research/longitudinal_validation/evidence/12.01_replication_claim_register.md`

## Implementation procedure

1. Read the LEV-WS12 workstream specification and confirm prerequisites for task 12.01.
2. Open or update the task evidence record before changing code, data, instruments or governance documents.
3. Implement the required work exactly as scoped: Identify the primary claims requiring replication and rank them by decision importance.
4. Circulate the draft to accountable and consulted roles.
5. Resolve comments and obtain the required versioned approval.
6. Attach or link the required evidence: Replication claim register.
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

- [ ] Replication claim register.
- [ ] All declared dependencies are closed or formally waived.
- [ ] No critical privacy, fairness, educational-safety or traceability finding remains unresolved.
- [ ] The LEV verifier returns valid=true after status and evidence updates.

## Required evidence

Replication claim register.

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
