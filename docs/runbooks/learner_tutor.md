---
title: "Learner Tutor Operations Runbook"
status: "active-runbook"
owner: "operations"
reviewers: ["operations", "engineering", "release-management"]
audience: "operator"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-06-24"
review_interval_days: 60
evidence_command: "make docs-housekeeping-stage5-check"
code_anchors: "[docs/runbooks, docs/operations]"
---

# Learner Tutor Operations Runbook

## Safety-first behaviour

- Provider output is not streamed to the learner until the complete response passes validation.
- `fallback=true` means the learner received a local, non-deceptive safe message.
- High-risk input/output creates an open `tutor_escalations` record.
- A high-severity escalation moves the session to `escalated`; the learner must start a new session after educator review.

## Investigation

1. Locate the session by `session_id`.
2. Review redacted messages only; raw learner text is not retained.
3. Confirm `reason_code`, severity, provider, model, and request ID.
4. Do not copy content into general logs or tickets.
5. Escalate self-harm or child-safety indicators through the approved safeguarding process.

## Provider outage

The learner sees: “The tutor is unavailable right now…” The lesson remains usable. Do not describe the fallback as an AI-generated answer.

## Budget exhaustion

The tutor returns a safe local fallback. Check per-user and tenant counters before raising limits. Never bypass the budget in production.

## Rollback

Disable or remove the tutor router while preserving lesson delivery. The migration can be rolled back only after confirming no evidence or open escalation must be retained. Prefer a forward fix.
