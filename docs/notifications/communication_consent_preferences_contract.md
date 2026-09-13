---
title: "Notifications — Communication Consent and Preferences Contract"
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
# Communication Consent and Preferences Contract

## Purpose

This contract defines consent and preference requirements for notifications and communication.

## Required Consent Controls

- per-channel preference tracking
- per-purpose preference tracking
- marketing unsubscribe requirement
- parent/guardian communication preference support
- learner-safe communication defaults
- quiet-hours preference support
- suppression list support
- lawful security/account/incident communication override
- consent audit event for preference changes
- preference export support

## Learner Safety Defaults

- direct learner SMS is prohibited by default
- direct learner WhatsApp is prohibited by default
- learner billing notifications are prohibited
- learner marketing notifications are prohibited
- learner reminders prefer in-app or push channels
- parent/guardian receives account, billing, and progress communication

## Boundary

This contract records communication consent and preference readiness. It does not replace POPIA consent records or send notifications.
