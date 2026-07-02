---
title: "AI Safety Release Evidence"
status: current-evidence
owner: ai-safety
reviewers: [ai-safety, curriculum, privacy]
audience: safety-reviewer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-06-24
review_interval_days: 60
evidence_command: "make docs-housekeeping-stage5-check"
code_anchors: [app/services, docs/ai]
---

# AI Safety Release Evidence

This index links the LLM gateway, PII redaction/sweeps, prompt contracts, output
schema validation, provider fallback, remediation safety, and refusal fixtures.

Run:

```bash
make ai-safety-release-check
```

Verification gaps: live provider staging checks, educator review of generated
content, and full CAPS approval remain separate release gates.
