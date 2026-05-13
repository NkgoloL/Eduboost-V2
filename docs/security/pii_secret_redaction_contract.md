# PII and Secret Redaction Contract

## Required Redaction Controls

- raw passwords are prohibited in logs
- raw API keys are prohibited in logs
- raw tokens are prohibited in logs
- private keys are prohibited in logs
- learner names are minimized
- emails are redacted where not required
- phone numbers are redacted where not required
- raw AI prompts are excluded from telemetry
- raw provider payloads are excluded from telemetry

## Boundary

This contract records redaction expectations. It does not process live telemetry.
