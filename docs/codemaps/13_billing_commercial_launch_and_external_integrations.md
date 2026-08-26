# EduBoost V2 Billing, Commercial Launch, and External Integrations

Maps product plans, subscriptions, Stripe checkout and webhooks, idempotency, entitlements, email notifications, and commercial launch readiness.

## Scope and ownership

This codemap is the primary architecture owner for:
- `app/api_v2_routers/billing.py`
- `app/services/stripe_service.py`
- `app/services/subscription_service.py`
- `app/repositories/stripe_event_repository.py`
- `app/services/email_service.py`
- `app/modules/commercial_launch`

It describes current implementation paths in repository-relative form. Related cross-cutting behaviour may be referenced from other codemaps, but every maintained source file has one primary owner in `codemap_coverage_manifest.json`.

## Architectural position

This area participates in the wider EduBoost request, data, evidence, and release architecture. Read it together with `00_application_bootstrap_and_request_lifecycle.md`, `17_testing_ci_coverage_security_and_quality_gates.md`, and `18_production_readiness_release_evidence_and_live_traffic.md` when changing runtime or release-critical behaviour.

## Trace ID: 1
**Title:** Plan, checkout, subscription, and entitlement flow

**Description:** Follows an authorized purchaser from plan selection through Stripe checkout and local subscription projection.

**Motivation:**
Commercial state must not become a hidden authorization system; payment facts and product entitlements need explicit, reconciled boundaries.

**Details:**

**Execution path**

1. Load active product and plan configuration.
2. Authorize purchaser and learner relationship.
3. Create an idempotent checkout session.
4. Redirect to the external payment provider.
5. Receive authoritative provider state.
6. Project subscription and entitlement state locally.

**State and ownership boundaries**

Provider customer/subscription IDs, local subscription records, and entitlements are linked but not interchangeable.

**Failure, privacy, and control points**

Prices are server-authoritative, duplicate checkout is controlled, no card data is stored, and entitlement changes require verified provider state.

**Verification signals**

Run billing route, Stripe service, subscription, entitlement, and commercial readiness tests.

**Trace text diagram:**
```text
1. Load active product and plan configuration [1a]
   |
   v
2. Authorize purchaser and learner relationship [1b]
   |
   v
3. Create an idempotent checkout session [1c]
   |
   v
4. Redirect to the external payment provider [1d]
   |
   v
5. Receive authoritative provider state [1d]
   |
   v
6. Project subscription and entitlement state locally [1d]
```

**Location ID: 1a**
- **Title:** Billing routes
- **Description:** Checkout and subscription API.
- **Path:LineNumber:** app/api_v2_routers/billing.py:18

**Location ID: 1b**
- **Title:** Stripe service
- **Description:** Provider checkout and webhook operations.
- **Path:LineNumber:** app/services/stripe_service.py:10

**Location ID: 1c**
- **Title:** Subscription service
- **Description:** Local subscription and entitlement projection.
- **Path:LineNumber:** app/services/subscription_service.py:10

**Location ID: 1d**
- **Title:** Stripe client
- **Description:** Configured provider client boundary.
- **Path:LineNumber:** app/core/stripe_client.py:24

### AI Guide: Plan, checkout, subscription, and entitlement flow

**Motivation:**
Commercial state must not become a hidden authorization system; payment facts and product entitlements need explicit, reconciled boundaries.

**Details:**

**Reasoning through the execution path.** Start at [1a] and follow the ordered state transition rather than jumping directly to a downstream repository or generated artefact. The trace is designed to show which layer owns transport, orchestration, persistence, and evidence. [1a] anchors billing routes. [1b] anchors stripe service. [1c] anchors subscription service. [1d] anchors stripe client.

**Safe change boundary.** Provider customer/subscription IDs, local subscription records, and entitlements are linked but not interchangeable. A change that moves responsibility across these boundaries should update the owning codemap, tests, and any affected ADR or release verifier in the same change.

**Controls to preserve.** Prices are server-authoritative, duplicate checkout is controlled, no card data is stored, and entitlement changes require verified provider state.

**How to verify the change.** Run billing route, Stripe service, subscription, entitlement, and commercial readiness tests. Use the cited locations as navigation anchors, then inspect call sites and tests before modifying behaviour.

## Trace ID: 2
**Title:** Webhook verification, idempotency, and reconciliation

**Description:** Maps inbound Stripe events through signature verification, event de-duplication, domain updates, and audit evidence.

**Motivation:**
Webhooks are untrusted network input even when they come from a payment provider.

**Details:**

**Execution path**

1. Read the raw request body.
2. Verify provider signature and timestamp tolerance.
3. Store or detect the provider event ID.
4. Dispatch supported event types.
5. Update local subscription state transactionally.
6. Record outcome and make retries idempotent.

**State and ownership boundaries**

Provider event log is immutable ingress evidence; local subscription state is a projection that can be reconciled.

**Failure, privacy, and control points**

Unsigned, stale, duplicated, or unsupported events do not mutate entitlements; processing failures remain retryable.

**Verification signals**

Run signature, duplicate event, ordering, reconciliation, and live-provider integration tests.

**Trace text diagram:**
```text
1. Read the raw request body [2a]
   |
   v
2. Verify provider signature and timestamp tolerance [2b]
   |
   v
3. Store or detect the provider event ID [2c]
   |
   v
4. Dispatch supported event types [2d]
   |
   v
5. Update local subscription state transactionally [2d]
   |
   v
6. Record outcome and make retries idempotent [2d]
```

**Location ID: 2a**
- **Title:** Stripe event repository
- **Description:** Webhook idempotency authority.
- **Path:LineNumber:** app/repositories/stripe_event_repository.py:11

**Location ID: 2b**
- **Title:** Webhook handler
- **Description:** Provider event validation and dispatch.
- **Path:LineNumber:** app/services/stripe_service.py:1

**Location ID: 2c**
- **Title:** Subscription persistence
- **Description:** Local commercial state.
- **Path:LineNumber:** app/models/auth_extensions.py:42

**Location ID: 2d**
- **Title:** Billing integration workflow
- **Description:** Hosted provider readiness evidence.
- **Path:LineNumber:** .github/workflows/rr011-live-billing-provider-integration.yml:1

### AI Guide: Webhook verification, idempotency, and reconciliation

**Motivation:**
Webhooks are untrusted network input even when they come from a payment provider.

**Details:**

**Reasoning through the execution path.** Start at [2a] and follow the ordered state transition rather than jumping directly to a downstream repository or generated artefact. The trace is designed to show which layer owns transport, orchestration, persistence, and evidence. [2a] anchors stripe event repository. [2b] anchors webhook handler. [2c] anchors subscription persistence. [2d] anchors billing integration workflow.

**Safe change boundary.** Provider event log is immutable ingress evidence; local subscription state is a projection that can be reconciled. A change that moves responsibility across these boundaries should update the owning codemap, tests, and any affected ADR or release verifier in the same change.

**Controls to preserve.** Unsigned, stale, duplicated, or unsupported events do not mutate entitlements; processing failures remain retryable.

**How to verify the change.** Run signature, duplicate event, ordering, reconciliation, and live-provider integration tests. Use the cited locations as navigation anchors, then inspect call sites and tests before modifying behaviour.

## Trace ID: 3
**Title:** Email notifications and commercial launch readiness

**Description:** Shows domain events becoming outbound notifications and commercial controls feeding launch decisions.

**Motivation:**
Payments, consent, account recovery, and parent journeys depend on reliable but privacy-safe communications.

**Details:**

**Execution path**

1. Create a notification intent from an accepted domain event.
2. Resolve recipient and consent-compatible template.
3. Render minimal transactional content.
4. Send through the configured email provider.
5. Record delivery or failure metadata.
6. Feed operational, billing, and support evidence into launch readiness.

**State and ownership boundaries**

Notification intent and delivery evidence are retained separately from provider internals and sensitive domain payloads.

**Failure, privacy, and control points**

Templates avoid unnecessary learner data, retries are bounded, unsubscribe rules are respected where applicable, and send failures do not corrupt domain transactions.

**Verification signals**

Run email service, notification readiness, billing readiness, and commercial launch handoff tests.

**Trace text diagram:**
```text
1. Create a notification intent from an accepted domain event [3a]
   |
   v
2. Resolve recipient and consent-compatible template [3b]
   |
   v
3. Render minimal transactional content [3c]
   |
   v
4. Send through the configured email provider [3d]
   |
   v
5. Record delivery or failure metadata [3d]
   |
   v
6. Feed operational, billing, and support evidence into launch readiness [3d]
```

**Location ID: 3a**
- **Title:** Email service
- **Description:** Outbound communication adapter.
- **Path:LineNumber:** app/services/email_service.py:39

**Location ID: 3b**
- **Title:** Notification readiness
- **Description:** Operational notification contracts.
- **Path:LineNumber:** app/modules/notifications/production_readiness_contracts.py:18

**Location ID: 3c**
- **Title:** Commercial readiness
- **Description:** Launch decision aggregation.
- **Path:LineNumber:** app/modules/commercial_launch/readiness.py:51

**Location ID: 3d**
- **Title:** Commercial launch routes
- **Description:** Read-only launch control surface.
- **Path:LineNumber:** app/api_v2_routers/commercial_launch.py:15

### AI Guide: Email notifications and commercial launch readiness

**Motivation:**
Payments, consent, account recovery, and parent journeys depend on reliable but privacy-safe communications.

**Details:**

**Reasoning through the execution path.** Start at [3a] and follow the ordered state transition rather than jumping directly to a downstream repository or generated artefact. The trace is designed to show which layer owns transport, orchestration, persistence, and evidence. [3a] anchors email service. [3b] anchors notification readiness. [3c] anchors commercial readiness. [3d] anchors commercial launch routes.

**Safe change boundary.** Notification intent and delivery evidence are retained separately from provider internals and sensitive domain payloads. A change that moves responsibility across these boundaries should update the owning codemap, tests, and any affected ADR or release verifier in the same change.

**Controls to preserve.** Templates avoid unnecessary learner data, retries are bounded, unsubscribe rules are respected where applicable, and send failures do not corrupt domain transactions.

**How to verify the change.** Run email service, notification readiness, billing readiness, and commercial launch handoff tests. Use the cited locations as navigation anchors, then inspect call sites and tests before modifying behaviour.

## Change checklist

- Update this codemap when an entry point, major dependency, persistence owner, or control flow changes.
- Keep all `Path:LineNumber` references repository-relative and line-valid.
- Update `codemap_coverage_manifest.json` when files move between architecture owners.
- Run `python scripts/maintenance/verify_codemaps.py --repo-root .` before merging.
