# Alerting and Incident Routing Contract

## Purpose

This contract defines production alerting, severity, incident routing, and runbook requirements.

## Required Alert Controls

- alert name
- severity
- service tier
- alert expression
- route owner
- runbook path
- paging requirement
- deduplication key
- suppression policy
- escalation policy

## Required Alert Categories

- API error-rate spike
- API latency SLO burn
- database saturation
- LLM provider failure spike
- billing webhook failure spike
- notification dead-letter spike
- POPIA export failure
- authentication anomaly
- frontend error spike
- background worker backlog

## Required Incident Routes

- engineering
- security
- privacy
- release owner
- support

## Boundary

This contract records alerting and incident routing readiness. It does not page operators or configure live alerting.
