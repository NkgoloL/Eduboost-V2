# Runbook: notification_dead_letter_spike

## Symptom

Alert notification_dead_letter_spike fired.

## Impact

Potential degradation in production service reliability, privacy operations, provider integrations, or support workflows.

## Immediate Mitigation

- Confirm alert route owner.
- Open the relevant dashboard.
- Check recent deploys and provider status.
- Apply documented rollback criteria where applicable.
- Record post-incident evidence.

## Escalation Owner

Engineering, privacy, release owner, or support route based on alert metadata.

## Boundary

This runbook is repository-side evidence. It does not execute remediation automatically.
