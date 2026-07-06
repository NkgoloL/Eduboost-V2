---
title: Pricing and Product Rules Contract
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

# Pricing and Product Rules Contract

## Purpose

This contract defines monetization product rules for free, parent, school, sponsored learner, and NGO/community plans.

## Required Product Rules

- free tier is defined
- parent plan is defined
- school plan is defined
- sponsored learner plan is defined
- NGO/community plan is defined
- trial length is defined
- payment failure policy is defined
- cancellation policy is defined
- refund policy is defined
- data-access-after-cancellation policy is defined
- invoices are required
- receipts are required
- coupons are supported
- sponsorships are supported
- pricing admin config is required before launch

## Required Learner Protection Rules

- cancellation must preserve lawful data export access for a defined period
- payment failure must not delete learner records
- sponsorship status must not expose payment details to learners
- billing records must avoid unnecessary learner personal information

## Boundary

This contract records product and monetization policy readiness. It does not publish prices, bill users, or authorize production billing launch.
