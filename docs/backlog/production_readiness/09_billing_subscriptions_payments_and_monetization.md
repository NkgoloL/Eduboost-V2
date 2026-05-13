# 9. Billing, subscriptions, payments, and monetization

## 9.1 Provider and architecture

- [verify] `P0` Decide production billing provider.
- [verify] `P0` Document billing provider decision in ADR.
- [verify] `P0` Document billing architecture.
- [verify] `P0` Define billing data model.
- [verify] `P0` Define subscription state machine.
- [verify] `P0` Define state `trial`.
- [verify] `P0` Define state `active`.
- [verify] `P0` Define state `past_due`.
- [verify] `P0` Define state `paused`.
- [verify] `P0` Define state `canceled`.
- [verify] `P0` Define state `expired`.
- [verify] `P1` Define sponsorship state if sponsored learner model is in scope.
- [verify] `P1` Define school-plan billing model if schools are in scope.

## 9.2 Webhooks

- [verify] `P0` Implement webhook signature verification.
- [verify] `P0` Implement webhook idempotency.
- [verify] `P0` Implement webhook replay protection.
- [verify] `P0` Implement webhook audit logging.
- [verify] `P0` Add webhook tests for valid signature.
- [verify] `P0` Add webhook tests for invalid signature.
- [verify] `P0` Add webhook tests for replay.
- [verify] `P0` Add webhook tests for duplicate event.
- [verify] `P0` Add webhook tests for out-of-order events.
- [verify] `P1` Add webhook dead-letter handling.
- [verify] `P1` Add webhook retry/backoff.
- [verify] `P1` Add webhook dashboard.

## 9.3 Pricing and product rules

- [verify] `P1` Define free tier.
- [verify] `P1` Define parent plan.
- [verify] `P1` Define school plan.
- [verify] `P1` Define sponsored learner plan.
- [verify] `P1` Define NGO/community plan.
- [verify] `P1` Define trial length.
- [verify] `P1` Define payment failure policy.
- [verify] `P1` Define cancellation policy.
- [verify] `P1` Define refund policy.
- [verify] `P1` Define data-access-after-cancellation policy.
- [verify] `P1` Add invoices.
- [verify] `P1` Add receipts.
- [verify] `P1` Add coupons.
- [verify] `P1` Add sponsorships.
- [verify] `P2` Add pricing admin config.

## 9.4 Billing UX and tests

- [verify] `P1` Add parent billing page.
- [verify] `P1` Add subscription status display.
- [verify] `P1` Add invoice history.
- [verify] `P1` Add cancel subscription flow.
- [verify] `P1` Add payment failure state.
- [verify] `P1` Add billing lifecycle tests.
- [verify] `P1` Add billing audit tests.
- [verify] `P2` Add billing metrics.
- [verify] `P2` Add churn metrics.

---



## 9.6 Repository-side implementation evidence

- [verify] Billing provider decision is documented in `docs/adr/ADR-009-billing-provider.md`.
- [verify] Billing architecture is documented in `docs/billing/production_billing_provider_architecture_contract.md`.
- [verify] Subscription lifecycle is specified in `docs/billing/subscription_state_machine_contract.md`.
- [verify] Webhook signature, replay, idempotency, audit, retry, and dead-letter controls are specified in `docs/billing/webhook_security_idempotency_contract.md`.
- [verify] Pricing, plan, cancellation, refund, invoice, receipt, coupon, sponsorship, and data-access-after-cancellation rules are specified in `docs/billing/pricing_product_rules_contract.md`.
- [verify] Billing UX, audit, lifecycle-test, metrics, and churn evidence are specified in `docs/billing/billing_ux_audit_contract.md`.
- [verify] Deterministic repository contracts live in `app/modules/billing/production_readiness_contracts.py`.
- [verify] Repository validation is provided by `scripts/check_billing_monetization_production_readiness.py`.
- [verify] Domain validation wrapper is provided by `scripts/check_domain_09_billing_monetization_evidence.py`.
- [verify] Unit coverage is provided by `tests/unit/test_billing_monetization_production_readiness.py`.
- [verify] Make target is `make billing-monetization-production-readiness-check`.

### Verification boundary

This implementation provides repository-side billing and monetization readiness evidence. It does not configure a live provider account, publish prices, process payments, create real subscriptions, or authorize production billing launch.
