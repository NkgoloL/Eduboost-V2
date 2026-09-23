---
title: "Threat Model Register"
status: active
owner: security
reviewers: [security, engineering, privacy]
audience: security-reviewer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-09-23"
review_interval_days: 60
evidence_command: "PYTHONPATH=. .venv/bin/python -m pytest tests/test_popia_negative.py tests/smoke/test_v2_smoke.py -q --no-cov"
code_anchors: [docs/security/README.md, app/security]
---

# Threat Model Register

## Required Threat Categories

- spoofing
- tampering
- repudiation
- information disclosure
- denial of service
- elevation of privilege
- prompt injection
- data exfiltration
- supply-chain compromise

## Required Threat Model Fields

- threat ID
- domain
- category
- asset
- abuse case
- control summary
- residual risk
- owner
- review required

## Boundary

This register records threat-model expectations. It does not claim a completed external security review.
