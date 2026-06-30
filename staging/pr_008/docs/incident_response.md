# Incident Response

## Incident categories

| Category | Examples | Initial severity |
|---|---|---|
| Security incident | credential exposure, suspicious access, exploit attempt | critical |
| Learner data exposure | PII disclosure, consent bypass, export to wrong guardian | critical |
| Auth outage | login/refresh outage, widespread session invalidation | high |
| Billing outage | webhook failure, incorrect subscription state | high |
| AI content safety issue | unsafe or non-CAPS lesson output | high |
| Data corruption | broken migration, audit chain failure, invalid learner state | critical |
| Availability outage | API down, DB unavailable, Redis unavailable | critical |

## Emergency actions

| Action | When |
|---|---|
| Disable lesson generation | unsafe AI output, provider compromise, PII-redaction failure |
| Revoke sessions | token exposure, account takeover, auth bypass |
| Disable provider | LLM/email/billing provider incident |
| Freeze billing webhooks | duplicate/invalid subscription writes |
| Enable maintenance mode | unsafe partial availability or migration failure |
| Stop optional learner processing | audit write failure or consent enforcement failure |

## First 15 minutes

1. Assign incident commander.
2. Classify incident category and severity.
3. Preserve logs, deployment metadata, and recent change set.
4. Check `/health`, `/ready`, `/metrics`, dashboards, and alerts.
5. Apply the smallest safe containment action.
6. If learner data may be affected, notify the Information Officer.

## Postmortem template

- Summary
- Timeline
- Impact
- Root cause
- Detection gap
- Response gap
- Corrective actions
- Owner and due date
- Learner/guardian communication required?
- POPIA/legal review required?

Run at least one tabletop exercise before production launch.
