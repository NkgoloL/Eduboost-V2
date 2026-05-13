# 10. Notifications and communication

## 10.1 Provider selection

- [verify] `P0` Choose production email provider.
- [verify] `P0` Write ADR for notification provider.
- [verify] `P0` Document notification architecture.
- [verify] `P0` Document email domain/authentication requirements.
- [verify] `P1` Add provider sandbox for staging.
- [verify] `P1` Add provider failover plan if required.

## 10.2 Transactional templates

- [verify] `P0` Add email verification template.
- [verify] `P0` Add password reset template.
- [verify] `P0` Add consent request template.
- [verify] `P0` Add consent expiry template.
- [verify] `P0` Add diagnostic complete template.
- [verify] `P0` Add weekly parent report template.
- [verify] `P0` Add billing event template.
- [verify] `P0` Add security alert template.
- [verify] `P1` Add erasure request received template.
- [verify] `P1` Add erasure completed template.
- [verify] `P1` Add export ready template.
- [verify] `P1` Add account lockout template.
- [verify] `P1` Add template preview tests.
- [verify] `P1` Add localization plan for templates.

## 10.3 Delivery controls

- [verify] `P0` Add notification audit events.
- [verify] `P0` Add delivery tracking.
- [verify] `P0` Add retry/backoff.
- [verify] `P0` Add bounce handling.
- [verify] `P0` Add complaint handling.
- [verify] `P1` Add notification preferences.
- [verify] `P1` Add quiet hours.
- [verify] `P1` Add rate limits.
- [verify] `P1` Add unsubscribe rules where appropriate.
- [verify] `P1` Add failed delivery dashboard.
- [verify] `P2` Evaluate SMS after privacy impact review.
- [verify] `P2` Evaluate WhatsApp after privacy impact review.

---



## 10.6 Repository-side implementation evidence

- [verify] Communication provider decision is documented in `docs/adr/ADR-010-notifications-communication-provider.md`.
- [verify] Notification architecture is documented in `docs/notifications/production_notifications_architecture_contract.md`.
- [verify] Communication consent and preference controls are documented in `docs/notifications/communication_consent_preferences_contract.md`.
- [verify] Notification template governance is documented in `docs/notifications/notification_template_governance_contract.md`.
- [verify] Delivery reliability, retry, idempotency, and dead-letter controls are documented in `docs/notifications/notification_delivery_reliability_contract.md`.
- [verify] Audit, metrics, observability, and alerting controls are documented in `docs/notifications/notification_audit_observability_contract.md`.
- [verify] Deterministic repository contracts live in `app/modules/notifications/production_readiness_contracts.py`.
- [verify] Repository validation is provided by `scripts/check_notifications_communication_production_readiness.py`.
- [verify] Domain validation wrapper is provided by `scripts/check_domain_10_notifications_communication_evidence.py`.
- [verify] Unit coverage is provided by `tests/unit/test_notifications_communication_production_readiness.py`.
- [verify] Make target is `make notifications-communication-production-readiness-check`.

### Verification boundary

This implementation provides repository-side notifications and communication readiness evidence. It does not configure live messaging providers, send emails, send SMS, send WhatsApp messages, send push notifications, or authorize production communication launch.
