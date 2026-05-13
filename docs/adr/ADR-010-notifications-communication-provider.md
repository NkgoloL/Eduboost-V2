# ADR-010: Notifications and Communication Provider Decision

## Status

Accepted for repository-side production-readiness evidence.

## Decision

EduBoost V2 will use provider-neutral notification adapters with separate channels for email, SMS, WhatsApp, push, and in-app notifications.

## Rationale

Provider-neutral adapters allow regional provider changes without weakening audit, consent, idempotency, quiet-hours, retry, bounce, complaint, suppression, or learner-safety controls.

## Required Controls

- email provider is abstracted behind a notification adapter
- SMS provider is abstracted behind a notification adapter
- WhatsApp provider is abstracted behind a notification adapter
- push provider is abstracted behind a notification adapter
- in-app notifications use a database outbox pattern
- provider webhook signature verification is required
- provider webhook idempotency is required
- bounce and complaint handling is required
- unsubscribe and preference handling is required
- raw provider payloads must not be retained without redaction

## Boundary

This ADR records communication provider decision evidence. It does not configure live messaging providers, send notifications, or authorize production communication launch.
