# Notification Template Governance Contract

## Purpose

This contract defines governance for notification templates.

## Required Template Controls

- template ID
- template version
- locale
- audience
- purpose
- channel list
- required variable list
- human review status
- learner-safety review
- PII leakage review
- unsubscribe footer for marketing
- HTML disabled for SMS
- template changelog
- template rollback path

## Required Template Tests

- required variables are present
- unknown variables are rejected
- learner billing templates are rejected
- learner marketing templates are rejected
- reviewed flag is required
- SMS HTML is rejected
- contact details are redacted from audit metadata

## Boundary

This contract records template governance readiness. It does not send messages or create provider-side templates.
