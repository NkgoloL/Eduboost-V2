---
title: "Frontend Spike Report Template"
status: "current-evidence"
owner: "frontend"
reviewers: ["frontend", "product", "privacy"]
audience: "developer"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-06-24"
review_interval_days: 60
evidence_command: "make docs-housekeeping-stage5-check"
code_anchors: "[app/frontend, docs/frontend/README.md]"
---

# Frontend Spike Report Template

| Field | Notes |
| --- | --- |
| Spike ID | e.g., `FE-SPIKE-003` |
| Focus | Short description of the question being answered |
| RC Gate | RC1..RC5 the spike informs |
| Owner | Engineer driving the investigation |
| Status | Draft / In Review / Accepted / Rejected |
| Verdict | Proceed / Modify / Defer / Abandon |

## Summary

Explain the hypothesis, constraints, and the user impact being validated.

## Experiments

Number each experiment with commands, environment variables, and outputs. Include Docker + ACA checks when relevant.

## Findings

- Bullet list of key findings.
- Reference bundle metrics, performance numbers, or compliance inputs.

## Risks

Detail outstanding risks, open questions, or dependencies on other spikes/ADRs.

## Recommendation

Provide the final verdict plus guardrails or follow-up actions required before implementation starts.

## Evidence

Link to logs, screenshots, or scripts stored alongside the spike report.
