---
title: "Production Notifications Architecture Contract (Production Notifications Architecture Contract)"
status: "active"
owner: "engineering"
reviewers: ['engineering', 'product']
audience: "developer"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-09-13"
review_interval_days: 90
evidence_command: "make docs-housekeeping-check"
code_anchors: "[]"
---
# Production Notifications Architecture Contract

## Purpose

This contract defines the production notification architecture for EduBoost V2 communication flows.

## Required Architecture Controls

- provider-neutral notification adapter
- email channel contract
- SMS channel contract
- WhatsApp channel contract
- push channel contract
- in-app channel contract
- database outbox pattern
- request ID propagation
- idempotency key per notification request
- delivery status tracking
- retry and dead-letter handling
- bounce and complaint ingestion
- suppression list enforcement
- audit logging for lifecycle events
- contact detail redaction for audit metadata

## Required Message Types

- security
- account
- learning reminder
- progress summary
- billing
- support
- marketing
- incident

## Boundary

This contract records repository-side notification architecture readiness. It does not send live messages or configure provider credentials.
