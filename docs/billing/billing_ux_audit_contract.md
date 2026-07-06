---
title: Billing UX and Audit Contract
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

# Billing UX and Audit Contract

## Purpose

This contract defines minimum billing UX and audit expectations for parent, school, and sponsorship billing flows.

## Required UX Surfaces

- parent billing page
- subscription status display
- invoice history
- receipt history
- cancel subscription flow
- payment failure state
- coupon display where applicable
- sponsorship display where applicable
- data-access-after-cancellation notice

## Required Audit Evidence

- billing lifecycle tests
- billing audit tests
- webhook audit event contract
- subscription transition audit contract
- billing metrics evidence
- churn metrics evidence
- payment failure metric evidence
- cancellation reason evidence

## Boundary

This contract records billing UX and audit readiness. It does not implement live checkout, collect payment details, or authorize production billing launch.
