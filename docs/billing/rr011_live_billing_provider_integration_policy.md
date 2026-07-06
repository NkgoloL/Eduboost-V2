---
title: RR-011 Live Billing Provider Integration Policy
status: active
owner: product
reviewers: [engineering, product, privacy, security, operations]
audience: developer
source_of_truth: true
supersedes: []
superseded_by: null
last_reviewed: 2026-07-05
review_interval_days: 30
evidence_command: make rr011-live-billing-provider-check
code_anchors: [docs/billing, scripts/roadmap_reconciliation]
---

# RR-011 Live Billing Provider Integration Policy

RR-011 records provider-integration evidence for the commercial billing path after beta outcome reporting. It is an integration-readiness and attestation gate, not a launch gate.

Live billing provider integration authority recorded: true

## Required final evidence files

Evidence capture requires final, non-template files under `docs/billing/`:

- `rr011_live_billing_provider_attestation.md`
- `rr011_hosted_checkout_sandbox_validation.md`
- `rr011_webhook_endpoint_validation.md`
- `rr011_pricing_catalogue_approval.md`
- `rr011_billing_launch_boundary.md`

## Required controls

- Hosted checkout is the only approved card-payment flow.
- Raw card data must never be stored by EduBoost.
- Provider secrets must be referenced by secret manager/environment name only, never committed.
- Webhook signature validation, replay protection, idempotency, and audit logging must be recorded.
- Pricing catalogue approval must include parent, school, sponsored learner, and NGO/community plan treatment.
- Billing launch remains separate from provider integration evidence.

## Required transparency

- RR-003 remains valid, but its fallback coverage baseline recorded `0.0` because full test collection had pre-existing blockers.
- RR-006 remains valid, but its evidence PR merged with only the required branch-protection check blocking; other non-required checks were red.
- RR-012 production telemetry dashboard implementation remains outstanding.
- RR-015 external approvals remain outstanding.
- RR-016 operational drills remain outstanding.

## Boundary

Billing launch authorised: false
Live payment processing authorised: false
Production release authorised: false
Deployment authorised: false
Release tag authorised: false
Public beta authorised: false
Runtime KG implementation claimed: false
