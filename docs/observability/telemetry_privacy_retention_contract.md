# Telemetry Privacy and Retention Contract

## Purpose

This contract defines privacy and retention controls for production telemetry.

## Required Privacy Controls

- PII redaction before log retention
- PII-safe metric labels
- PII-safe trace attributes
- raw prompt exclusion
- raw AI output exclusion
- raw payment provider payload exclusion
- learner name exclusion unless explicitly justified
- contact detail redaction
- telemetry deletion workflow
- telemetry export workflow

## Required Retention Controls

- metrics retention period
- logs retention period
- traces retention period
- audit logs retention period
- retention owner
- deletion owner
- export owner
- legal hold boundary

## Boundary

This contract records telemetry privacy and retention readiness. It does not delete data, export data, or configure a live telemetry backend.
