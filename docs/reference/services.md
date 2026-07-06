---
title: Services
status: active
owner: documentation-governance
reviewers: [documentation-governance, engineering, release-management]
audience: developer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-06
review_interval_days: 90
evidence_command: make docs-housekeeping-stage7-check
code_anchors: [docs/reference, docs/documentation/source_of_truth.yml]
---

# Services

Services encapsulate policy-aware business logic while delegating persistence
to repositories and external integrations to the core runtime.

::: app.services.auth_service
::: app.services.learner_service
::: app.services.lesson_service_v2
::: app.services.study_plan_service_v2
::: app.services.diagnostic_service_v2
::: app.services.gamification_service_v2
::: app.services.parent_report_service_v2
::: app.services.assessment_service_v2
::: app.services.audit_service
::: app.services.consent
::: app.services.consent_expiry_service
::: app.services.consent_renewal_service
::: app.services.caps_validator
::: app.services.quota_service
::: app.services.rlhf_service
::: app.services.pii_sweep
::: app.services.subscription_service
::: app.services.stripe_service
::: app.services.telemetry

