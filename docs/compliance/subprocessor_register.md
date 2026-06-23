---
title: "Subprocessor register"
status: active
owner: privacy
reviewers: [privacy, security, release-management]
audience: compliance-reviewer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-06-23
review_interval_days: 60
evidence_command: "make docs-housekeeping-stage4-check"
code_anchors: [docs/compliance/README.md]
---

# Subprocessor register

| Subprocessor | Purpose | Data exposure | Status |
|---|---|---|---|
| PostgreSQL hosting provider | Primary application database | Guardian/learner operational data | Required production processor |
| Redis hosting provider | Cache, rate limits, token/session revocation | Session metadata, no learner content | Required production processor |
| SendGrid or configured email provider | Transactional email | Guardian email address, template metadata | Pending production selection |
| Stripe | Billing/subscriptions | Guardian billing/customer metadata | Pending production selection |
| PostHog | Product analytics | Pseudonymous events only | Optional; no raw learner PII |
| Anthropic/Groq/local HF provider | LLM lesson generation | Pseudonymous educational context only | Provider depends on deployment config |
| Azure Blob/Object storage | Backups/assets/exports if enabled | Encrypted objects | Pending production selection |

Before production launch, each active subprocessor must have: contract/DPA status, region, retention behavior, breach-notification terms, and offboarding procedure recorded.
