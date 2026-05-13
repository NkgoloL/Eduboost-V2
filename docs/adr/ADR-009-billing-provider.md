# ADR-009: Billing Provider Decision

## Status

Accepted for repository-side production-readiness evidence.

## Decision

EduBoost V2 will use a hosted-checkout billing provider integration pattern. Stripe is the canonical provider for repository-side contract evidence, while Paystack and Yoco remain documented regional alternatives.

## Rationale

Hosted checkout ensures the application must not store raw card data and avoids raw card-data storage in the application, narrows PCI exposure, and allows billing events to enter the system through signed webhooks.

## Required Controls

- Webhook signature verification is mandatory.
- Webhook idempotency is mandatory.
- Webhook replay protection is mandatory.
- Billing events require audit records.
- Raw provider payloads must not be retained without redaction.
- Subscription state changes must follow the canonical state machine.

## Boundary

This ADR records provider decision evidence. It does not configure a live merchant account, execute payments, create subscriptions, or authorize production billing launch.
