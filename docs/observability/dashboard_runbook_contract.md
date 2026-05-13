# Dashboard and Runbook Contract

## Purpose

This contract defines dashboard and runbook requirements for production observability.

## Required Dashboards

- Production API Overview
- AI Provider Safety and Latency
- Notifications and Billing Operations
- POPIA Privacy Operations
- Frontend Experience and Errors
- Database Performance and Saturation

## Required Dashboard Panels

- traffic
- latency
- errors
- saturation
- SLO burn
- retry count
- dead-letter count
- provider failures

## Required Runbook Sections

- symptom
- impact
- dashboard links
- likely causes
- immediate mitigation
- rollback criteria
- escalation owner
- post-incident evidence

## Boundary

This contract records dashboard and runbook readiness. It does not create live dashboards or execute incident response.
