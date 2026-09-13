---
title: "Reference — Core Runtime"
status: "active"
owner: "engineering"
reviewers: ['engineering', 'architecture']
audience: "developer"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-09-13"
review_interval_days: 90
evidence_command: "make docs-housekeeping-check"
code_anchors: "[]"
---
# Core Runtime

These modules define the shared runtime kernel for the V2 modular monolith.

## Configuration
::: app.core.config

## Security and RBAC
::: app.core.security
::: app.core.rbac
::: app.core.refresh_tokens
::: app.core.token_revocation

## Database and Dependencies
::: app.core.database
::: app.core.dependencies
::: app.core.base

## Observability and Operations
::: app.core.logging
::: app.core.middleware
::: app.core.metrics
::: app.core.analytics
::: app.core.health
::: app.core.secret_rotation

## Governance and Jobs
::: app.core.audit
::: app.core.jobs
::: app.core.judiciary
::: app.core.rate_limit
::: app.core.rate_limiter

## External Integrations
::: app.core.redis
::: app.core.llm_gateway
::: app.core.stripe_client

