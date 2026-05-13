# Runbook: API Outage

## Detection

- confirm alert
- check dashboard
- review recent deploy

## Triage

- classify severity
- assign incident commander
- identify affected routes

## Mitigation

- scale service
- rollback recent release
- disable failing dependency

## Recovery

- verify health checks
- run smoke tests

## Verification

- confirm API availability
- confirm error rate normal

## Rollback Criteria

- error rate remains elevated
- smoke tests fail
- customer impact persists

## Boundary

This runbook records API outage response readiness. It does not execute remediation.
