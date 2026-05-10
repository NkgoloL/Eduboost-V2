# Post-Beta Evidence Archive Manifest

## Purpose

The post-beta evidence archive manifest defines the evidence package to preserve after controlled beta validation, including release decision, feedback, issue, support, and retrospective records.

## Archive Sections

### Release Identity

- `docs/operations/release_state_snapshot.md`
- `docs/operations/release_candidate_tag_manifest.md`
- `docs/operations/beta_release_evidence_bundle.md`

### Release Decision

- `docs/operations/beta_release_decision_log.md`
- `docs/operations/beta_acceptance_exit_criteria.md`
- `docs/operations/beta_outcome_report_template.md`

### Feedback and Issue Evidence

- `docs/operations/beta_feedback_intake_contract.md`
- `docs/operations/beta_known_issues_register.md`
- `docs/operations/beta_retrospective_action_register.md`

### Operations and Support Evidence

- `docs/operations/final_beta_operator_packet_index.md`
- `docs/operations/beta_participant_support_handoff_checklist.md`
- `docs/operations/beta_release_communications_plan.md`
- `docs/operations/beta_monitoring_incident_trigger_matrix.md`

### Audit Evidence

- `docs/operations/release_audit_trail_index.md`
- `docs/operations/final_cluster_h_closeout_rollup.md`
- `docs/operations/CLUSTER_H_CLOSURE.md`

## Archive Rules

- archive must reference release candidate and commit SHA
- archive must preserve accepted, rejected, deferred, or rolled back outcome
- archive must preserve feedback and known issue summaries
- archive must preserve unresolved follow-up ownership
- archive must preserve support and incident trigger references
- archive must not include unnecessary learner personal information
- archive must remain audit evidence, not production launch authorization

## Boundary

This archive manifest preserves evidence. It does not approve release, execute deployment, create release tags, or replace source control history.

## Command

```bash
make post-beta-evidence-archive-manifest-check
```
