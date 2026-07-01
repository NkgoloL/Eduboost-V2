# Phase 18 Controlled Beta Incident Response Runbook

This incident response runbook supports controlled beta governance. It does not authorise production release, deployment, public beta, controlled beta launch activation, live learner traffic, or runtime KG implementation.

## Incident Classes

- P0: data exposure, consent bypass, authentication breakage
- P1: learner-blocking journey failure
- P2: parent portal/reporting defect
- P3: cosmetic or non-blocking issue

## Response

P0 and P1 incidents require immediate beta owner notification, engineering triage, evidence preservation, and rollback consideration. Learner data must not be copied into logs or chat systems.
