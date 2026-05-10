# Beta Feedback Intake Contract

## Purpose

The beta feedback intake contract defines how feedback from controlled beta validation is captured, classified, and linked to release evidence.

## Required Feedback Fields

| Field | Value |
| --- | --- |
| Feedback ID | pending |
| Reporter Role | learner / parent / operator / support / approver |
| Submitted At UTC | pending |
| Release Candidate | pending |
| Commit SHA | pending |
| Area | learner / parent / AI safety / consent / privacy / performance / support |
| Severity | low / medium / high / blocker |
| Summary | pending |
| Evidence Link | pending |
| Owner | pending |
| Status | open / triaged / accepted / deferred / closed |

## Classification Rules

- blocker feedback must be linked to beta monitoring and incident trigger matrix
- privacy feedback must be routed to POPIA process owner
- AI safety feedback must be linked to AI safety evidence owner
- access-boundary feedback must be escalated to technical approver and privacy/POPIA approver
- support feedback must reference beta participant support handoff checklist
- accepted feedback must reference a follow-up owner and status
- deferred feedback must record reason and target milestone

## Evidence Links

- `docs/operations/beta_monitoring_incident_trigger_matrix.md`
- `docs/operations/beta_participant_support_handoff_checklist.md`
- `docs/security/POPIA_CONSENT_GATE_CLOSURE.md`
- `docs/ai/CLUSTER_F_CLOSURE.md`
- `docs/operations/beta_release_decision_log.md`

## Boundary

This feedback intake contract records beta feedback evidence. It does not collect live participant data, approve release, execute deployment, or create product commitments.

## Command

```bash
make beta-feedback-intake-contract-check
```
