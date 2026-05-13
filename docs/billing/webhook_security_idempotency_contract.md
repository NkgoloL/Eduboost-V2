# Webhook Security and Idempotency Contract

## Purpose

This contract defines required controls for payment-provider webhook ingestion.

## Required Webhook Controls

- webhook signature verification
- webhook timestamp replay protection
- webhook idempotency by provider event ID
- webhook audit logging
- duplicate event handling
- out-of-order event handling
- dead-letter handling
- retry and backoff handling
- request ID propagation
- raw provider payload redaction

## Required Test Cases

- valid signature accepted
- invalid signature rejected
- replayed timestamp rejected
- duplicate event is idempotent
- out-of-order event is handled without corrupting subscription state
- dead-letter event records reason
- retry policy has bounded attempts
- audit event includes account ID, provider, request ID, and idempotency key

## Boundary

This contract records repository-side webhook safety readiness. It does not expose a public payment webhook endpoint or accept live provider traffic.
