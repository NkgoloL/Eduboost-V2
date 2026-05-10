# Beta Retrospective Action Register

## Purpose

The beta retrospective action register converts beta feedback, known issues, support observations, and release execution findings into owned follow-up work.

## Required Action Fields

| Field | Value |
| --- | --- |
| Action ID | pending |
| Source | outcome report / feedback / known issue / support / monitoring / approval |
| Release Candidate | pending |
| Commit SHA | pending |
| Action Type | bug / documentation / compliance / safety / operations / support |
| Priority | low / medium / high / blocker |
| Owner | pending |
| Target Milestone | pending |
| Evidence Link | pending |
| Status | open / in progress / done / deferred |

## Required Rules

- every high or blocker action must have an owner and target milestone
- compliance action must reference POPIA or consent evidence owner
- safety action must reference AI safety evidence owner
- operational action must reference release owner accountability matrix
- support action must reference participant support handoff checklist
- deferred action must record reason and next review date
- done action must reference evidence or pull request
- unresolved blocker action prevents accepted beta outcome

## Evidence Links

- `docs/operations/beta_outcome_report_template.md`
- `docs/operations/beta_feedback_intake_contract.md`
- `docs/operations/beta_known_issues_register.md`
- `docs/operations/beta_participant_support_handoff_checklist.md`
- `docs/operations/release_owner_accountability_matrix.md`
- `docs/security/POPIA_CONSENT_GATE_CLOSURE.md`
- `docs/ai/CLUSTER_F_CLOSURE.md`

## Boundary

This retrospective register records follow-up actions. It does not create tickets automatically, approve release, execute remediation, or close actions without evidence.

## Command

```bash
make beta-retrospective-action-register-check
```
