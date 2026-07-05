---
title: RR-011 Webhook Endpoint Validation Template
status: template
owner: engineering
reviewers: [engineering, product, privacy, security, operations]
audience: developer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-03
review_interval_days: 30
evidence_command: make rr011-live-billing-provider-check
code_anchors: [app/modules/billing/production_readiness_contracts.py, app/api_v2_routers/billing.py]
---
# RR-011 Webhook Endpoint Validation Template

Webhook endpoint configured: true
Webhook signature validation recorded: true
Webhook replay protection recorded: true
Webhook idempotency validation recorded: true
Webhook audit logging recorded: true
Duplicate provider event handling recorded: true
Out-of-order provider event handling recorded: true
Live webhook traffic authorised: false
