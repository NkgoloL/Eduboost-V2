# Pricing operations and refund process

## Initial operating decision

EduBoost remains free during private alpha. Paid plans are disabled unless the billing capability is available and Stripe checkout/webhook/reconciliation have passed staging validation.

## Paid-plan readiness gates

- Stripe secret key, webhook secret, and price ID are configured through the approved secret store.
- Checkout, cancellation, failed-payment downgrade, and webhook idempotency tests pass.
- Refund policy has been approved and published.
- Support team can identify a guardian subscription without exposing learner PII.
- Finance owner can reconcile Stripe events against internal subscription records.

## Refund process

1. Guardian submits request through support.
2. Support verifies account ownership and billing event.
3. Finance approves or rejects according to the published Refund Policy.
4. Support communicates the outcome.
5. Audit event records the decision without storing unnecessary learner details.

## Escalation

Billing disputes involving minors, school-sponsored accounts, or suspected fraud escalate to the product owner and compliance owner before action.
