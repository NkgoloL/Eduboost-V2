# Frontend Auth Consent Denial Contract

## Purpose

The frontend must display safe, actionable states when backend object
authorization or active consent checks deny learner-scoped or parent-scoped
requests.

## Required Denial States

- unauthenticated session
- unauthorized learner access
- unauthorized parent access
- inactive or expired consent
- revoked consent
- missing learner link
- data-rights request unavailable
- retryable network failure
- non-retryable server failure

## Required UX Rules

- denial states must not expose another learner's data
- denial states must not reveal internal policy details
- denial states must show safe next action
- consent denial must link to consent or parent support flow
- authorization denial must not offer bypass instructions
- retryable failures must be visually distinct from hard denials
- learner-facing copy must remain age-appropriate

## Required Frontend Evidence

- route or component handling 401/403
- route or component handling consent required/expired
- API client branch for error envelope parsing
- visible safe next action for denied learner flow
- visible safe next action for denied parent flow

## Command

```bash
make frontend-auth-consent-denial-check
```
