---
title: "Recovery Objectives Contract"
status: "active"
owner: "operations"
reviewers: "[operations, security, privacy]"
audience: "operator"
source_of_truth: "false"
supersedes: "[]"
superseded_by: null
last_reviewed: "2026-06-24"
review_interval_days: "60"
evidence_command: "make docs-housekeeping-stage5-check"
code_anchors: "[docs/disaster_recovery, scripts]"
---

# Recovery Objectives Contract

## Purpose

This contract defines RPO and RTO objectives for critical EduBoost V2 services.

## Required Recovery Objective Fields

- service
- recovery tier
- RPO minutes
- RTO minutes
- owner
- escalation route

## Required Objectives

- API service has critical RPO and RTO
- database service has critical RPO and RTO
- object storage service has important RPO and RTO
- audit logs have critical RPO and RTO
- critical services require RPO <= 60 minutes
- critical services require RTO <= 240 minutes
- escalation route is required
- owner is required

## Boundary

This contract records recovery-objective readiness. It does not guarantee live infrastructure recovery performance.
