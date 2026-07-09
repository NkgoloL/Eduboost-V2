# PRD-9.0–9.4 Billing and Commercial Launch Readiness Foundation

This record starts PRD-9 after PRD-8 closure. It defines deterministic, repository-verifiable readiness for billing and commercial launch without enabling live payment processing, public beta, live learner traffic, deployment, release tags, or production release.

## Scope

- PRD-9.0 — PRD-9 billing/commercial authority start.
- PRD-9.1 — Billing provider test-mode and pricing/packaging readiness visibility.
- PRD-9.2 — Checkout/webhook dry-run and subscription entitlement readiness visibility.
- PRD-9.3 — Invoice, tax, refund, dunning, sponsorship, and school procurement readiness visibility.
- PRD-9.4 — Commercial support, reconciliation, terms/privacy, and launch-comms readiness visibility.

## Implementation

- `app.modules.commercial_launch` exposes deterministic readiness helpers.
- `/api/v2/commercial-launch/readiness` exposes the readiness contract.
- The helper imports the existing billing monetisation contracts and confirms they remain valid as readiness evidence only.
- Evidence controls are test-mode only and explicitly block billing launch and live payment processing until a later, explicit authority gate.

## Boundary

This slice does not authorise:

- PRD-10 implementation.
- Billing launch.
- Live payment processing.
- Live learner traffic.
- Public beta.
- Deployment.
- Release tags.
- Production release.
