---
title: "Status Communication Contract"
status: "current-evidence"
owner: "operations"
reviewers: "[operations, support, privacy]"
audience: "operator"
source_of_truth: "false"
supersedes: "[]"
superseded_by: null
last_reviewed: "2026-06-24"
review_interval_days: "60"
evidence_command: "make docs-housekeeping-stage5-check"
code_anchors: "[docs/operations_support, docs/runbooks]"
---

# Status Communication Contract

## Purpose

This contract defines customer and internal status communication expectations.

## Required Template Fields

- template ID
- severity
- channels
- audience
- update interval minutes
- privacy review flag
- incident ID
- impact
- current status
- next update

## Required Channels

- status page
- email
- in-app
- admin console
- internal chat

## Required Rules

- sev1 status communication requires status page
- sev2 status communication requires status page
- privacy-related updates require privacy review
- status updates must avoid unnecessary personal information
- next update must be stated for active sev1/sev2 incidents

## Boundary

This contract records status communication readiness. It does not send status updates.
