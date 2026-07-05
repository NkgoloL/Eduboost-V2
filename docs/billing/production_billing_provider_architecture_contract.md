---
title: Production Billing Provider Architecture Contract
status: active
owner: billing
reviewers: [billing, privacy, release-management]
audience: release-reviewer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-05
review_interval_days: 45
evidence_command: make docs-housekeeping-stage6-check
code_anchors: [docs/billing, scripts/roadmap_reconciliation]
---

# Production Billing Provider Architecture Contract

## Purpose

This contract defines the production billing provider architecture for subscriptions, payments, sponsorships, and monetization.

## Required Architecture Controls

- production billing provider decision is documented in ADR-009
- hosted checkout is required for paid card flows
- application must not store raw card data
- webhook signature verification is required
- webhook idempotency is required
- webhook replay protection is required
- webhook audit logging is required
- provider customer ID is stored separately from learner identity
- provider subscription ID is stored separately from learner identity
- manual sponsorship flow is separated from paid subscription flow

## Required Data Model Concepts

- account
- billing customer
- subscription
- subscription item
- invoice
- receipt
- coupon
- sponsorship
- webhook event
- billing audit event

## Required Provider Boundary

Billing provider integration must isolate provider payload parsing, subscription state transition, audit logging, and user entitlement update.

## Boundary

This contract records repository-side billing architecture readiness. It does not create a live billing provider account, run checkout, process payment, or authorize production billing launch.
