# 9. Billing, subscriptions, payments, and monetization

## 9.1 Provider and architecture

- [ ] `P0` Decide production billing provider.
- [ ] `P0` Document billing provider decision in ADR.
- [ ] `P0` Document billing architecture.
- [ ] `P0` Define billing data model.
- [ ] `P0` Define subscription state machine.
- [ ] `P0` Define state `trial`.
- [ ] `P0` Define state `active`.
- [ ] `P0` Define state `past_due`.
- [ ] `P0` Define state `paused`.
- [ ] `P0` Define state `canceled`.
- [ ] `P0` Define state `expired`.
- [ ] `P1` Define sponsorship state if sponsored learner model is in scope.
- [ ] `P1` Define school-plan billing model if schools are in scope.

## 9.2 Webhooks

- [ ] `P0` Implement webhook signature verification.
- [ ] `P0` Implement webhook idempotency.
- [ ] `P0` Implement webhook replay protection.
- [ ] `P0` Implement webhook audit logging.
- [ ] `P0` Add webhook tests for valid signature.
- [ ] `P0` Add webhook tests for invalid signature.
- [ ] `P0` Add webhook tests for replay.
- [ ] `P0` Add webhook tests for duplicate event.
- [ ] `P0` Add webhook tests for out-of-order events.
- [ ] `P1` Add webhook dead-letter handling.
- [ ] `P1` Add webhook retry/backoff.
- [ ] `P1` Add webhook dashboard.

## 9.3 Pricing and product rules

- [ ] `P1` Define free tier.
- [ ] `P1` Define parent plan.
- [ ] `P1` Define school plan.
- [ ] `P1` Define sponsored learner plan.
- [ ] `P1` Define NGO/community plan.
- [ ] `P1` Define trial length.
- [ ] `P1` Define payment failure policy.
- [ ] `P1` Define cancellation policy.
- [ ] `P1` Define refund policy.
- [ ] `P1` Define data-access-after-cancellation policy.
- [ ] `P1` Add invoices.
- [ ] `P1` Add receipts.
- [ ] `P1` Add coupons.
- [ ] `P1` Add sponsorships.
- [ ] `P2` Add pricing admin config.

## 9.4 Billing UX and tests

- [ ] `P1` Add parent billing page.
- [ ] `P1` Add subscription status display.
- [ ] `P1` Add invoice history.
- [ ] `P1` Add cancel subscription flow.
- [ ] `P1` Add payment failure state.
- [ ] `P1` Add billing lifecycle tests.
- [ ] `P1` Add billing audit tests.
- [ ] `P2` Add billing metrics.
- [ ] `P2` Add churn metrics.

---

