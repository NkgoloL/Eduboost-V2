# Evidence Archive Completeness Guard

## Purpose

The evidence archive completeness guard verifies that the final controlled staging/beta evidence set is complete enough to reconstruct the release decision.

## Required Archive Evidence

- release identity evidence
- governance seal evidence
- terminal closure assertion evidence
- release final index evidence
- post-beta archive manifest evidence
- outcome report evidence
- known issues evidence
- feedback intake evidence
- retrospective action evidence
- support handoff evidence
- monitoring trigger evidence
- operator packet evidence

## Required Source Documents

- `docs/operations/release_state_snapshot.md`
- `docs/operations/beta_governance_seal_checklist.md`
- `docs/operations/cluster_h_terminal_closure_assertion.md`
- `docs/operations/beta_release_final_index.md`
- `docs/operations/post_beta_evidence_archive_manifest.md`
- `docs/operations/beta_outcome_report_template.md`
- `docs/operations/beta_known_issues_register.md`
- `docs/operations/beta_feedback_intake_contract.md`
- `docs/operations/beta_retrospective_action_register.md`
- `docs/operations/beta_participant_support_handoff_checklist.md`
- `docs/operations/beta_monitoring_incident_trigger_matrix.md`
- `docs/operations/final_beta_operator_packet_index.md`

## Completeness Rules

- archive completeness must reference release candidate and commit SHA
- archive completeness must preserve decision, outcome, feedback, and follow-up evidence
- archive completeness must preserve operational handoff and support references
- archive completeness must preserve governance and terminal closure references
- archive completeness must not include unnecessary learner personal information
- archive completeness must remain audit evidence only

## Boundary

This guard verifies evidence completeness. It does not approve production launch, execute deployment, create release tags, or replace source control history.

## Command

```bash
make evidence-archive-completeness-guard-check
```
