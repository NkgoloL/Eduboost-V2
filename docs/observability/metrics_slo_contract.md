---
title: "Metrics and SLO Contract"
status: "active"
owner: "operations"
reviewers: ["operations", "security", "backend"]
audience: "operator"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-06-24"
review_interval_days: 60
evidence_command: "make docs-housekeeping-stage5-check"
code_anchors: "[app/api_v2.py, docs/observability]"
---

# Metrics and SLO Contract

## Purpose

This contract defines required production metrics, service-level indicators, service-level objectives, and burn-rate alert expectations.

## Required Metric Families

- API request duration
- API error count
- API traffic count
- database query duration
- database connection pool saturation
- LLM provider latency
- LLM provider failure count
- billing webhook failure count
- notification delivery failure count
- notification dead-letter count
- POPIA export failure count

## Required SLOs

- API availability SLO
- API latency SLO
- diagnostic generation success SLO
- POPIA export reliability SLO
- notification delivery reliability SLO

## Required SLO Controls

- SLI metric is defined
- target percentage is defined
- rolling window is defined
- burn-rate alerts are defined
- owner is defined
- runbook is linked

## Boundary

This contract records metrics and SLO readiness. It does not create live dashboards, scrape metrics, or page operators.
