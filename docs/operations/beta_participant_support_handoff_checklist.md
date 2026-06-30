# Beta Participant Support Handoff Checklist

## Purpose

The beta participant support handoff checklist defines the support evidence and
owner handoff required before beta participants are invited or supported.

## Required Support Owners

- beta support contact
- incident contact
- privacy/POPIA approver
- technical approver
- post-deploy verification owner
- rollback owner

## Required Support Inputs

- beta boundary and non-production scope
- known issues and follow-ups
- support intake channel
- escalation channel
- privacy request escalation path
- data deletion request escalation path
- AI safety issue escalation path
- rollback status contact
- release decision log location

## Required Participant Support Rules

- support must not promise production availability
- support must not request unnecessary learner personal information
- privacy requests must be routed to POPIA process owner
- suspected access-boundary incidents must be escalated immediately
- AI safety issues must be linked to AI safety evidence owner
- support outcomes must be summarized after beta validation

## Evidence Links

- `docs/operations/beta_release_decision_log.md`
- `docs/operations/beta_monitoring_incident_trigger_matrix.md`
- `docs/security/POPIA_CONSENT_GATE_CLOSURE.md`
- `docs/ai/CLUSTER_F_CLOSURE.md`
- `docs/operations/beta_rollback_runbook.md`

## Boundary

This handoff checklist supports participant support readiness. It does not invite beta participants, approve release, execute deployment, or collect participant data.

## Command

```bash
make beta-participant-support-handoff-check
```
