---
title: Subscription State Machine Contract
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

# Subscription State Machine Contract

## Purpose

This contract defines the canonical subscription state machine for EduBoost V2 monetization.

## Required States

- trial
- active
- past_due
- paused
- canceled
- expired

## Required Transition Rules

- trial can transition to active, past_due, canceled, or expired
- active can transition to past_due, paused, canceled, or expired
- past_due can transition to active, canceled, or expired
- paused can transition to active, canceled, or expired
- canceled is terminal
- expired is terminal
- state transitions must be audit logged
- entitlement changes must be derived from subscription state

## Required Sponsored/School Plan Rules

- sponsored learner plan must reference a sponsor account
- school plan must reference a school account
- manual sponsorship must not bypass audit logging
- sponsored learner access must not expose sponsor payment details

## Boundary

This contract records subscription-state readiness. It does not execute billing transitions against a live provider.
